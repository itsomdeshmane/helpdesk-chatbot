"""
Enhanced prompts for better formatted responses
"""

def detect_query_type(query: str) -> str:
    """Detect what type of response is needed"""
    query_lower = query.lower()
    
    # List-type questions
    list_keywords = ['list', 'types of', 'kinds of', 'what are', 'all the', 'different', 'options', 'choices']
    if any(keyword in query_lower for keyword in list_keywords):
        return 'list'
    
    # Configuration/setup questions
    config_keywords = ['how to', 'how do i', 'configure', 'setup', 'set up', 'install', 'enable', 'create', 'add']
    if any(keyword in query_lower for keyword in config_keywords):
        return 'step-by-step'
    
    # Definition questions
    definition_keywords = ['what is', 'what does', 'define', 'explain', 'meaning of']
    if any(keyword in query_lower for keyword in definition_keywords):
        return 'definition'
    
    # Comparison questions
    comparison_keywords = ['difference between', 'vs', 'versus', 'compare', 'better than']
    if any(keyword in query_lower for keyword in comparison_keywords):
        return 'comparison'
    
    # Troubleshooting questions
    troubleshoot_keywords = ['error', 'not working', 'issue', 'problem', 'fix', 'troubleshoot', 'debug']
    if any(keyword in query_lower for keyword in troubleshoot_keywords):
        return 'troubleshooting'
    
    return 'general'


