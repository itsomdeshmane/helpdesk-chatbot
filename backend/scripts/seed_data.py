"""
Seed query type patterns and ERP modules into MySQL database
Simple version without Unicode characters for Windows compatibility
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import db_manager

def seed_modules():
    """Seed initial ERP modules"""
    
    print("="*60)
    print("SEEDING ERP MODULES")
    print("="*60)
    
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
        success = db_manager.bulk_add_erp_modules(modules)
        
        if success:
            print("[OK] Modules seeded successfully!")
            loaded_modules = db_manager.get_erp_modules(active_only=True)
            print(f"\n[INFO] Total modules in database: {len(loaded_modules)}")
            print(f"\n[INFO] Modules:")
            for module in loaded_modules:
                print(f"   - {module['module_name']} ({module['module_code']}): {module['description']}")
        else:
            print("[ERROR] Failed to seed modules")
            return False
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def seed_patterns():
    """Seed initial query type patterns"""
    
    print("\n" + "="*60)
    print("SEEDING QUERY TYPE PATTERNS")
    print("="*60)
    
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
        
        # Step-by-step questions (priority 5)
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
        success = db_manager.bulk_add_query_patterns(patterns)
        
        if success:
            print("[OK] Patterns seeded successfully!")
            loaded_patterns = db_manager.get_query_type_patterns()
            
            print(f"\n[INFO] Total patterns: {sum(len(keywords) for keywords in loaded_patterns.values())}")
            print(f"\n[INFO] Patterns by type:")
            for query_type, keywords in sorted(loaded_patterns.items()):
                print(f"   - {query_type}: {len(keywords)} keywords")
        else:
            print("[ERROR] Failed to seed patterns")
            return False
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def seed_all():
    """Seed both modules and patterns"""
    print("\n" + "="*80)
    print("SEEDING ALL DATA")
    print("="*80 + "\n")
    
    if not seed_modules():
        print("\n[ERROR] Module seeding failed!")
        return False
    
    if not seed_patterns():
        print("\n[ERROR] Pattern seeding failed!")
        return False
    
    print("\n" + "="*80)
    print("[SUCCESS] ALL DATA SEEDED SUCCESSFULLY!")
    print("="*80)
    print("\n[INFO] Database is now ready with:")
    print("   - ERP Modules (for dynamic classification)")
    print("   - Query Type Patterns (for dynamic detection)")
    print("\n[TIP] Patterns and modules are cached for performance")
    print("[TIP] Restart your backend server to use the new data\n")
    
    return True

if __name__ == "__main__":
    seed_all()

