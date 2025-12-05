"""
Entity Extractor - Automatically extract system entities from documents
"""
import re
from typing import List, Dict, Set
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def extract_entities_with_ai(text: str, max_length: int = 4000) -> List[Dict]:
    """
    Use AI to extract important entities from text.
    
    Args:
        text: Document text to analyze
        max_length: Maximum text length to send to AI
        
    Returns:
        List of entity dictionaries with key, name, type, and description
    """
    # Truncate text if too long
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    system_prompt = """You are an entity extraction expert. Analyze the provided documentation and identify important entities (nouns, concepts, features, objects, actions).

Extract entities that are:
- Key features or functionalities
- Important objects or items users interact with
- Common actions or operations
- Domain-specific terms

For each entity, provide:
1. entity_key: lowercase, single word or hyphenated (e.g., "user", "workflow", "purchase-request")
2. entity_name: Proper formatted name (e.g., "User", "Workflow", "Purchase Request")
3. entity_type: One of: reference, transactional, feature, configuration, action
4. description: Brief description (one sentence)

Output format (JSON array):
[
  {"entity_key": "workflow", "entity_name": "Workflow", "entity_type": "feature", "description": "Process flow definition"},
  {"entity_key": "approval", "entity_name": "Approval", "entity_type": "action", "description": "Authorization or approval action"}
]

Extract 5-15 most important entities. Output ONLY valid JSON array, no other text."""

    user_prompt = f"""Documentation Text:
{text}

Extract important entities from this text."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse JSON
        import json
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = re.sub(r'```json\s*|\s*```', '', content)
        
        entities = json.loads(content)
        
        # Validate and clean entities
        valid_entities = []
        for entity in entities:
            if isinstance(entity, dict) and 'entity_key' in entity and 'entity_name' in entity:
                # Ensure entity_key is lowercase and valid
                entity['entity_key'] = entity.get('entity_key', '').lower().strip()
                entity['entity_key'] = re.sub(r'[^a-z0-9\-]', '', entity['entity_key'])
                
                if entity['entity_key']:
                    valid_entities.append({
                        'entity_key': entity['entity_key'],
                        'entity_name': entity.get('entity_name', entity['entity_key'].title()),
                        'entity_type': entity.get('entity_type', 'reference'),
                        'description': entity.get('description', '')[:255]  # Limit description length
                    })
        
        return valid_entities
        
    except Exception as e:
        print(f"⚠️  AI entity extraction failed: {e}", flush=True)
        return []


def extract_entities_with_patterns(text: str) -> List[Dict]:
    """
    Extract entities using pattern matching (fallback method).
    
    Args:
        text: Document text to analyze
        
    Returns:
        List of entity dictionaries
    """
    entities = []
    text_lower = text.lower()
    
    # Common patterns to detect
    patterns = {
        # Action patterns
        r'\b(create|add|edit|update|delete|remove|view|display|configure|setup|approve|reject)\s+(\w+)': 'action',
        
        # Feature patterns
        r'\b(\w+)\s+(feature|functionality|module|system|tool)': 'feature',
        
        # Object patterns (capitalized words that appear frequently)
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b': 'reference',
    }
    
    detected = set()
    
    for pattern, entity_type in patterns.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            # Get the relevant group
            if match.lastindex >= 2:
                entity_text = match.group(2)
            else:
                entity_text = match.group(1)
            
            entity_key = entity_text.lower().strip()
            entity_key = re.sub(r'\s+', '-', entity_key)
            entity_key = re.sub(r'[^a-z0-9\-]', '', entity_key)
            
            if entity_key and len(entity_key) > 2 and entity_key not in detected:
                detected.add(entity_key)
                entities.append({
                    'entity_key': entity_key,
                    'entity_name': entity_text.title(),
                    'entity_type': entity_type,
                    'description': f'{entity_text.title()} entity'
                })
    
    return entities[:20]  # Limit to 20 entities


def extract_and_save_entities(text: str, tenant_id: str = "default", use_ai: bool = True) -> int:
    """
    Extract entities from text and save them to database.
    
    Args:
        text: Document text to analyze
        tenant_id: Tenant identifier
        use_ai: Whether to use AI extraction (True) or pattern matching (False)
        
    Returns:
        Number of new entities added
    """
    from database.db_manager import db_manager
    
    # Extract entities
    if use_ai:
        print("   🔍 Extracting entities using AI...", flush=True)
        entities = extract_entities_with_ai(text)
    else:
        print("   🔍 Extracting entities using patterns...", flush=True)
        entities = extract_entities_with_patterns(text)
    
    if not entities:
        print("   ℹ️  No entities extracted", flush=True)
        return 0
    
    # Get existing entities to avoid duplicates
    existing_entities = db_manager.get_system_entities(active_only=False)
    existing_keys = set(existing_entities.keys())
    
    # Add new entities to database
    new_count = 0
    for entity in entities:
        entity_key = entity['entity_key']
        
        if entity_key not in existing_keys:
            success = db_manager.add_system_entity(
                entity_key=entity_key,
                entity_name=entity['entity_name'],
                entity_type=entity.get('entity_type', 'reference'),
                description=entity.get('description', ''),
                priority=1
            )
            
            if success:
                new_count += 1
                print(f"   ✅ Added entity: {entity['entity_name']} ({entity_key})", flush=True)
    
    if new_count > 0:
        print(f"   🎉 Added {new_count} new entities to database", flush=True)
    else:
        print(f"   ℹ️  All {len(entities)} entities already exist", flush=True)
    
    return new_count


def bulk_extract_from_chunks(chunks: List[str], tenant_id: str = "default", use_ai: bool = True) -> int:
    """
    Extract entities from multiple document chunks.
    
    Args:
        chunks: List of text chunks
        tenant_id: Tenant identifier
        use_ai: Whether to use AI extraction
        
    Returns:
        Total number of new entities added
    """
    # Combine first few chunks for analysis (don't need all chunks)
    sample_size = min(5, len(chunks))
    combined_text = "\n\n".join(chunks[:sample_size])
    
    # Limit text size
    max_text_length = 8000
    if len(combined_text) > max_text_length:
        combined_text = combined_text[:max_text_length]
    
    return extract_and_save_entities(combined_text, tenant_id, use_ai)


def extract_from_file_content(content: str, filename: str, tenant_id: str = "default") -> int:
    """
    Extract entities from a full document.
    
    Args:
        content: Document content
        filename: Name of the file
        tenant_id: Tenant identifier
        
    Returns:
        Number of new entities added
    """
    print(f"\n🔎 Extracting entities from: {filename}", flush=True)
    
    # Use AI for better extraction quality
    return extract_and_save_entities(content, tenant_id, use_ai=True)

