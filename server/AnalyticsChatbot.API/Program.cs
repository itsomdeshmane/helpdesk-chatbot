using System.Text;
using AnalyticsChatbot.API.Services;
using AnalyticsChatbot.API.Embeddings;
using AnalyticsChatbot.API.Models;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Register application services
builder.Services.AddScoped<ILlmService, LlmService>();
builder.Services.AddScoped<ISqlExecutionService, SqlExecutionService>();
builder.Services.AddScoped<IReportService, ReportService>();
builder.Services.AddScoped<ILlmPromptBuilder, LlmPromptBuilder>();
builder.Services.AddScoped<IResponseFormatAnalyzer, ResponseFormatAnalyzer>();
builder.Services.AddScoped<INaturalLanguageGenerator, NaturalLanguageGenerator>();
builder.Services.AddScoped<IChatSessionService, ChatSessionService>();

// Register RAG and Smart Chat services
builder.Services.AddScoped<IKeywordExtractorService, KeywordExtractorService>();
builder.Services.AddScoped<IRagService, RagService>();
builder.Services.AddScoped<IClarifyingQuestionService, ClarifyingQuestionService>();
builder.Services.AddScoped<IConversationContextService, ConversationContextService>();
builder.Services.AddScoped<IGenericSchemaService, GenericSchemaService>();

// Register embedding and vector search services
builder.Services.AddSingleton<QueryEmbedder>();
builder.Services.AddSingleton<VectorSearch>(sp =>
{
    var vectorSearch = new VectorSearch();
    // Load embeddings on startup if file exists
    try
    {
        vectorSearch.LoadEmbeddingsAsync().Wait();
    }
    catch (Exception ex)
    {
        var logger = sp.GetRequiredService<ILogger<Program>>();
        logger.LogWarning(ex, "Could not load schema embeddings on startup. Please generate embeddings first.");
    }
    return vectorSearch;
});

// Register Identity and DbContext (separate databases)
// Identity Database - for user authentication
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseMySQL(builder.Configuration.GetConnectionString("IdentityConnection") 
        ?? throw new InvalidOperationException("IdentityConnection not configured")));

builder.Services.AddIdentity<IdentityUser, IdentityRole>(options =>
{
    // Password settings
    options.Password.RequireDigit = false;
    options.Password.RequireLowercase = false;
    options.Password.RequireNonAlphanumeric = false;
    options.Password.RequireUppercase = false;
    options.Password.RequiredLength = 6;
    options.Password.RequiredUniqueChars = 0;
    
    // User settings
    options.User.RequireUniqueEmail = true;
})
    .AddEntityFrameworkStores<AppDbContext>()
    .AddDefaultTokenProviders();

// Configure JWT Settings
builder.Services.Configure<JwtSettings>(builder.Configuration.GetSection("JwtSettings"));

// Add JWT Authentication
var jwtSettings = builder.Configuration.GetSection("JwtSettings").Get<JwtSettings>();
if (jwtSettings != null)
{
    builder.Services.AddAuthentication(options =>
    {
        options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
        options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
        options.DefaultScheme = JwtBearerDefaults.AuthenticationScheme;
    })
    .AddJwtBearer(options =>
    {
        options.SaveToken = true;
        options.RequireHttpsMetadata = false; // Set to true in production
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = jwtSettings.Issuer,
            ValidAudience = jwtSettings.Audience,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSettings.SecretKey)),
            ClockSkew = TimeSpan.Zero // Remove default 5 minute clock skew
        };
    });
}

// Register JWT Token Service
builder.Services.AddScoped<IJwtTokenService, JwtTokenService>();

// Application Database - for ERP data (erp_demo)
// This connection is used by SqlExecutionService and SchemaExtractor

// Add CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll",
        builder =>
        {
            builder.AllowAnyOrigin()
                   .AllowAnyMethod()
                   .AllowAnyHeader();
        });
});

var app = builder.Build();

// Ensure Identity database is created
using (var scope = app.Services.CreateScope())
{
    var services = scope.ServiceProvider;
    try
    {
        var context = services.GetRequiredService<AppDbContext>();
        var logger = services.GetRequiredService<ILogger<Program>>();
        
        // Ensure database is created
        context.Database.EnsureCreated();
        logger.LogInformation("Identity database initialized successfully");
    }
    catch (Exception ex)
    {
        var logger = services.GetRequiredService<ILogger<Program>>();
        logger.LogError(ex, "An error occurred while initializing the Identity database");
    }
}

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.UseCors("AllowAll");

app.UseAuthentication();

app.UseAuthorization();

app.MapControllers();

app.Run();