def get_enhanced_prompt(query: str, context: str, query_type: str = None) -> tuple:
    """
    Get enhanced system and user prompts based on query type
    Returns: (system_prompt, user_prompt)
    """
    
    if query_type is None:
        query_type = detect_query_type(query)
    
    base_instructions = """You are a helpful AI assistant for the Verax ERP helpdesk system.

🚨 CRITICAL RULES - MUST FOLLOW STRICTLY:
1. ONLY use information from the provided documentation context below
2. DO NOT use your general knowledge or training data
3. DO NOT make assumptions or infer information not explicitly stated in the context
4. If the context doesn't contain the answer, respond with: "I don't have this information in the current documentation. Please contact support or check the complete documentation."
5. Extract ALL relevant details ONLY from the provided documentation
6. For lists, include EVERYTHING mentioned in the context - don't skip items
7. Use simple, clear language that anyone can understand
8. DO NOT add information from outside the provided context, even if you know it

⚠️ NEVER HALLUCINATE OR MAKE UP INFORMATION ⚠️

FORMATTING RULES:
"""

    if query_type == 'list':
        system_prompt = base_instructions + """
- When asked for a list, extract the COMPLETE list from the documentation
- For modules/submodules: List ALL items mentioned in the context, don't skip any
- Use bullet points (•) or numbered lists (1, 2, 3)
- Include brief descriptions if provided in documentation
- Start with a clear introduction
- Example format:
  
  Here are the submodules in the Purchasing module:
  
  • Vendors - Manage supplier information
  • Manufacturers - Track product manufacturers  
  • Purchase Orders - Create and manage purchase orders
  • Requisitions - Request items for purchase
  • Request for Quote (RFQ) - Request quotes from vendors
  • Current Demand - View material requirements
  • Purchasing Reports - Generate purchasing analytics

IMPORTANT: Extract ALL items from the documentation. Do not summarize or reduce the list.

Classify the ERP module at the end as: MODULE: [module name]"""

    elif query_type == 'step-by-step':
        system_prompt = base_instructions + """
- Provide STEP-BY-STEP instructions for configuration/setup questions
- Number each step clearly (Step 1, Step 2, etc.)
- Keep steps simple and actionable
- Mention prerequisites if any
- Add notes or warnings if needed
- Example format:

  To configure the inventory module, follow these steps:
  
  Step 1: Navigate to Settings
  Go to the main menu and click on "System Settings"
  
  Step 2: Select Inventory Module
  Click on "Inventory" from the modules list
  
  Step 3: Configure Basic Settings
  - Set your default warehouse
  - Choose your inventory valuation method
  - Enable stock tracking
  
  Step 4: Save and Test
  Click "Save Changes" and verify the settings

Classify the ERP module at the end as: MODULE: [module name]"""

    elif query_type == 'definition':
        system_prompt = base_instructions + """
- Start with a clear, simple definition (1-2 sentences)
- Explain in plain language (avoid technical jargon)
- Provide a real-world example if helpful
- Mention key features or benefits
- Example format:

  An ERP (Enterprise Resource Planning) system is software that helps businesses manage their daily operations in one place.
  
  It combines different business functions like:
  - Accounting and finance
  - Inventory management
  - Sales and purchasing
  - Human resources
  
  Think of it as a central hub where all business information comes together, making it easier to make decisions and run your business efficiently.

Classify the ERP module at the end as: MODULE: [module name]"""

    elif query_type == 'comparison':
        system_prompt = base_instructions + """
- Use a clear comparison format
- Highlight key differences
- Use tables or side-by-side comparison when appropriate
- Be objective and factual
- Example format:

  Here's the difference between FIFO and LIFO inventory methods:
  
  FIFO (First In, First Out):
  - Items purchased first are sold first
  - Better for perishable goods
  - Usually results in higher profits during inflation
  - More commonly used
  
  LIFO (Last In, First Out):
  - Items purchased last are sold first
  - Better for non-perishable items
  - Can reduce tax liability during inflation
  - Less commonly used internationally

Classify the ERP module at the end as: MODULE: [module name]"""

    elif query_type == 'troubleshooting':
        system_prompt = base_instructions + """
- Start by acknowledging the problem
- Provide step-by-step troubleshooting guide
- Offer multiple solutions if possible
- Explain what might cause the issue
- Example format:

  I understand you're experiencing an error. Let's troubleshoot this:
  
  Common Causes:
  - Incorrect permissions
  - Missing data
  - System configuration issue
  
  Try these solutions:
  
  Solution 1: Check User Permissions
  1. Go to User Settings
  2. Verify you have the required access level
  3. Contact admin if permissions are missing
  
  Solution 2: Clear Cache and Reload
  1. Clear your browser cache
  2. Refresh the page
  3. Try the operation again
  
  If the issue persists, please contact technical support with the error code.

Classify the ERP module at the end as: MODULE: [module name]"""

    else:  # general
        system_prompt = base_instructions + """
- Provide clear, well-structured answers
- Use paragraphs for explanations
- Use bullet points for lists within the answer
- Keep language simple and professional
- Break complex topics into smaller sections

Classify the ERP module at the end as: MODULE: [module name]"""

    # Limit context size (larger for list queries to get complete sections)
    max_context_chars = 5000 if query_type == 'list' else 3000
    if len(context) > max_context_chars:
        context = context[:max_context_chars] + "\n... (additional context available)"
    
    user_prompt = f"""Documentation Context:
{context}

User Question: {query}

INSTRUCTIONS:
- Answer STRICTLY using ONLY the information from the Documentation Context above
- DO NOT use any external knowledge or general information
- If the answer is not in the context, clearly state: "I don't have this information in the current documentation."
- Include all relevant details found in the context
- Do not add, assume, or infer anything beyond what is explicitly stated in the context"""

    return system_prompt, user_prompt


def is_complex_query(query: str) -> tuple:
    """
    Detect if query is too complex and should be broken down
    Returns: (is_complex, suggested_subquestions)
    """
    query_lower = query.lower()
    
    # Check for multiple questions
    question_markers = ['and', ' or ', 'also', 'plus', 'as well as', 'additionally']
    has_multiple = any(marker in query_lower for marker in question_markers)
    
    # Check for very long query
    is_too_long = len(query.split()) > 20
    
    # Check for broad questions
    broad_keywords = ['everything', 'all about', 'complete', 'entire', 'whole system']
    is_too_broad = any(keyword in query_lower for keyword in broad_keywords)
    
    if has_multiple or is_too_long or is_too_broad:
        # Generate sub-questions
        subquestions = []
        
        if 'and' in query_lower:
            parts = query_lower.split(' and ')
            subquestions = [f"Could you first tell me about {part.strip()}?" for part in parts[:2]]
        elif is_too_broad:
            subquestions = [
                "Would you like to know about the basic features first?",
                "Are you interested in setup and configuration?",
                "Do you need help with specific operations?"
            ]
        
        return True, subquestions
    
    return False, []


