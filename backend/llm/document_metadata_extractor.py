"""
Document Metadata Extractor - Extract structured data from documents to populate database
Automatically extracts: entities, query patterns, keywords, FAQs, and clarification patterns
"""
import re
import json
from typing import List, Dict, Tuple
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def extract_all_metadata(text: str, filename: str, tenant_id: str = "default") -> Dict:
    """
    Extract all types of metadata from document text.
    
    Args:
        text: Document content
        filename: Name of the source file
        tenant_id: Tenant identifier
        
    Returns:
        Dictionary with counts of items added to each table
    """
    print(f"\n{'='*60}")
    print(f"🔍 Extracting Metadata from: {filename}")
    print(f"{'='*60}")
    
    results = {
        'entities': 0,
        'query_patterns': 0,
        'keywords': 0,
        'faqs': 0,
        'synonyms': 0,
        'suggestions': 0,
        'category': None
    }
    
    # Truncate text if too long (keep first part which usually has key info)
    max_text_length = 6000
    if len(text) > max_text_length:
        text = text[:max_text_length] + "\n... (content truncated)"
    
    # Extract document category
    try:
        category = detect_document_category(text, filename)
        results['category'] = category
        if category:
            print(f"📂 Category: {category}")
    except Exception as e:
        print(f"⚠️  Category detection failed: {e}")
    
    # Extract entities
    try:
        entities_count = extract_entities(text, tenant_id)
        results['entities'] = entities_count
        print(f"✅ Entities: {entities_count} added")
    except Exception as e:
        print(f"⚠️  Entity extraction failed: {e}")
    
    # Extract query patterns
    try:
        patterns_count = extract_query_patterns(text, tenant_id)
        results['query_patterns'] = patterns_count
        print(f"✅ Query Patterns: {patterns_count} added")
    except Exception as e:
        print(f"⚠️  Query pattern extraction failed: {e}")
    
    # Extract keywords
    try:
        keywords_count = extract_keywords(text, tenant_id)
        results['keywords'] = keywords_count
        print(f"✅ Keywords: {keywords_count} added")
    except Exception as e:
        print(f"⚠️  Keyword extraction failed: {e}")
    
    # Extract FAQs
    try:
        faqs_count = extract_faqs(text, tenant_id)
        results['faqs'] = faqs_count
        print(f"✅ FAQs: {faqs_count} added")
    except Exception as e:
        print(f"⚠️  FAQ extraction failed: {e}")
    
    # Extract synonyms
    try:
        synonyms_count = extract_synonyms(text, tenant_id)
        results['synonyms'] = synonyms_count
        print(f"✅ Synonyms: {synonyms_count} added")
    except Exception as e:
        print(f"⚠️  Synonym extraction failed: {e}")
    
    # Extract auto-suggestions
    try:
        suggestions_count = extract_suggestions(text, tenant_id)
        results['suggestions'] = suggestions_count
        print(f"✅ Suggestions: {suggestions_count} added")
    except Exception as e:
        print(f"⚠️  Suggestion extraction failed: {e}")
    
    # Save document metadata
    try:
        save_document_metadata(filename, text, category, tenant_id)
        print(f"✅ Document metadata saved")
    except Exception as e:
        print(f"⚠️  Document metadata save failed: {e}")
    
    print(f"{'='*60}\n")
    
    return results


def extract_entities(text: str, tenant_id: str) -> int:
    """Extract and save system entities."""
    from llm.entity_extractor import extract_and_save_entities
    return extract_and_save_entities(text, tenant_id, use_ai=True)


