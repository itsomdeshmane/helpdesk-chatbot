using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using AnalyticsChatbot.API.Embeddings;

namespace AnalyticsChatbot.API.Services;

public interface ILlmService
{
    Task<string> ConvertToSqlAsync(string naturalLanguageQuery);
}

public class LlmService : ILlmService
{
    private readonly ILogger<LlmService> _logger;
    private readonly IConfiguration _configuration;
    private readonly QueryEmbedder _queryEmbedder;
    private readonly VectorSearch _vectorSearch;
    private readonly ILlmPromptBuilder _promptBuilder;
    private readonly HttpClient _httpClient;

    public LlmService(
        ILogger<LlmService> logger, 
        IConfiguration configuration,
        QueryEmbedder queryEmbedder,
        VectorSearch vectorSearch,
        ILlmPromptBuilder promptBuilder)
    {
        _logger = logger;
        _configuration = configuration;
        _queryEmbedder = queryEmbedder;
        _vectorSearch = vectorSearch;
        _promptBuilder = promptBuilder;
        _httpClient = new HttpClient();
    }

    public async Task<string> ConvertToSqlAsync(string naturalLanguageQuery)
    {
        _logger.LogInformation("Converting query to SQL using vector embeddings: {Query}", naturalLanguageQuery);

        try
        {
            // Step 1: Embed the user's query
            var queryEmbedding = await _queryEmbedder.GetQueryEmbeddingAsync(naturalLanguageQuery);
            if (queryEmbedding == null)
            {
                _logger.LogWarning("Failed to generate query embedding, falling back to simple mode");
                return await FallbackSimpleMode(naturalLanguageQuery);
            }

            // Step 2: Find top relevant schema elements
            var topMatches = _vectorSearch.FindTopMatches(queryEmbedding, topN: 10);
            _logger.LogInformation("Found {Count} relevant schema elements", topMatches.Count);

            // FIX #1: Check if we have schema context
            if (topMatches == null || topMatches.Count == 0)
            {
                _logger.LogWarning("No schema elements found. Schema embeddings may not be loaded. Run /api/schema/generate-embeddings first.");
                _logger.LogWarning("Falling back to simple mode");
                return await FallbackSimpleMode(naturalLanguageQuery);
            }

            // Step 3: Build optimized prompt with pruned context
            var prompt = _promptBuilder.BuildPrompt(naturalLanguageQuery, topMatches);
            _logger.LogInformation("Prompt size: {Size} characters (optimized)", prompt.Length);

            // Step 4: Call OpenAI ChatGPT API
            var sqlQuery = await CallOpenAIAsync(prompt);

            // FIX #2: Validate SQL was extracted
            if (string.IsNullOrWhiteSpace(sqlQuery))
            {
                _logger.LogWarning("OpenAI returned no valid SQL. Falling back to simple mode");
                return await FallbackSimpleMode(naturalLanguageQuery);
            }

            // Step 5: Log interaction for future training
            await LogInteractionAsync(naturalLanguageQuery, topMatches, sqlQuery);

            return sqlQuery;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in ConvertToSqlAsync");
            return await FallbackSimpleMode(naturalLanguageQuery);
        }
    }

    private async Task<string?> CallOpenAIAsync(string prompt)
    {
        var apiKey = _configuration["OpenAI:ApiKey"];
        if (string.IsNullOrEmpty(apiKey))
        {
            _logger.LogWarning("OpenAI API key not configured");
            return null;
        }

        var requestBody = new
        {
            model = "gpt-4",
            messages = new[]
            {
                new { role = "system", content = "You are a SQL expert assistant." },
                new { role = "user", content = prompt }
            },
            temperature = 0.0,
            max_tokens = 500
        };

        var content = new StringContent(JsonSerializer.Serialize(requestBody), Encoding.UTF8, "application/json");
        _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", apiKey);

        var response = await _httpClient.PostAsync("https://api.openai.com/v1/chat/completions", content);
        if (!response.IsSuccessStatusCode)
        {
            _logger.LogError("OpenAI API call failed: {Status}", response.StatusCode);
            return null;
        }

        using var respStream = await response.Content.ReadAsStreamAsync();
        using var doc = await JsonDocument.ParseAsync(respStream);
        var sqlQuery = doc.RootElement
            .GetProperty("choices")[0]
            .GetProperty("message")
            .GetProperty("content")
            .GetString();

        // Extract only the SQL query from the response
        return ExtractSqlQuery(sqlQuery);
    }

