# Development startup script for Analytics Chatbot API
Write-Host "Starting Analytics Chatbot API..." -ForegroundColor Green

# Navigate to the API directory
Set-Location -Path $PSScriptRoot

# Restore packages
Write-Host "`nRestoring NuGet packages..." -ForegroundColor Yellow
dotnet restore

# Build the solution
Write-Host "`nBuilding the solution..." -ForegroundColor Yellow
dotnet build

# Run the application
Write-Host "`nStarting the application..." -ForegroundColor Yellow
Write-Host "Navigate to: http://localhost:5000/swagger" -ForegroundColor Cyan
Write-Host "or https://localhost:5001/swagger" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop the application" -ForegroundColor Gray
dotnet run --project AnalyticsChatbot.API