def extract_query_patterns(text: str, tenant_id: str) -> int:
    """
    Extract common query patterns and keywords from documentation.
    Populates query_patterns table.
    """
    from database.db_manager import db_manager
    
    system_prompt = """You are a query pattern expert. Analyze the documentation and identify common question patterns users might ask.

Extract:
1. query_type: Type of query (e.g., "how-to", "troubleshooting", "definition", "list", "configuration")
2. keywords: Comma-separated keywords that trigger this pattern (e.g., "create, add, new" for how-to)

Generate 5-10 query patterns based on the documentation content.

Output format (JSON array):
[
  {"query_type": "how-to-create", "keywords": "create, add, new, make"},
  {"query_type": "troubleshooting-error", "keywords": "error, issue, problem, not working, failed"}
]

Output ONLY valid JSON array, no other text."""

    user_prompt = f"""Documentation Text:
{text}

Extract query patterns from this documentation."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean and parse JSON
        if content.startswith("```"):
            content = re.sub(r'```json\s*|\s*```', '', content)
        
        patterns = json.loads(content)
        
        # Save to database
        new_count = 0
        for pattern in patterns:
            if isinstance(pattern, dict) and 'query_type' in pattern and 'keywords' in pattern:
                try:
                    # Check if pattern exists
                    with db_manager.get_connection() as conn:
                        cursor = conn.execute(
                            "SELECT COUNT(*) as count FROM query_patterns WHERE query_type = %s",
                            (pattern['query_type'],)
                        )
                        result = cursor.fetchone()
                        
                        if result and result[0] == 0:
                            # Insert new pattern
                            conn.execute(
                                """INSERT INTO query_patterns 
                                   (query_type, keyword, tenant_id) 
                                   VALUES (%s, %s, %s)""",
                                (pattern['query_type'], pattern['keywords'], tenant_id)
                            )
                            conn.commit()
                            new_count += 1
                except Exception as e:
                    print(f"   ⚠️  Error saving query pattern: {e}")
        
        return new_count
        
    except Exception as e:
        print(f"   ⚠️  Query pattern extraction error: {e}")
        return 0


def extract_keywords(text: str, tenant_id: str) -> int:
    """
    Extract important keywords and their context from documentation.
    Populates query_keywords table.
    """
    from database.db_manager import db_manager
    
    system_prompt = """You are a keyword extraction expert. Analyze the documentation and identify the most important keywords/terms.

For each keyword provide:
1. keyword: The actual keyword/term (lowercase)
2. query_type: Category (e.g., "feature", "action", "object", "process", "configuration")
3. context: Brief context or definition (max 100 chars)

Extract 10-15 most important keywords.

Output format (JSON array):
[
  {"keyword": "workflow", "query_type": "feature", "context": "Process automation and task sequencing"},
  {"keyword": "approval", "query_type": "action", "context": "Authorization or sign-off process"}
]

Output ONLY valid JSON array, no other text."""

    user_prompt = f"""Documentation Text:
{text}

Extract important keywords from this documentation."""

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
        
        # Clean and parse JSON
        if content.startswith("```"):
            content = re.sub(r'```json\s*|\s*```', '', content)
        
        keywords = json.loads(content)
        
        # Save to database
        new_count = 0
        for kw in keywords:
            if isinstance(kw, dict) and 'keyword' in kw:
                try:
                    keyword_lower = kw['keyword'].lower().strip()
                    
                    # Check if keyword exists
                    with db_manager.get_connection() as conn:
                        cursor = conn.execute(
                            "SELECT COUNT(*) as count FROM query_keywords WHERE keyword = %s",
                            (keyword_lower,)
                        )
                        result = cursor.fetchone()
                        
                        if result and result[0] == 0:
                            # Insert new keyword
                            conn.execute(
                                """INSERT INTO query_keywords 
                                   (keyword, query_type, context, tenant_id, priority) 
                                   VALUES (%s, %s, %s, %s, %s)""",
                                (keyword_lower, 
                                 kw.get('query_type', 'general'),
                                 kw.get('context', '')[:255],
                                 tenant_id,
                                 3)  # Default priority
                            )
                            conn.commit()
                            new_count += 1
                except Exception as e:
                    print(f"   ⚠️  Error saving keyword: {e}")
        
        return new_count
        
    except Exception as e:
        print(f"   ⚠️  Keyword extraction error: {e}")
        return 0


def extract_faqs(text: str, tenant_id: str) -> int:
    """
    Extract potential FAQs from documentation.
    Populates frequently_asked_questions table.
    """
    from database.db_manager import db_manager
    
    # Look for FAQ sections first
    faq_pattern = r'(?:FAQ|Frequently Asked Questions|Common Questions|Q&A)(.*?)(?:\n#{1,2}\s|\Z)'
    faq_sections = re.findall(faq_pattern, text, re.DOTALL | re.IGNORECASE)
    
    if not faq_sections:
        # No explicit FAQ section, use AI to generate potential FAQs
        return extract_faqs_with_ai(text, tenant_id)
    
    # Parse FAQ section
    new_count = 0
    for section in faq_sections:
        # Extract Q&A pairs
        qa_pairs = re.findall(r'Q[:\s]+(.*?)\s*A[:\s]+(.*?)(?=Q[:\s]|\Z)', section, re.DOTALL)
        
        for question, answer in qa_pairs:
            question = question.strip()[:500]
            answer = answer.strip()[:1000]
            
            if len(question) > 10 and len(answer) > 10:
                try:
                    with db_manager.get_connection() as conn:
                        # Check if similar question exists
                        cursor = conn.execute(
                            "SELECT COUNT(*) as count FROM frequently_asked_questions WHERE question = %s",
                            (question,)
                        )
                        result = cursor.fetchone()
                        
                        if result and result[0] == 0:
                            conn.execute(
                                """INSERT INTO frequently_asked_questions 
                                   (question, answer, tenant_id, ask_count, category) 
                                   VALUES (%s, %s, %s, %s, %s)""",
                                (question, answer, tenant_id, 0, 'documentation')
                            )
                            conn.commit()
                            new_count += 1
                except Exception as e:
                    print(f"   ⚠️  Error saving FAQ: {e}")
    
    return new_count


def extract_faqs_with_ai(text: str, tenant_id: str) -> int:
    """Use AI to generate potential FAQs from documentation."""
    from database.db_manager import db_manager
    
    system_prompt = """You are an FAQ generator. Analyze the documentation and generate 5-7 frequently asked questions with answers.

