# PowerShell script to setup normalized ERP database with sample data

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ERP Database Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$mysqlUser = "root"
$mysqlPassword = Read-Host "Enter MySQL root password" -AsSecureString
$mysqlPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($mysqlPassword))

Write-Host "`n📊 Creating normalized database schema..." -ForegroundColor Yellow

try {
    # Run the SQL script
    $command = "mysql -u $mysqlUser -p$mysqlPasswordPlain < Database_Schema_Normalized.sql"
    Invoke-Expression $command
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database created successfully!" -ForegroundColor Green
        
        # Verify the data
        Write-Host "`n📈 Verifying data..." -ForegroundColor Yellow
        $verifyCommand = @"
mysql -u $mysqlUser -p$mysqlPasswordPlain -D erp_demo -e "
SELECT 'Database Statistics:' as Info;
SELECT 
    (SELECT COUNT(*) FROM vendors) as Vendors,
    (SELECT COUNT(*) FROM customers) as Customers,
    (SELECT COUNT(*) FROM products) as Products,
    (SELECT COUNT(*) FROM purchase_orders) as PurchaseOrders,
    (SELECT COUNT(*) FROM vendor_payments) as Payments,
    (SELECT CONCAT('\\$', FORMAT(SUM(amount), 2)) FROM vendor_payments) as TotalRevenue;
"
"@
        Invoke-Expression $verifyCommand
        
        Write-Host "`n✅ Setup Complete!" -ForegroundColor Green
        Write-Host "`n📋 Summary:" -ForegroundColor Cyan
        Write-Host "  - Database: erp_demo" -ForegroundColor White
        Write-Host "  - Tables: 9 (vendors, customers, products, purchase_orders, etc.)" -ForegroundColor White
        Write-Host "  - Views: 3 (revenue summaries)" -ForegroundColor White
        Write-Host "  - Sample Data: Loaded" -ForegroundColor White
        
        Write-Host "`n🚀 You can now query:" -ForegroundColor Yellow
        Write-Host "  - 'Top 10 vendors with more revenue'" -ForegroundColor White
        Write-Host "  - 'Vendors in India'" -ForegroundColor White
        Write-Host "  - 'Total revenue by country'" -ForegroundColor White
        
    } else {
        Write-Host "❌ Failed to create database" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan

