using AnalyticsChatbot.API.Models;
using AnalyticsChatbot.API.Embeddings;
using Microsoft.EntityFrameworkCore;
using System.Text.Json;

namespace AnalyticsChatbot.API.Services;

public interface IRagService
{
    Task<string> GetAnswerAsync(string question, string userId, string sessionId);
    Task<bool> AddToKnowledgeBaseAsync(string question, string answer, string? category = null);
    Task<List<KnowledgeBase>> SearchKnowledgeBaseAsync(string query, int topK = 5);
}

public class RagService : IRagService
{
    private readonly AppDbContext _dbContext;
    private readonly IKeywordExtractorService _keywordExtractor;
    private readonly ILogger<RagService> _logger;
    private readonly QueryEmbedder _embedder;

    public RagService(
        AppDbContext dbContext,
        IKeywordExtractorService keywordExtractor,
        QueryEmbedder embedder,
        ILogger<RagService> logger)
    {
        _dbContext = dbContext;
        _keywordExtractor = keywordExtractor;
        _embedder = embedder;
        _logger = logger;
    }

    public async Task<string> GetAnswerAsync(string question, string userId, string sessionId)
    {
        _logger.LogInformation("RAG: Searching for answer to: {Question}", question);
        
        // Extract keywords from question
        var keywords = _keywordExtractor.ExtractKeywords(question);
        var keywordsStr = string.Join(",", keywords.Take(5));
        
        // Save user question to conversation history
        await SaveConversationAsync(userId, sessionId, question, "user", keywordsStr);
        
        // Search knowledge base using multiple strategies
        var results = await SearchKnowledgeBaseAsync(question, topK: 5);
        
        if (results.Any())
        {
            var bestMatch = results.First();
            
            // Update usage statistics
            bestMatch.UsageCount++;
            bestMatch.UpdatedAt = DateTime.UtcNow;
            await _dbContext.SaveChangesAsync();
            
            // Save assistant response to conversation history
            await SaveConversationAsync(userId, sessionId, bestMatch.Answer, "assistant", 
                keywordsStr, confidenceScore: CalculateConfidence(question, bestMatch));
            
            _logger.LogInformation("RAG: Found answer with confidence: {Confidence}", 
                CalculateConfidence(question, bestMatch));
            
            return bestMatch.Answer;
        }
        
        _logger.LogWarning("RAG: No answer found in knowledge base");
        return string.Empty;
    }

    public async Task<List<KnowledgeBase>> SearchKnowledgeBaseAsync(string query, int topK = 5)
    {
        _logger.LogInformation("RAG: Searching knowledge base for: {Query}", query);
        
        // Strategy 1: Keyword-based search
        var keywordResults = await SearchByKeywords(query, topK * 2);
        
        // Strategy 2: Semantic similarity using embeddings
        var semanticResults = await SearchBySemanticSimilarity(query, topK * 2);
        
        // Combine and rank results
        var combinedResults = CombineAndRankResults(keywordResults, semanticResults, query);
        
        return combinedResults.Take(topK).ToList();
    }

    private async Task<List<(KnowledgeBase kb, float score)>> SearchByKeywords(string query, int topK)
    {
        var queryKeywords = _keywordExtractor.ExtractKeywords(query).Take(10).ToList();
        
        if (!queryKeywords.Any())
        {
            return new List<(KnowledgeBase, float)>();
        }
        
        var allKnowledge = await _dbContext.KnowledgeBases.ToListAsync();
        var scoredResults = new List<(KnowledgeBase kb, float score)>();
        
        foreach (var kb in allKnowledge)
        {
            var kbKeywords = kb.Keywords?.Split(',', StringSplitOptions.RemoveEmptyEntries)
                .Select(k => k.Trim())
                .ToList() ?? new List<string>();
            
            // Calculate keyword overlap
            var matchCount = queryKeywords.Count(qk => 
                kbKeywords.Any(kk => kk.Equals(qk, StringComparison.OrdinalIgnoreCase)));
            
            if (matchCount > 0)
            {
                var score = (float)matchCount / queryKeywords.Count;
                scoredResults.Add((kb, score));
            }
        }
        
        return scoredResults.OrderByDescending(r => r.score).Take(topK).ToList();
    }

    private async Task<List<(KnowledgeBase kb, float score)>> SearchBySemanticSimilarity(string query, int topK)
    {
        try
        {
            var queryEmbedding = await _embedder.GetQueryEmbeddingAsync(query);
            if (queryEmbedding == null)
            {
                return new List<(KnowledgeBase, float)>();
            }
            
            var allKnowledge = await _dbContext.KnowledgeBases
                .Where(kb => kb.Embedding != null)
                .ToListAsync();
            
            var scoredResults = new List<(KnowledgeBase kb, float score)>();
            
            foreach (var kb in allKnowledge)
            {
                if (string.IsNullOrWhiteSpace(kb.Embedding))
                    continue;
                
                var kbEmbedding = JsonSerializer.Deserialize<float[]>(kb.Embedding);
                if (kbEmbedding == null)
                    continue;
                
                var similarity = CosineSimilarity(queryEmbedding, kbEmbedding);
                scoredResults.Add((kb, similarity));
            }
            
            return scoredResults.OrderByDescending(r => r.score).Take(topK).ToList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in semantic similarity search");
            return new List<(KnowledgeBase, float)>();
        }
    }