For each FAQ:
1. question: A clear, natural question users would ask (max 200 chars)
2. answer: A concise answer based on the documentation (max 500 chars)

Output format (JSON array):
[
  {"question": "How do I create a new workflow?", "answer": "Navigate to Workflows, click Create New, fill in details..."},
  {"question": "What are the approval stages?", "answer": "There are 3 approval stages: draft, review, and final approval..."}
]

Output ONLY valid JSON array, no other text."""

    user_prompt = f"""Documentation Text:
{text}

Generate FAQs based on this documentation."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean and parse JSON
        if content.startswith("```"):
            content = re.sub(r'```json\s*|\s*```', '', content)
        
        faqs = json.loads(content)
        
        # Save to database
        new_count = 0
        for faq in faqs:
            if isinstance(faq, dict) and 'question' in faq and 'answer' in faq:
                try:
                    question = faq['question'][:500]
                    answer = faq['answer'][:1000]
                    
                    with db_manager.get_connection() as conn:
                        cursor = conn.execute(
                            "SELECT COUNT(*) as count FROM frequently_asked_questions WHERE question = %s",
                            (question,)
                        )
                        result = cursor.fetchone()
                        
                        if result and result[0] == 0:
                            conn.execute(
                                """INSERT INTO frequently_asked_questions 
                                   (question, answer, tenant_id, ask_count, category) 
                                   VALUES (%s, %s, %s, %s, %s)""",
                                (question, answer, tenant_id, 0, 'generated')
                            )
                            conn.commit()
                            new_count += 1
                except Exception as e:
                    print(f"   ⚠️  Error saving FAQ: {e}")
        
        return new_count
        
    except Exception as e:
        print(f"   ⚠️  FAQ generation error: {e}")
        return 0


def detect_document_category(text: str, filename: str) -> str:
    """Detect the category of the document."""
    text_lower = text.lower()
    filename_lower = filename.lower()
    
    # Simple keyword-based detection
    if any(word in text_lower or word in filename_lower for word in ['getting started', 'quick start', 'introduction', 'intro']):
        return 'getting-started'
    elif any(word in text_lower or word in filename_lower for word in ['how to', 'guide', 'tutorial', 'step by step']):
        return 'how-to'
    elif any(word in text_lower or word in filename_lower for word in ['troubleshoot', 'error', 'fix', 'problem', 'issue']):
        return 'troubleshooting'
    elif any(word in text_lower or word in filename_lower for word in ['reference', 'api', 'specification', 'docs']):
        return 'reference'
    elif any(word in text_lower or word in filename_lower for word in ['feature', 'capability', 'functionality']):
        return 'features'
    elif any(word in text_lower or word in filename_lower for word in ['config', 'setup', 'settings', 'configuration']):
        return 'configuration'
    else:
        return 'reference'  # Default


