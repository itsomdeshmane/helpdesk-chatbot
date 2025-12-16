using System.Text.RegularExpressions;
using System.Text.Json;

namespace AnalyticsChatbot.API.Services;

public interface IResponseFormatAnalyzer
{
    string DetermineResponseFormat(string userQuery, int resultCount, int columnCount);
}

public class ResponseFormatAnalyzer : IResponseFormatAnalyzer
{
    private readonly ILogger<ResponseFormatAnalyzer> _logger;
    private readonly FormatKeywords _keywords;

    public ResponseFormatAnalyzer(ILogger<ResponseFormatAnalyzer> logger)
    {
        _logger = logger;
        _keywords = LoadKeywords();
    }

    private FormatKeywords LoadKeywords()
    {
        try
        {
            var jsonPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "response_format_keywords.json");
            if (File.Exists(jsonPath))
            {
                var jsonContent = File.ReadAllText(jsonPath);
                var keywords = JsonSerializer.Deserialize<FormatKeywords>(jsonContent, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });
                
                if (keywords != null)
                {
                    _logger.LogInformation("Loaded format keywords from JSON configuration");
                    return keywords;
                }
            }
            
            _logger.LogWarning("Keywords JSON file not found, using default keywords");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error loading keywords from JSON, using defaults");
        }

        // Return default keywords if loading fails
        return GetDefaultKeywords();
    }

    private FormatKeywords GetDefaultKeywords()
    {
        return new FormatKeywords
        {
            GridKeywords = new[] { "show table", "in a table", "as a table", "tabular format", "grid format", "compare", "comparison", "show all columns", "show all fields", "detailed view" },
            ListKeywords = new[] { "list", "list all", "list of", "show names", "show titles", "give me names", "what are the names", "enumerate" },
            AggregateKeywords = new[] { "how many", "count", "total", "sum", "average", "avg", "maximum", "max", "minimum", "min", "median" },
            SingleAnswerPatterns = new[] { "what is", "what's", "who is", "who's", "when was", "when is", "where is", "which is", "how much", "is there", "are there" },
            ListOrientedKeywords = new[] { "list", "names", "titles", "all the", "which", "what are", "show me the" }
        };
    }

    private class FormatKeywords
    {
        public string[] GridKeywords { get; set; } = Array.Empty<string>();
        public string[] ListKeywords { get; set; } = Array.Empty<string>();
        public string[] AggregateKeywords { get; set; } = Array.Empty<string>();
        public string[] SingleAnswerPatterns { get; set; } = Array.Empty<string>();
        public string[] ListOrientedKeywords { get; set; } = Array.Empty<string>();
    }

    public string DetermineResponseFormat(string userQuery, int resultCount, int columnCount)
    {
        var query = userQuery.ToLower().Trim();
        
        _logger.LogInformation("Analyzing query for response format: {Query}, Results: {Count}, Columns: {Columns}", 
            userQuery, resultCount, columnCount);

        // Priority 1: Check for explicit user preference in query
        if (ContainsGridKeywords(query))
        {
            _logger.LogInformation("Format: GRID (explicit grid keywords detected)");
            return "grid";
        }

        if (ContainsListKeywords(query))
        {
            _logger.LogInformation("Format: LIST (explicit list keywords detected)");
            return "list";
        }

        // Priority 2: Single value results should be plain sentence
        if (resultCount == 1 && columnCount == 1)
        {
            _logger.LogInformation("Format: SENTENCE (single value result)");
            return "sentence";
        }

        // Priority 3: Aggregate queries (count, sum, average, etc.) -> Sentence
        if (ContainsAggregateKeywords(query))
        {
            _logger.LogInformation("Format: SENTENCE (aggregate query detected)");
            return "sentence";
        }

        // Priority 4: Questions asking for single information -> Sentence
        if (ContainsSingleAnswerQuestions(query))
        {
            _logger.LogInformation("Format: SENTENCE (single answer question)");
            return "sentence";
        }

        // Priority 5: Single column with multiple rows -> List
        if (columnCount == 1 && resultCount > 1)
        {
            _logger.LogInformation("Format: LIST (single column, multiple rows)");
            return "list";
        }

        // Priority 6: List-oriented queries with results -> List (unless only 1 result)
        if (ContainsListOrientedKeywords(query) && resultCount > 1)
        {
            _logger.LogInformation("Format: LIST (list-oriented query with multiple results)");
            return "list";
        }

        // Priority 7: Multiple columns or complex data -> Grid
        if (columnCount > 2 && resultCount > 3)
        {
            _logger.LogInformation("Format: GRID (multiple columns and many results)");
            return "grid";
        }

        // Priority 8: Multiple results with few columns -> Sentence with structured data
        if (resultCount > 1 && columnCount <= 2)
        {
            _logger.LogInformation("Format: SENTENCE (multiple results, simple structure)");
            return "sentence";
        }

        // Default: Sentence for most queries
        _logger.LogInformation("Format: SENTENCE (default)");
        return "sentence";
    }

    private bool ContainsGridKeywords(string query)
    {
        return _keywords.GridKeywords.Any(keyword => query.Contains(keyword));
    }

    private bool ContainsListKeywords(string query)
    {
        return _keywords.ListKeywords.Any(keyword => query.Contains(keyword));
    }

    private bool ContainsAggregateKeywords(string query)
    {
        return _keywords.AggregateKeywords.Any(keyword => query.Contains(keyword));
    }

    private bool ContainsSingleAnswerQuestions(string query)
    {
        return _keywords.SingleAnswerPatterns.Any(pattern => query.Contains(pattern));
    }

    private bool ContainsListOrientedKeywords(string query)
    {
        return _keywords.ListOrientedKeywords.Any(keyword => query.Contains(keyword));
    }
}

