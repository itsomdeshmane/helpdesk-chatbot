"""
Seed query type patterns and ERP modules into MySQL database
Run this script after database setup to populate default patterns and modules
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import db_manager

def seed_modules():
    """Seed initial ERP modules"""
    
    print("="*60)
    print("SEEDING ERP MODULES")
    print("="*60)
    
    # Define modules: (module_name, module_code, description, keywords, priority)
    modules = [
        ('Finance', 'FIN', 'Financial management, accounting, general ledger, AP, AR', 
         'accounting,finance,ledger,payment,invoice,bill,credit,debit,journal,fiscal', 10),
        
        ('Human Resources', 'HR', 'Employee management, payroll, attendance, recruitment',
         'employee,hr,payroll,attendance,leave,recruitment,staff,personnel,hiring', 9),
        
        ('Sales', 'SAL', 'Sales orders, quotations, customer orders, revenue',
         'sales,order,customer,quote,quotation,revenue,sell,selling,so,customer order', 8),
        
        ('Purchasing', 'PUR', 'Purchase orders, vendors, procurement, requisitions',
         'purchase,vendor,procurement,supplier,po,requisition,buying,buy', 8),
        
        ('Inventory', 'INV', 'Stock management, warehouse, items, materials',
         'inventory,stock,warehouse,item,material,wip,location,bin,demand', 7),
        
        ('Manufacturing', 'MFG', 'Production, work orders, BOMs, routing',
         'manufacturing,production,work order,wo,bom,routing,assembly,fabrication', 7),
        
        ('CRM', 'CRM', 'Customer relationship management, leads, opportunities',
         'crm,lead,opportunity,contact,customer relationship,pipeline,prospect', 6),
        
        ('Workflow', 'WF', 'Job management, work orders, change requests, shipping',
         'workflow,job,shipper,change request,release,active work,send to production', 6),
        
        ('Reporting', 'RPT', 'Reports, analytics, dashboard, insights',
         'report,analytics,dashboard,insight,statistics,data,metrics', 5),
        
        ('Service', 'SRV', 'Service orders, maintenance, machines, service issues',
         'service,maintenance,machine,repair,service issue,service order,equipment', 6),
        
        ('Accounting Settings', 'ACC_SET', 'Accounting configuration, setup, chart of accounts',
         'accounting setting,setup,configuration,chart of accounts,fiscal year,company settings', 4),
        
        ('General', 'GEN', 'General queries, navigation, system help',
         'general,help,how to,navigation,menu,system,getting started,about', 1),
    ]
    
    print(f"\nSeeding {len(modules)} modules...")
    print("-"*60)
    
    try:
        # Bulk insert modules
        success = db_manager.bulk_add_erp_modules(modules)
        
        if success:
            print("✅ Modules seeded successfully!")
            
            # Verify
            loaded_modules = db_manager.get_erp_modules(active_only=True)
            
            print(f"\n📊 Summary:")
            print(f"   Total modules in database: {len(loaded_modules)}")
            print(f"\n   Modules:")
            for module in loaded_modules:
                print(f"   • {module['module_name']} ({module['module_code']}): {module['description']}")
            
            print("\n" + "="*60)
            print("✅ ERP modules ready to use!")
            print("="*60)
            
        else:
            print("❌ Failed to seed modules")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def seed_patterns():
    """Seed initial query type patterns"""
    
    print("="*60)
    print("SEEDING QUERY TYPE PATTERNS")
    print("="*60)
    
    # Define patterns: (query_type, keyword, priority)
    patterns = [
        # List-type questions (priority 5)
        ('list', 'list', 5),
        ('list', 'types of', 5),
        ('list', 'kinds of', 5),
        ('list', 'what are', 5),
        ('list', 'all the', 5),
        ('list', 'different', 4),
        ('list', 'options', 4),
        ('list', 'choices', 4),
        ('list', 'categories', 4),
        ('list', 'available', 3),
        
        # Step-by-step/How-to questions (priority 5)
        ('step-by-step', 'how to', 5),
        ('step-by-step', 'how do i', 5),
        ('step-by-step', 'how can i', 5),
        ('step-by-step', 'configure', 5),
        ('step-by-step', 'setup', 5),
        ('step-by-step', 'set up', 5),
        ('step-by-step', 'install', 5),
        ('step-by-step', 'enable', 4),
        ('step-by-step', 'create', 4),
        ('step-by-step', 'add', 4),
        ('step-by-step', 'steps to', 5),
        ('step-by-step', 'procedure', 4),
        ('step-by-step', 'process', 3),
        
        # Definition questions (priority 5)
        ('definition', 'what is', 5),
        ('definition', 'what does', 5),
        ('definition', 'define', 5),
        ('definition', 'explain', 5),
        ('definition', 'meaning of', 5),
        ('definition', 'definition', 4),
        ('definition', 'describe', 4),
        ('definition', 'tell me about', 4),
        
        # Comparison questions (priority 5)
        ('comparison', 'difference between', 5),
        ('comparison', 'vs', 5),
        ('comparison', 'versus', 5),
        ('comparison', 'compare', 5),
        ('comparison', 'better than', 5),
        ('comparison', 'which is better', 5),
        ('comparison', 'pros and cons', 4),
        ('comparison', 'advantages', 3),
        ('comparison', 'disadvantages', 3),
        
        # Troubleshooting questions (priority 5)
        ('troubleshooting', 'error', 5),
        ('troubleshooting', 'not working', 5),
        ('troubleshooting', 'issue', 5),
        ('troubleshooting', 'problem', 5),
        ('troubleshooting', 'fix', 5),
        ('troubleshooting', 'troubleshoot', 5),
        ('troubleshooting', 'debug', 5),
        ('troubleshooting', 'broken', 5),
        ('troubleshooting', 'failed', 4),
        ('troubleshooting', 'why is', 4),
        ('troubleshooting', 'cant', 4),
        ('troubleshooting', "can't", 4),
        ('troubleshooting', "won't", 4),
        ('troubleshooting', "doesn't work", 5),
    ]
    
    print(f"\nSeeding {len(patterns)} patterns...")
    print("-"*60)
    
    try:
        # Bulk insert patterns
        success = db_manager.bulk_add_query_patterns(patterns)
        
        if success:
            print("✅ Patterns seeded successfully!")
            
            # Verify
            loaded_patterns = db_manager.get_query_type_patterns()
            
            print(f"\n📊 Summary:")
            print(f"   Total patterns in database: {sum(len(keywords) for keywords in loaded_patterns.values())}")
            print(f"\n   Patterns by type:")
            for query_type, keywords in sorted(loaded_patterns.items()):
                print(f"   • {query_type}: {len(keywords)} keywords")
            
            print("\n" + "="*60)
            print("✅ Query patterns ready to use!")
            print("="*60)
            print("\n💡 Usage:")
            print("   - Patterns are cached for 5 minutes")
            print("   - Add new patterns via database or API")
            print("   - Update priority to control matching order")
            print("   - Set is_active=FALSE to disable without deleting")
            print("\n")
            
        else:
            print("❌ Failed to seed patterns")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def list_patterns():
    """List all patterns currently in database"""
    print("\n" + "="*60)
    print("CURRENT QUERY TYPE PATTERNS")
    print("="*60)
    
    try:
        patterns = db_manager.get_query_type_patterns()
        
        if not patterns:
            print("\n⚠️  No patterns found in database!")
            print("   Run: python seed_query_patterns.py")
            return
        
        for query_type, keywords in sorted(patterns.items()):
            print(f"\n📋 {query_type.upper()} ({len(keywords)} keywords):")
            for keyword in sorted(keywords):
                print(f"   - {keyword}")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_detection():
    """Test query type detection with current patterns"""
    print("\n" + "="*60)
    print("TESTING QUERY TYPE DETECTION")
    print("="*60)
    
    # Force reload patterns from database
    from llm.prompt_enhancer import detect_query_type, refresh_pattern_cache
    refresh_pattern_cache()
    
    test_queries = [
        "List all the modules in Verax",
        "How do I create a purchase order?",
        "What is a sales order?",
        "What's the difference between PO and SO?",
        "I'm getting an error when saving",
        "Tell me about the inventory module",
    ]
    
    print("\nTesting queries:")
    print("-"*60)
    
    for query in test_queries:
        detected_type = detect_query_type(query)
        print(f"'{query}'")
        print(f"  → Type: {detected_type}\n")
    
    print("="*60)

def list_modules():
    """List all modules currently in database"""
    print("\n" + "="*60)
    print("CURRENT ERP MODULES")
    print("="*60)
    
    try:
        modules = db_manager.get_erp_modules(active_only=True)
        
        if not modules:
            print("\n⚠️  No modules found in database!")
            print("   Run: python seed_query_patterns.py")
            return
        
        for module in modules:
            print(f"\n📦 {module['module_name']} ({module['module_code']})")
            print(f"   Description: {module['description']}")
            if module['keywords']:
                print(f"   Keywords: {module['keywords']}")
            print(f"   Priority: {module['priority']}")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_module_detection():
    """Test module detection with current modules"""
    print("\n" + "="*60)
    print("TESTING MODULE DETECTION")
    print("="*60)
    
    # Force reload modules from database
    from llm.classifier import detect_module, refresh_module_cache
    refresh_module_cache()
    
    test_queries = [
        "How do I create a sales order?",
        "What's the current inventory level?",
        "I need to add a new employee",
        "How to configure chart of accounts?",
        "Issue with purchase order approval",
        "Generate sales report for last month",
    ]
    
    print("\nTesting queries:")
    print("-"*60)
    
    for query in test_queries:
        detected_module = detect_module(query)
        print(f"'{query}'")
        print(f"  → Module: {detected_module}\n")
    
    print("="*60)

def seed_all():
    """Seed both modules and patterns"""
    print("\n" + "="*80)
    print("SEEDING ALL DATA")
    print("="*80 + "\n")
    
    # Seed modules first
    if not seed_modules():
        print("\n❌ Module seeding failed!")
        return False
    
    print("\n")
    
    # Then seed patterns
    if not seed_patterns():
        print("\n❌ Pattern seeding failed!")
        return False
    
    print("\n" + "="*80)
    print("✅ ALL DATA SEEDED SUCCESSFULLY!")
    print("="*80)
    print("\n📝 Database is now ready with:")
    print("   • ERP Modules (for dynamic classification)")
    print("   • Query Type Patterns (for dynamic detection)")
    print("\n💡 Use 'list-modules' and 'list-patterns' to view data")
    print("💡 Use 'test' to test the detection systems\n")
    
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "list-patterns" or command == "list":
            list_patterns()
        elif command == "list-modules":
            list_modules()
        elif command == "test-patterns":
            test_detection()
        elif command == "test-modules":
            test_module_detection()
        elif command == "test":
            test_detection()
            print()
            test_module_detection()
        elif command == "modules":
            seed_modules()
        elif command == "patterns":
            seed_patterns()
        else:
            print("Usage: python seed_query_patterns.py [command]")
            print("\nCommands:")
            print("  (none)         - Seed both modules and patterns (default)")
            print("  modules        - Seed only modules")
            print("  patterns       - Seed only patterns")
            print("  list-modules   - List all modules")
            print("  list-patterns  - List all patterns")
            print("  test           - Test both detection systems")
            print("  test-modules   - Test module detection")
            print("  test-patterns  - Test pattern detection")
    else:
        # Default: seed everything
        seed_all()

