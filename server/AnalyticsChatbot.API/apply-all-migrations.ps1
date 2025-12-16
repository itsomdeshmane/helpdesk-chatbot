# PowerShell script to apply all database migrations

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DATABASE MIGRATION SCRIPT" -ForegroundColor Cyan
Write-Host "   Applying ALL Migrations" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Get MySQL credentials
Write-Host "`n🔐 MySQL Credentials" -ForegroundColor Yellow
$mysqlUser = Read-Host "Enter MySQL username (default: root)"
if ([string]::IsNullOrWhiteSpace($mysqlUser)) {
    $mysqlUser = "root"
}

$mysqlPassword = Read-Host "Enter MySQL password" -AsSecureString
$mysqlPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($mysqlPassword))

Write-Host "`n📊 Starting migration process..." -ForegroundColor Yellow
Write-Host "This will:" -ForegroundColor White
Write-Host "  1. Create Identity database (chatbot_identity)" -ForegroundColor White
Write-Host "  2. Create Chat Session tables" -ForegroundColor White
Write-Host "  3. Create RAG/Smart Chat tables" -ForegroundColor White
Write-Host "  4. Create ERP database (erp_demo)" -ForegroundColor White
Write-Host "  5. Insert sample data" -ForegroundColor White
Write-Host "  6. Create views" -ForegroundColor White

$confirm = Read-Host "`nProceed with migration? (y/n)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "❌ Migration cancelled" -ForegroundColor Red
    exit 0
}

Write-Host "`n⏳ Applying migrations..." -ForegroundColor Yellow

try {
    # Apply all migrations
    $output = mysql -u $mysqlUser -p$mysqlPasswordPlain < Database_Migration_All.sql 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ ALL MIGRATIONS APPLIED SUCCESSFULLY!" -ForegroundColor Green
        
        Write-Host "`n📊 Database Summary:" -ForegroundColor Cyan
        
        # Show identity database tables
        Write-Host "`n1️⃣  Identity Database (chatbot_identity):" -ForegroundColor Yellow
        mysql -u $mysqlUser -p$mysqlPasswordPlain -D chatbot_identity -e "SHOW TABLES;" 2>$null
        
        # Show ERP database tables
        Write-Host "`n2️⃣  ERP Database (erp_demo):" -ForegroundColor Yellow
        mysql -u $mysqlUser -p$mysqlPasswordPlain -D erp_demo -e "SHOW TABLES;" 2>$null
        
        # Show data statistics
        Write-Host "`n3️⃣  Data Statistics:" -ForegroundColor Yellow
        mysql -u $mysqlUser -p$mysqlPasswordPlain -D erp_demo -e "
        SELECT 
            (SELECT COUNT(*) FROM vendors) as Vendors,
            (SELECT COUNT(*) FROM customers) as Customers,
            (SELECT COUNT(*) FROM products) as Products,
            (SELECT COUNT(*) FROM purchase_orders) as PurchaseOrders,
            (SELECT COUNT(*) FROM vendor_payments) as VendorPayments,
            (SELECT CONCAT('\\$', FORMAT(SUM(amount), 2)) FROM vendor_payments) as TotalRevenue;
        " 2>$null
        
        # Test vendor revenue query
        Write-Host "`n4️⃣  Top 5 Vendors by Revenue:" -ForegroundColor Yellow
        mysql -u $mysqlUser -p$mysqlPasswordPlain -D erp_demo -e "
        SELECT 
            vendor_name as Vendor,
            country as Country,
            CONCAT('\\$', FORMAT(total_revenue, 2)) as Revenue
        FROM vendor_revenue_summary
        ORDER BY total_revenue DESC
        LIMIT 5;
        " 2>$null
        
        Write-Host "`n========================================" -ForegroundColor Cyan
        Write-Host "✅ MIGRATION COMPLETE!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        
        Write-Host "`n📝 Next Steps:" -ForegroundColor Yellow
        Write-Host "  1. Update appsettings.json with MySQL credentials" -ForegroundColor White
        Write-Host "  2. Restart the API: dotnet run" -ForegroundColor White
        Write-Host "  3. Start Angular app: cd ../../client && npm start" -ForegroundColor White
        Write-Host "  4. Test queries:" -ForegroundColor White
        Write-Host "     - 'Register a new user'" -ForegroundColor Gray
        Write-Host "     - 'Login'" -ForegroundColor Gray
        Write-Host "     - 'Top 10 vendors with more revenue'" -ForegroundColor Gray
        Write-Host "     - 'How many vendors in India?'" -ForegroundColor Gray
        
        Write-Host "`n✨ All systems ready!" -ForegroundColor Green
        
    } else {
        Write-Host "`n❌ Migration failed" -ForegroundColor Red
        Write-Host "Error details:" -ForegroundColor Red
        Write-Host $output -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "`n❌ Error during migration:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan

