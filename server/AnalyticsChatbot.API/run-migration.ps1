# ============================================
# Complete Database Migration Runner
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ANALYTICS CHATBOT - DATABASE SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Get MySQL credentials
Write-Host "`n[MySQL Connection]" -ForegroundColor Yellow
$mysqlUser = Read-Host "Enter MySQL username (default: root)"
if ([string]::IsNullOrWhiteSpace($mysqlUser)) {
    $mysqlUser = "root"
}

$mysqlPassword = Read-Host "Enter MySQL password" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($mysqlPassword)
$mysqlPasswordPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Test connection
Write-Host "`n[Testing MySQL connection...]" -ForegroundColor Yellow
try {
    $testResult = & mysql -u $mysqlUser "-p$mysqlPasswordPlain" -e "SELECT 1;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Connected to MySQL" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to connect to MySQL" -ForegroundColor Red
        Write-Host "Error: $testResult" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] MySQL not found. Please install MySQL or add it to PATH" -ForegroundColor Red
    exit 1
}

# Confirm migration
Write-Host "`nThis migration will:" -ForegroundColor Yellow
Write-Host "  1. Create chatbot_identity database (Authentication)" -ForegroundColor White
Write-Host "  2. Create erp_demo database (Business Data)" -ForegroundColor White
Write-Host "  3. Create 21 base tables with relationships" -ForegroundColor White
Write-Host "  4. Insert master data (countries, states, cities, etc.)" -ForegroundColor White
Write-Host "  5. Insert sample transaction data" -ForegroundColor White
Write-Host "  6. Create reporting views" -ForegroundColor White

$confirm = Read-Host "`n[WARNING] Proceed? This will DROP and RECREATE erp_demo database (y/n)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "[CANCELLED] Migration cancelled" -ForegroundColor Red
    exit 0
}

Write-Host "`n[Running migration...]" -ForegroundColor Yellow
Write-Host "This may take 30-60 seconds..." -ForegroundColor Gray

try {
    # Run the complete migration script
    $sqlScript = Get-Content -Path "Database_Complete_Migration.sql" -Raw
    $output = $sqlScript | & mysql -u $mysqlUser "-p$mysqlPasswordPlain" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[SUCCESS] MIGRATION COMPLETED!" -ForegroundColor Green
        
        # Show results
        Write-Host "`n========================================" -ForegroundColor Cyan
        Write-Host "   DATABASE SUMMARY" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        
        Write-Host "`n[Checking created databases...]" -ForegroundColor Yellow
        & mysql -u $mysqlUser "-p$mysqlPasswordPlain" -e "SHOW DATABASES LIKE '%chatbot%'; SHOW DATABASES LIKE '%erp%';" 2>$null
        
        Write-Host "`n[Tables in chatbot_identity]" -ForegroundColor Yellow
        & mysql -u $mysqlUser "-p$mysqlPasswordPlain" -D chatbot_identity -e "SELECT COUNT(*) as Total_Tables FROM information_schema.tables WHERE table_schema='chatbot_identity';" 2>$null
        
        Write-Host "`n[Tables in erp_demo]" -ForegroundColor Yellow
        & mysql -u $mysqlUser "-p$mysqlPasswordPlain" -D erp_demo -e "SELECT (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='erp_demo' AND table_type='BASE TABLE') as Tables, (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='erp_demo' AND table_type='VIEW') as Views;" 2>$null
        
        Write-Host "`n[Sample Data Counts]" -ForegroundColor Yellow
        & mysql -u $mysqlUser "-p$mysqlPasswordPlain" -D erp_demo -e "SELECT (SELECT COUNT(*) FROM countries) as Countries, (SELECT COUNT(*) FROM vendors) as Vendors, (SELECT COUNT(*) FROM products) as Products;" 2>$null
        
        Write-Host "`n[Revenue Summary]" -ForegroundColor Yellow
        & mysql -u $mysqlUser "-p$mysqlPasswordPlain" -D erp_demo -e "SELECT CONCAT('`$', FORMAT(SUM(amount), 2)) as Total_Vendor_Revenue FROM vendor_payments;" 2>$null
        
        Write-Host "`n[Top 5 Vendors by Revenue]" -ForegroundColor Yellow
        & mysql -u $mysqlUser "-p$mysqlPasswordPlain" -D erp_demo -e "SELECT vendor_name as Vendor, country, CONCAT('`$', FORMAT(total_revenue, 2)) as Revenue FROM top_vendors_by_revenue LIMIT 5;" 2>$null
        
        Write-Host "`n========================================" -ForegroundColor Cyan
        Write-Host "[SETUP COMPLETE!]" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        
        Write-Host "`nNext Steps:" -ForegroundColor Yellow
        Write-Host "  1. Update appsettings.json with MySQL password" -ForegroundColor White
        Write-Host "  2. Restart the API: dotnet run" -ForegroundColor White
        Write-Host "  3. Start Angular: cd ../../client; npm start" -ForegroundColor White
        Write-Host "  4. Test queries like:" -ForegroundColor White
        Write-Host "     - Give me top 10 vendors with more revenue" -ForegroundColor Gray
        Write-Host "     - How many vendors in India?" -ForegroundColor Gray
        
        Write-Host "`n[SUCCESS] Your Analytics Chatbot is ready!" -ForegroundColor Green
        
    } else {
        Write-Host "`n[ERROR] Migration failed!" -ForegroundColor Red
        Write-Host "Error output:" -ForegroundColor Red
        Write-Host $output -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "`n[ERROR] Error during migration:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
} finally {
    # Clear password from memory
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
}

Write-Host "`n========================================" -ForegroundColor Cyan
