# Visual Studio Setup Guide

## ✅ Your Application is Ready!

The Analytics Chatbot API has been successfully configured for Visual Studio. All necessary files have been created and the solution builds successfully.

## 📁 Project Structure

```
C:\projects\AnalyticsChatbot\backend\
├── AnalyticsChatbot.sln           # Solution file - Open this in Visual Studio
├── start-dev.ps1                  # PowerShell script to run from command line
└── AnalyticsChatbot.API\
    ├── AnalyticsChatbot.API.csproj  # Project file
    ├── Program.cs                   # Application entry point
    ├── appsettings.json             # Configuration
    ├── Controllers\                 # API Controllers
    │   ├── ChatController.cs
    │   └── ReportController.cs
    ├── Models\                      # Data models
    │   ├── QueryRequest.cs
    │   └── ReportResult.cs
    ├── Services\                    # Business logic
    │   ├── LlmService.cs
    │   ├── ReportService.cs
    │   └── SqlExecutionService.cs
    ├── Utils\                       # Helper utilities
    │   ├── ExcelHelper.cs
    │   └── PdfHelper.cs
    └── Properties\
        └── launchSettings.json      # Debug settings
```

## 🚀 How to Open in Visual Studio

### Method 1: Double-click the Solution File
1. Navigate to: `C:\projects\AnalyticsChatbot\backend\`
2. Double-click: `AnalyticsChatbot.sln`
3. Visual Studio will open automatically

### Method 2: From Visual Studio
1. Open Visual Studio
2. Click "Open a project or solution"
3. Navigate to: `C:\projects\AnalyticsChatbot\backend\AnalyticsChatbot.sln`
4. Click "Open"

## ▶️ Running the Application

### In Visual Studio:
1. Press `F5` or click the green "Start" button
2. The application will build and launch
3. Your browser will open to: `https://localhost:5001/swagger`
4. Swagger UI will display all available API endpoints

### From Command Line:
```powershell
cd C:\projects\AnalyticsChatbot\backend
.\start-dev.ps1
```

## 🔧 Configuration

### Database Connection
Edit `appsettings.json` and update the connection string:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=YOUR_SERVER;Database=YOUR_DATABASE;Trusted_Connection=True;TrustServerCertificate=True;"
  }
}
```

### OpenAI Integration (Optional)
To enable LLM features, add your API key to `appsettings.json`:

```json
{
  "OpenAI": {
    "ApiKey": "your-api-key-here",
    "Model": "gpt-4"
  }
}
```

## 📡 API Endpoints

Once running, the following endpoints are available:

### Chat Controller
- **POST** `/api/chat/query` - Process natural language queries
- **POST** `/api/chat/validate-sql` - Validate SQL generation

### Report Controller
- **POST** `/api/report/export/excel` - Export data to Excel
- **POST** `/api/report/export/pdf` - Export data to PDF

## 🧪 Testing with Swagger

1. Run the application (F5)
2. Navigate to: `https://localhost:5001/swagger`
3. Expand any endpoint
4. Click "Try it out"
5. Enter test data
6. Click "Execute"

### Example Test Request for `/api/chat/query`:
```json
{
  "query": "show me all users",
  "connectionString": "Server=localhost;Database=TestDB;Trusted_Connection=True;"
}
```

## 📦 NuGet Packages Included

- **Microsoft.AspNetCore.OpenApi** - OpenAPI support
- **Swashbuckle.AspNetCore** - Swagger UI
- **Microsoft.Data.SqlClient** - SQL Server connectivity
- **EPPlus** - Excel file generation
- **itext7** - PDF file generation
- **Newtonsoft.Json** - JSON serialization

## 🔨 Build Status

✅ **Debug Build**: Successful  
✅ **Release Build**: Successful  
✅ **NuGet Packages**: Restored  
✅ **All Files**: Created

## 🎯 Next Steps

1. **Configure your database connection** in `appsettings.json`
2. **Run the application** to verify everything works
3. **Test API endpoints** using Swagger UI
4. **Integrate with LLM** by adding OpenAI API key (optional)
5. **Customize the code** to fit your specific requirements

## 🐛 Troubleshooting

### If Visual Studio doesn't recognize the solution:
- Make sure you have .NET 8.0 SDK installed
- Right-click the solution → "Restore NuGet Packages"
- Clean and rebuild: Build → Clean Solution, then Build → Rebuild Solution

### If the application won't start:
- Check that ports 5000 and 5001 are not in use
- Run as Administrator if SSL certificate issues occur
- Trust the development certificate: `dotnet dev-certs https --trust`

### If database connection fails:
- Verify SQL Server is running
- Check connection string format
- Ensure database exists
- Verify SQL Server allows remote connections

## 📝 Notes

- The LlmService currently uses simple pattern matching. Integrate with OpenAI or Azure OpenAI for production use.
- EPPlus is configured for NonCommercial use. Update license context if needed.
- The application includes CORS policy "AllowAll" for development - restrict this in production.

## 🎉 Success!

Your application is fully configured and ready to use in Visual Studio!

For more details, see the `README.md` file in the AnalyticsChatbot.API directory.