    private List<KnowledgeBase> CombineAndRankResults(
        List<(KnowledgeBase kb, float score)> keywordResults,
        List<(KnowledgeBase kb, float score)> semanticResults,
        string query)
    {
        var combinedScores = new Dictionary<int, (KnowledgeBase kb, float totalScore)>();
        
        // Add keyword results with weight
        foreach (var (kb, score) in keywordResults)
        {
            if (!combinedScores.ContainsKey(kb.Id))
            {
                combinedScores[kb.Id] = (kb, score * 0.6f); // 60% weight for keywords
            }
            else
            {
                var current = combinedScores[kb.Id];
                combinedScores[kb.Id] = (current.kb, current.totalScore + score * 0.6f);
            }
        }
        
        // Add semantic results with weight
        foreach (var (kb, score) in semanticResults)
        {
            if (!combinedScores.ContainsKey(kb.Id))
            {
                combinedScores[kb.Id] = (kb, score * 0.4f); // 40% weight for semantics
            }
            else
            {
                var current = combinedScores[kb.Id];
                combinedScores[kb.Id] = (current.kb, current.totalScore + score * 0.4f);
            }
        }
        
        return combinedScores.Values
            .OrderByDescending(v => v.totalScore)
            .Select(v => v.kb)
            .ToList();
    }

    public async Task<bool> AddToKnowledgeBaseAsync(string question, string answer, string? category = null)
    {
        try
        {
            var keywords = _keywordExtractor.ExtractKeywords(question + " " + answer);
            var keywordsStr = string.Join(",", keywords.Take(10));
            
            // Generate embedding for the question
            var embedding = await _embedder.GetQueryEmbeddingAsync(question);
            var embeddingJson = embedding != null ? JsonSerializer.Serialize(embedding) : null;
            
            var kb = new KnowledgeBase
            {
                Question = question,
                Answer = answer,
                Keywords = keywordsStr,
                Category = category,
                Embedding = embeddingJson,
                CreatedAt = DateTime.UtcNow
            };
            
            _dbContext.KnowledgeBases.Add(kb);
            await _dbContext.SaveChangesAsync();
            
            _logger.LogInformation("Added new knowledge to base: {Question}", question);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding to knowledge base");
            return false;
        }
    }

    private async Task SaveConversationAsync(
        string userId, 
        string sessionId, 
        string message, 
        string role,
        string? keywords = null,
        float? confidenceScore = null)
    {
        var conversation = new ConversationHistory
        {
            UserId = userId,
            SessionId = sessionId,
            Message = message,
            Role = role,
            Keywords = keywords,
            ConfidenceScore = confidenceScore,
            Timestamp = DateTime.UtcNow
        };
        
        _dbContext.ConversationHistories.Add(conversation);
        await _dbContext.SaveChangesAsync();
    }

    private float CalculateConfidence(string question, KnowledgeBase match)
    {
        var questionKeywords = _keywordExtractor.ExtractKeywords(question);
        var matchKeywords = match.Keywords?.Split(',', StringSplitOptions.RemoveEmptyEntries)
            .Select(k => k.Trim())
            .ToList() ?? new List<string>();
        
        if (!questionKeywords.Any() || !matchKeywords.Any())
        {
            return 0.5f;
        }
        
        var matchCount = questionKeywords.Count(qk => 
            matchKeywords.Any(mk => mk.Equals(qk, StringComparison.OrdinalIgnoreCase)));
        
        return Math.Min(1.0f, (float)matchCount / questionKeywords.Count);
    }

    private float CosineSimilarity(float[] vector1, float[] vector2)
    {
        if (vector1.Length != vector2.Length)
        {
            return 0;
        }
        
        float dotProduct = 0;
        float magnitude1 = 0;
        float magnitude2 = 0;
        
        for (int i = 0; i < vector1.Length; i++)
        {
            dotProduct += vector1[i] * vector2[i];
            magnitude1 += vector1[i] * vector1[i];
            magnitude2 += vector2[i] * vector2[i];
        }
        
        magnitude1 = (float)Math.Sqrt(magnitude1);
        magnitude2 = (float)Math.Sqrt(magnitude2);
        
        if (magnitude1 == 0 || magnitude2 == 0)
        {
            return 0;
        }
        
        return dotProduct / (magnitude1 * magnitude2);
    }
}