def extract_synonyms(text: str, tenant_id: str) -> int:
    """Extract synonyms and aliases from documentation."""
    from database.db_manager import db_manager
    
    system_prompt = """You are a synonym extraction expert. Analyze the documentation and find terms that are used interchangeably or as synonyms.

Extract pairs of synonymous terms (main term and its synonym).

Output format (JSON array):
[
  {"primary_term": "workflow", "synonym": "process flow", "synonym_type": "exact"},
  {"primary_term": "approve", "synonym": "authorize", "synonym_type": "exact"},
  {"primary_term": "req", "synonym": "request", "synonym_type": "abbreviation"}
]

Synonym types: exact, abbreviation, colloquial, technical

Extract 5-10 synonym pairs. Output ONLY valid JSON array, no other text."""

    user_prompt = f"""Documentation Text:
{text[:3000]}

Extract synonym pairs from this documentation."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```"):
            content = re.sub(r'```json\s*|\s*```', '', content)
        
        synonyms = json.loads(content)
        
        new_count = 0
        for syn in synonyms:
            if isinstance(syn, dict) and 'primary_term' in syn and 'synonym' in syn:
                try:
                    with db_manager.get_connection() as conn:
                        cursor = conn.execute(
                            "SELECT COUNT(*) as count FROM term_synonyms WHERE primary_term = %s AND synonym = %s",
                            (syn['primary_term'].lower(), syn['synonym'].lower())
                        )
                        result = cursor.fetchone()
                        
                        if result and result[0] == 0:
                            conn.execute(
                                """INSERT INTO term_synonyms 
                                   (primary_term, synonym, synonym_type, tenant_id) 
                                   VALUES (%s, %s, %s, %s)""",
                                (syn['primary_term'].lower(), syn['synonym'].lower(), 
                                 syn.get('synonym_type', 'exact'), tenant_id)
                            )
                            conn.commit()
                            new_count += 1
                except Exception as e:
                    pass
        
        return new_count
        
    except Exception as e:
        return 0


def extract_suggestions(text: str, tenant_id: str) -> int:
    """Extract auto-suggestions from documentation."""
    from database.db_manager import db_manager
    
    system_prompt = """You are a suggestion generator. Based on the documentation, create helpful auto-suggestions that users might want to explore.

Generate 5-8 suggestions like:
- Common questions
- Key topics
- Popular features

Output format (JSON array):
[
  {"suggestion_text": "How to create a workflow?", "suggestion_type": "query", "category": "getting-started"},
  {"suggestion_text": "Approval process overview", "suggestion_type": "topic", "category": "features"}
]

Output ONLY valid JSON array, no other text."""

    user_prompt = f"""Documentation Text:
{text[:3000]}

Generate helpful auto-suggestions."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4,
            max_tokens=600
        )
        
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```"):
            content = re.sub(r'```json\s*|\s*```', '', content)
        
        suggestions = json.loads(content)
        
        new_count = 0
        for sug in suggestions:
            if isinstance(sug, dict) and 'suggestion_text' in sug:
                try:
                    with db_manager.get_connection() as conn:
                        cursor = conn.execute(
                            "SELECT COUNT(*) as count FROM auto_suggestions WHERE suggestion_text = %s",
                            (sug['suggestion_text'],)
                        )
                        result = cursor.fetchone()
                        
                        if result and result[0] == 0:
                            conn.execute(
                                """INSERT INTO auto_suggestions 
                                   (suggestion_text, suggestion_type, category, tenant_id, popularity_score) 
                                   VALUES (%s, %s, %s, %s, %s)""",
                                (sug['suggestion_text'], 
                                 sug.get('suggestion_type', 'query'),
                                 sug.get('category', 'general'),
                                 tenant_id,
                                 5.0)
                            )
                            conn.commit()
                            new_count += 1
                except Exception as e:
                    pass
        
        return new_count
        
    except Exception as e:
        return 0


def save_document_metadata(filename: str, content: str, category: str, tenant_id: str):
    """Save document metadata to database."""
    from database.db_manager import db_manager
    import hashlib
    
    try:
        # Get or create category_id
        category_id = None
        if category:
            with db_manager.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT id FROM document_categories WHERE category_key = %s",
                    (category,)
                )
                result = cursor.fetchone()
                if result:
                    category_id = result[0]
        
        # Calculate file size
        file_size_kb = len(content) // 1024
        
        # Extract title (first heading or first line)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else filename
        
        # Save or update document metadata
        with db_manager.get_connection() as conn:
            cursor = conn.execute(
                "SELECT id FROM document_metadata WHERE filename = %s AND tenant_id = %s",
                (filename, tenant_id)
            )
            result = cursor.fetchone()
            
            if result:
                # Update existing
                conn.execute(
                    """UPDATE document_metadata 
                       SET category_id = %s, title = %s, file_size_kb = %s, last_indexed_at = NOW()
                       WHERE id = %s""",
                    (category_id, title, file_size_kb, result[0])
                )
            else:
                # Insert new
                conn.execute(
                    """INSERT INTO document_metadata 
                       (filename, category_id, title, file_size_kb, tenant_id, last_indexed_at) 
                       VALUES (%s, %s, %s, %s, %s, NOW())""",
                    (filename, category_id, title, file_size_kb, tenant_id)
                )
            conn.commit()
            
    except Exception as e:
        print(f"   ⚠️  Error saving document metadata: {e}")

