from openai import OpenAI
from config import OPENAI_API_KEY, GPT_MODEL
from datetime import datetime, timedelta
import json

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Cache for ERP modules (refreshes every 10 minutes)
_module_cache = None
_module_cache_timestamp = None
MODULE_CACHE_DURATION = timedelta(minutes=10)

def load_erp_modules():
    """
    Load ERP modules from database with caching
    Returns list of module descriptions for AI prompt
    """
    global _module_cache, _module_cache_timestamp
    
    # Check if cache is valid
    if _module_cache and _module_cache_timestamp:
        if datetime.now() - _module_cache_timestamp < MODULE_CACHE_DURATION:
            return _module_cache
    
    # Try to load from database
    try:
        from database.db_manager import db_manager
        module_list = db_manager.get_module_names_for_prompt()
        
        if module_list:
            _module_cache = module_list
            _module_cache_timestamp = datetime.now()
            return module_list
    except Exception as e:
        print(f"Warning: Could not load modules from database: {e}", flush=True)
    
    # Fallback to default modules if database unavailable
    return get_default_modules()

def get_default_modules():
    """Fallback default modules if database is unavailable"""
    return [
        "- Finance/Accounting",
        "- Human Resources (HR)",
        "- Sales",
        "- Purchasing",
        "- Inventory/Warehouse",
        "- Manufacturing",
        "- CRM (Customer Relationship Management)",
        "- Workflow",
        "- Reporting",
        "- General"
    ]

def refresh_module_cache():
    """Force refresh the module cache"""
    global _module_cache, _module_cache_timestamp
    _module_cache = None
    _module_cache_timestamp = None
    return load_erp_modules()

def detect_module(query: str):
    """
    Detect which ERP module the query is related to using OpenAI's ChatGPT.
    Modules are loaded dynamically from database and cached for 10 minutes.
    """
    try:
        # Load modules (from cache or database)
        modules = load_erp_modules()
        modules_text = "\n".join(modules)
        
        # Create the prompt for module classification
        system_prompt = f"""You are an ERP module classifier. Analyze the user's query and determine which ERP module it relates to.

Common ERP modules include:
{modules_text}

Respond with only the module name (without description or code)."""

        # Call OpenAI ChatGPT API
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Classify this query: {query}"}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        module = response.choices[0].message.content.strip()
        return module
    except Exception as e:
        print(f"Error detecting module: {e}")
        return "General"