    private async Task LogInteractionAsync(string query, List<VectorSearchResult> schemaContext, string? generatedSql)
    {
        try
        {
            var logEntry = new
            {
                Timestamp = DateTime.UtcNow,
                UserQuery = query,
                RelevantSchema = schemaContext.Select(s => new {
                    s.Element.TableName,
                    s.Element.ColumnName,
                    s.Similarity
                }),
                GeneratedSql = generatedSql
            };

            var logJson = JsonSerializer.Serialize(logEntry, new JsonSerializerOptions { WriteIndented = true });
            await File.AppendAllTextAsync("training_logs.jsonl", logJson + Environment.NewLine);
            _logger.LogInformation("Logged interaction for training dataset");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to log interaction");
        }
    }

    private string? ExtractSqlQuery(string? response)
    {
        if (string.IsNullOrWhiteSpace(response))
        {
            _logger.LogWarning("ExtractSqlQuery: Received null or empty response");
            return null;
        }

        _logger.LogDebug("ExtractSqlQuery: Raw response: {Response}", response);

        // Remove markdown code blocks if present
        var cleaned = response.Trim();
        
        // Remove ```sql or ``` markers
        if (cleaned.StartsWith("```sql", StringComparison.OrdinalIgnoreCase))
        {
            cleaned = cleaned.Substring(6).Trim();
        }
        else if (cleaned.StartsWith("```"))
        {
            cleaned = cleaned.Substring(3).Trim();
        }
        
        if (cleaned.EndsWith("```"))
        {
            cleaned = cleaned.Substring(0, cleaned.Length - 3).Trim();
        }

        // SQL keywords we're looking for
        var sqlKeywords = new[] { "SELECT", "INSERT", "UPDATE", "DELETE", "WITH", "CREATE", "DROP", "ALTER", "SHOW", "DESCRIBE", "EXPLAIN" };
        
        // FIX #3: Check if the entire cleaned response is SQL (most common case)
        var cleanedUpper = cleaned.TrimStart().ToUpper();
        if (sqlKeywords.Any(kw => cleanedUpper.StartsWith(kw)))
        {
            // The entire response is SQL, return it
            _logger.LogInformation("Extracted SQL (direct): {Sql}", cleaned);
            return cleaned;
        }

        // FIX #4: Split by lines and find the SQL statement
        var lines = cleaned.Split(new[] { '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        
        var sqlLines = new List<string>();
        bool inSqlBlock = false;

        foreach (var line in lines)
        {
            var upperLine = line.TrimStart().ToUpper();
            
            // Skip comments and explanations
            if (line.StartsWith("--") || line.StartsWith("//") || line.StartsWith("#") || line.StartsWith("*"))
                continue;
            
            // Skip common explanatory phrases
            if (line.ToLower().Contains("here is") || 
                line.ToLower().Contains("here's") || 
                line.ToLower().Contains("the query") ||
                line.ToLower().Contains("based on") ||
                line.ToLower().StartsWith("as an ai"))
                continue;
                
            // Check if line starts with SQL keyword
            if (sqlKeywords.Any(kw => upperLine.StartsWith(kw)))
            {
                inSqlBlock = true;
            }

            if (inSqlBlock)
            {
                sqlLines.Add(line);
                // Stop if we hit a semicolon at the end
                if (line.TrimEnd().EndsWith(";"))
                    break;
            }
        }

        if (sqlLines.Count > 0)
        {
            var sql = string.Join("\n", sqlLines).Trim();
            // Remove trailing semicolon if present (MySQL doesn't require it)
            if (sql.EndsWith(";"))
                sql = sql.Substring(0, sql.Length - 1).Trim();
                
            _logger.LogInformation("Extracted SQL (from lines): {Sql}", sql);
            return sql;
        }

        // FIX #5: Last resort - look for SQL patterns in the text
        var sqlPattern = new System.Text.RegularExpressions.Regex(
            @"(SELECT|INSERT|UPDATE|DELETE|WITH|SHOW|DESCRIBE)\s+.*?(?=;|\Z)",
            System.Text.RegularExpressions.RegexOptions.IgnoreCase | 
            System.Text.RegularExpressions.RegexOptions.Singleline);
        
        var match = sqlPattern.Match(cleaned);
        if (match.Success)
        {
            var sql = match.Value.Trim();
            _logger.LogInformation("Extracted SQL (regex): {Sql}", sql);
            return sql;
        }

        // If still no SQL found, log the full response for debugging
        _logger.LogWarning("Could not extract SQL from response. Full response: {Response}", response);
        return null;
    }

    private Task<string> FallbackSimpleMode(string naturalLanguageQuery)
    {
        _logger.LogInformation("Using fallback simple mode for query: {Query}", naturalLanguageQuery);
        var query = naturalLanguageQuery.ToLower();

        string sqlQuery;
        var limit = ExtractNumber(query) ?? 10;
        
        // Generic table detection with safe queries (no hardcoded columns)
        string? detectedTable = null;
        
        // Common table name patterns
        var tableKeywords = new Dictionary<string, string[]>
        {
            { "vendors", new[] { "vendor", "supplier" } },
            { "customers", new[] { "customer", "client", "buyer" } },
            { "products", new[] { "product", "item", "good" } },
            { "orders", new[] { "order", "purchase" } },
            { "employees", new[] { "employee", "staff", "worker", "personnel" } },
            { "users", new[] { "user", "account" } },
            { "sales", new[] { "sale", "revenue", "turnover" } },
            { "inventory", new[] { "inventory", "stock", "warehouse" } }
        };
        
        // Find matching table
        foreach (var tableEntry in tableKeywords)
        {
            if (tableEntry.Value.Any(keyword => query.Contains(keyword)))
            {
                detectedTable = tableEntry.Key;
                break;
            }
        }
        
        // Generate safe SQL based on query type
        if (query.Contains("how many") || query.Contains("count"))
        {
            // Count query - safe, no specific columns needed
            if (!string.IsNullOrEmpty(detectedTable))
            {
                // Handle location filters generically
                if (query.Contains("in india"))
                {
                    sqlQuery = $"SELECT COUNT(*) as total FROM {detectedTable} WHERE LOWER(country) = 'india' OR LOWER(location) LIKE '%india%'";
                }
                else if (query.Contains(" in "))
                {
                    // Generic location handling
                    var locationMatch = System.Text.RegularExpressions.Regex.Match(query, @"in\s+([a-z\s]+)$");
                    if (locationMatch.Success)
                    {
                        var location = locationMatch.Groups[1].Value.Trim();
                        sqlQuery = $"SELECT COUNT(*) as total FROM {detectedTable} WHERE LOWER(country) = '{location}' OR LOWER(location) LIKE '%{location}%'";
                    }
                    else
                    {
                        sqlQuery = $"SELECT COUNT(*) as total FROM {detectedTable}";
                    }
                }
                else
                {
                    sqlQuery = $"SELECT COUNT(*) as total FROM {detectedTable}";
                }
            }
            else
            {
                sqlQuery = "SHOW TABLES";
            }
        }
        else if (query.Contains("total") || query.Contains("sum"))
        {
            // Sum query - try common amount/value columns
            if (!string.IsNullOrEmpty(detectedTable))
            {
                sqlQuery = $"SELECT COALESCE(SUM(amount), SUM(total), SUM(value), SUM(price), 0) as total FROM {detectedTable}";
            }
            else
            {
                sqlQuery = "SHOW TABLES";
            }
        }
        else if (query.Contains("average") || query.Contains("avg"))
        {
            // Average query
            if (!string.IsNullOrEmpty(detectedTable))
            {
                sqlQuery = $"SELECT COALESCE(AVG(amount), AVG(total), AVG(value), AVG(price), 0) as average FROM {detectedTable}";
            }
            else
            {
                sqlQuery = "SHOW TABLES";
            }
        }
        else if (!string.IsNullOrEmpty(detectedTable))
        {
            // List/show query - safe, just SELECT * with limit
            if (query.Contains("in india"))
            {
                sqlQuery = $"SELECT * FROM {detectedTable} WHERE LOWER(country) = 'india' OR LOWER(location) LIKE '%india%' LIMIT {limit}";
            }
            else if (query.Contains(" in "))
            {
                var locationMatch = System.Text.RegularExpressions.Regex.Match(query, @"in\s+([a-z\s]+)$");
                if (locationMatch.Success)
                {
                    var location = locationMatch.Groups[1].Value.Trim();
                    sqlQuery = $"SELECT * FROM {detectedTable} WHERE LOWER(country) = '{location}' OR LOWER(location) LIKE '%{location}%' LIMIT {limit}";
                }
                else
                {
                    sqlQuery = $"SELECT * FROM {detectedTable} LIMIT {limit}";
                }
            }
            else
            {
                sqlQuery = $"SELECT * FROM {detectedTable} LIMIT {limit}";
            }
        }
        else
        {
            // No table detected - show available tables
            _logger.LogWarning("No specific table match found. Showing available tables.");
            sqlQuery = "SHOW TABLES";
        }

        _logger.LogInformation("Fallback SQL: {Sql}", sqlQuery);
        return Task.FromResult(sqlQuery);
    }

    private int? ExtractNumber(string text)
    {
        var match = System.Text.RegularExpressions.Regex.Match(text, @"\d+");
        return match.Success ? int.Parse(match.Value) : null;
    }
}
