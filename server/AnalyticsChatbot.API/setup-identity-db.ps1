# PowerShell script to setup Identity database for authentication

Write-Host "Setting up Identity Database for Authentication..." -ForegroundColor Green

# Check if MySQL is accessible
Write-Host "`nChecking MySQL connection..." -ForegroundColor Yellow

$mysqlUser = "root"
$mysqlPassword = "root123"

# Test MySQL connection
try {
    $result = mysql -u $mysqlUser -p$mysqlPassword -e "SELECT 1;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ MySQL connection successful" -ForegroundColor Green
    } else {
        Write-Host "✗ MySQL connection failed" -ForegroundColor Red
        Write-Host "Please make sure MySQL is running and credentials are correct" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ MySQL not found. Please install MySQL or check PATH" -ForegroundColor Red
    exit 1
}

# Run the SQL script
Write-Host "`nCreating Identity database and tables..." -ForegroundColor Yellow

try {
    mysql -u $mysqlUser -p$mysqlPassword < Database_Create_Identity_Tables.sql
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Identity database created successfully!" -ForegroundColor Green
        
        # Verify tables were created
        Write-Host "`nVerifying tables..." -ForegroundColor Yellow
        $tables = mysql -u $mysqlUser -p$mysqlPassword -D chatbot_identity -e "SHOW TABLES;" 2>&1
        
        Write-Host "`nTables in chatbot_identity database:" -ForegroundColor Cyan
        Write-Host $tables
        
        Write-Host "`n✓ Setup complete! You can now start the API." -ForegroundColor Green
        Write-Host "`nTo start the API, run:" -ForegroundColor Yellow
        Write-Host "  dotnet run" -ForegroundColor White
    } else {
        Write-Host "✗ Failed to create database" -ForegroundColor Red
        Write-Host "Please check the error message above" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Error running SQL script" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Start the API: dotnet run" -ForegroundColor White
Write-Host "2. Start the Angular app: cd ../../client && npm start" -ForegroundColor White
Write-Host "3. Open browser: http://localhost:4200" -ForegroundColor White
Write-Host "4. Register a new user to test authentication" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan

