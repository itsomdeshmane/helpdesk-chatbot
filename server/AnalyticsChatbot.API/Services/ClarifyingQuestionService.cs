using AnalyticsChatbot.API.Models;
using Microsoft.EntityFrameworkCore;

namespace AnalyticsChatbot.API.Services;

public interface IClarifyingQuestionService
{
    Task<string?> GenerateClarifyingQuestionAsync(string userQuery, string userId, string sessionId, List<string>? availableTables = null);
    bool ShouldAskClarifyingQuestion(string userQuery, List<KnowledgeBase> searchResults);
}

public class ClarifyingQuestionService : IClarifyingQuestionService
{
    private readonly AppDbContext _dbContext;
    private readonly IKeywordExtractorService _keywordExtractor;
    private readonly ILogger<ClarifyingQuestionService> _logger;

    public ClarifyingQuestionService(
        AppDbContext dbContext,
        IKeywordExtractorService keywordExtractor,
        ILogger<ClarifyingQuestionService> logger)
    {
        _dbContext = dbContext;
        _keywordExtractor = keywordExtractor;
        _logger = logger;
    }

    public bool ShouldAskClarifyingQuestion(string userQuery, List<KnowledgeBase> searchResults)
    {
        // No results found
        if (!searchResults.Any())
        {
            return true;
        }
        
        // Low confidence in top result
        var keywords = _keywordExtractor.ExtractKeywords(userQuery);
        if (keywords.Count < 2)
        {
            return true; // Query too vague
        }
        
        // Multiple similar results (ambiguous query)
        if (searchResults.Count >= 3)
        {
            return true;
        }
        
        return false;
    }

    public async Task<string?> GenerateClarifyingQuestionAsync(string userQuery, string userId, string sessionId, List<string>? availableTables = null)
    {
        _logger.LogInformation("Generating clarifying question for: {Query}", userQuery);
        
        // Analyze the query to understand what's missing
        var keywords = _keywordExtractor.ExtractKeywords(userQuery);
        var missingContext = await AnalyzeMissingContext(userQuery, keywords);
        
        string clarifyingQuestion;
        
        if (missingContext.NeedsTimeframe)
        {
            clarifyingQuestion = $"I'd like to help you with information about {missingContext.Subject}. " +
                                "Could you please specify the time period you're interested in? " +
                                "(e.g., this month, last quarter, specific date range)";
        }
        else if (missingContext.NeedsLocation)
        {
            clarifyingQuestion = $"I found some information about {missingContext.Subject}. " +
                                "Could you please specify the location or region you're asking about?";
        }
        else if (missingContext.NeedsCategory)
        {
            clarifyingQuestion = $"I have information about {missingContext.Subject}. " +
                                "Could you please specify which category or type you're interested in?";
        }
        else if (missingContext.MultipleOptions != null && missingContext.MultipleOptions.Any())
        {
            var options = string.Join(", ", missingContext.MultipleOptions.Select((o, i) => $"{i + 1}. {o}"));
            clarifyingQuestion = $"I found multiple related topics. Which one are you asking about?\n{options}";
        }
        else if (availableTables != null && availableTables.Any() && keywords.Count >= 1)
        {
            // Suggest available tables based on keyword match
            var suggestedTables = availableTables
                .Where(t => keywords.Any(k => t.ToLower().Contains(k.ToLower()) || k.ToLower().Contains(t.ToLower())))
                .Take(5)
                .ToList();
            
            if (suggestedTables.Any())
            {
                var tableList = string.Join(", ", suggestedTables.Select((t, i) => $"{i + 1}. {FormatTableName(t)}"));
                clarifyingQuestion = $"I found these data sources that might be relevant:\n{tableList}\n\n" +
                                    "Which one would you like me to query?";
            }
            else if (availableTables.Count > 0 && availableTables.Count <= 10)
            {
                var allTables = string.Join(", ", availableTables.Select((t, i) => $"{i + 1}. {FormatTableName(t)}").Take(10));
                clarifyingQuestion = $"I have access to these data sources:\n{allTables}\n\n" +
                                    "Which one contains the information you're looking for?";
            }
            else
            {
                clarifyingQuestion = $"I have access to {availableTables.Count} data sources. " +
                                    "Could you please be more specific about what kind of data you're looking for? " +
                                    "(e.g., customers, products, orders, employees, sales, etc.)";
            }
        }
        else if (keywords.Count < 2)
        {
            clarifyingQuestion = "Could you please provide more details about what you're looking for? " +
                                "This will help me give you a more accurate answer.";
        }
        else
        {
            // Find related topics in knowledge base
            var relatedTopics = await FindRelatedTopics(keywords);
            
            if (relatedTopics.Any())
            {
                var topics = string.Join(", ", relatedTopics.Select((t, i) => $"{i + 1}. {t}"));
                clarifyingQuestion = $"I couldn't find an exact match, but I have information on these related topics:\n{topics}\n\n" +
                                    "Which one would you like to know about?";
            }
            else
            {
                clarifyingQuestion = "I don't have specific information about that yet. " +
                                    "Could you rephrase your question or provide more context? " +
                                    "For example, are you asking about specific data, reports, or analytics?";
            }
        }
        
        // Save clarifying question to conversation history
        await SaveClarifyingQuestion(userId, sessionId, userQuery, clarifyingQuestion);
        
        return clarifyingQuestion;
    }

    private string FormatTableName(string tableName)
    {
        // Convert table names to user-friendly format
        // e.g., "customer_orders" -> "Customer Orders"
        return string.Join(" ", tableName.Split('_'))
            .Replace("_", " ")
            .ToLower()
            .Split(' ')
            .Select(word => char.ToUpper(word[0]) + word.Substring(1))
            .Aggregate((a, b) => a + " " + b);
    }

    private async Task<MissingContext> AnalyzeMissingContext(string userQuery, List<string> keywords)
    {
        var context = new MissingContext
        {
            Subject = keywords.FirstOrDefault() ?? "that"
        };
        
        var queryLower = userQuery.ToLower();
        
        // Check for time-related queries without specific timeframe
        var hasTimeQuery = queryLower.Contains("when") || queryLower.Contains("recent") || 
                          queryLower.Contains("latest") || queryLower.Contains("current");
        var hasTimeframe = queryLower.Contains("month") || queryLower.Contains("year") || 
                          queryLower.Contains("quarter") || queryLower.Contains("day") ||
                          queryLower.Contains("today") || queryLower.Contains("yesterday");
        
        if (hasTimeQuery && !hasTimeframe)
        {
            context.NeedsTimeframe = true;
        }
        
        // Check for location-related queries without specific location
        var hasLocationQuery = queryLower.Contains("where") || queryLower.Contains("location");
        var hasLocation = System.Text.RegularExpressions.Regex.IsMatch(queryLower, 
            @"\b(in|at|from)\s+[a-z]+\b");
        
        if (hasLocationQuery && !hasLocation)
        {
            context.NeedsLocation = true;
        }
        
        // Check for category/type queries
        var hasCategoryQuery = queryLower.Contains("which") || queryLower.Contains("what kind") || 
                              queryLower.Contains("what type");
        
        if (hasCategoryQuery)
        {
            context.NeedsCategory = true;
            
            // Try to find available categories
            context.MultipleOptions = await FindAvailableCategories(keywords);
        }
        
        return context;
    }

    private async Task<List<string>> FindRelatedTopics(List<string> keywords)
    {
        var relatedTopics = new List<string>();
        
        try
        {
            var knowledge = await _dbContext.KnowledgeBases
                .Where(kb => kb.Keywords != null)
                .ToListAsync();
            
            foreach (var kb in knowledge)
            {
                var kbKeywords = kb.Keywords?.Split(',', StringSplitOptions.RemoveEmptyEntries)
                    .Select(k => k.Trim())
                    .ToList() ?? new List<string>();
                
                // Check if any keyword matches
                if (keywords.Any(kw => kbKeywords.Any(kbk => 
                    kbk.Equals(kw, StringComparison.OrdinalIgnoreCase))))
                {
                    // Extract a short topic description from the question
                    var topic = ExtractTopicFromQuestion(kb.Question);
                    if (!relatedTopics.Contains(topic))
                    {
                        relatedTopics.Add(topic);
                    }
                }
                
                if (relatedTopics.Count >= 5)
                    break;
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error finding related topics");
        }
        
        return relatedTopics;
    }

    private async Task<List<string>> FindAvailableCategories(List<string> keywords)
    {
        var categories = new List<string>();
        
        try
        {
            var knowledge = await _dbContext.KnowledgeBases
                .Where(kb => kb.Category != null)
                .Select(kb => kb.Category)
                .Distinct()
                .ToListAsync();
            
            return knowledge.Where(c => c != null).Cast<string>().Take(5).ToList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error finding categories");
        }
        
        return categories;
    }

    private string ExtractTopicFromQuestion(string question)
    {
        // Extract first 50 characters as topic or until first question mark/period
        var topic = question.Length > 50 ? question.Substring(0, 50) + "..." : question;
        
        var endIndex = Math.Min(
            question.IndexOf('?') > 0 ? question.IndexOf('?') : question.Length,
            question.IndexOf('.') > 0 ? question.IndexOf('.') : question.Length
        );
        
        if (endIndex < question.Length && endIndex < 60)
        {
            topic = question.Substring(0, endIndex);
        }
        
        return topic.Trim();
    }

    private async Task SaveClarifyingQuestion(string userId, string sessionId, string userQuery, string clarifyingQuestion)
    {
        try
        {
            var conversation = new ConversationHistory
            {
                UserId = userId,
                SessionId = sessionId,
                Message = clarifyingQuestion,
                Role = "assistant",
                IsClarity = true,
                Timestamp = DateTime.UtcNow,
                Context = System.Text.Json.JsonSerializer.Serialize(new { OriginalQuery = userQuery })
            };
            
            _dbContext.ConversationHistories.Add(conversation);
            
            // Update context to mark pending clarification
            var context = await _dbContext.ConversationContexts
                .FirstOrDefaultAsync(c => c.SessionId == sessionId && c.UserId == userId);
            
            if (context == null)
            {
                context = new ConversationContext
                {
                    SessionId = sessionId,
                    UserId = userId,
                    PendingClarification = userQuery,
                    LastActivity = DateTime.UtcNow
                };
                _dbContext.ConversationContexts.Add(context);
            }
            else
            {
                context.PendingClarification = userQuery;
                context.LastActivity = DateTime.UtcNow;
            }
            
            await _dbContext.SaveChangesAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error saving clarifying question");
        }
    }

    private class MissingContext
    {
        public string Subject { get; set; } = string.Empty;
        public bool NeedsTimeframe { get; set; }
        public bool NeedsLocation { get; set; }
        public bool NeedsCategory { get; set; }
        public List<string>? MultipleOptions { get; set; }
    }
}

