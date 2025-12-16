using AnalyticsChatbot.API.Models;
using Microsoft.EntityFrameworkCore;
using System.Text.Json;

namespace AnalyticsChatbot.API.Services;

public interface IConversationContextService
{
    Task<List<ConversationHistory>> GetConversationHistoryAsync(string userId, string sessionId, int limit = 10);
    Task<ConversationContext?> GetContextAsync(string userId, string sessionId);
    Task UpdateContextAsync(string userId, string sessionId, string? intent = null, string? contextData = null);
    Task ClearPendingClarificationAsync(string userId, string sessionId);
    string GenerateSessionId();
}

public class ConversationContextService : IConversationContextService
{
    private readonly AppDbContext _dbContext;
    private readonly ILogger<ConversationContextService> _logger;

    public ConversationContextService(AppDbContext dbContext, ILogger<ConversationContextService> logger)
    {
        _dbContext = dbContext;
        _logger = logger;
    }

    public async Task<List<ConversationHistory>> GetConversationHistoryAsync(string userId, string sessionId, int limit = 10)
    {
        return await _dbContext.ConversationHistories
            .Where(c => c.UserId == userId && c.SessionId == sessionId)
            .OrderByDescending(c => c.Timestamp)
            .Take(limit)
            .OrderBy(c => c.Timestamp) // Re-order for chronological display
            .ToListAsync();
    }

    public async Task<ConversationContext?> GetContextAsync(string userId, string sessionId)
    {
        return await _dbContext.ConversationContexts
            .FirstOrDefaultAsync(c => c.UserId == userId && c.SessionId == sessionId && c.IsActive);
    }

    public async Task UpdateContextAsync(string userId, string sessionId, string? intent = null, string? contextData = null)
    {
        var context = await GetContextAsync(userId, sessionId);
        
        if (context == null)
        {
            context = new ConversationContext
            {
                UserId = userId,
                SessionId = sessionId,
                CurrentIntent = intent,
                ContextData = contextData,
                LastActivity = DateTime.UtcNow,
                IsActive = true
            };
            _dbContext.ConversationContexts.Add(context);
        }
        else
        {
            if (intent != null)
                context.CurrentIntent = intent;
            
            if (contextData != null)
                context.ContextData = contextData;
            
            context.LastActivity = DateTime.UtcNow;
        }
        
        await _dbContext.SaveChangesAsync();
    }

    public async Task ClearPendingClarificationAsync(string userId, string sessionId)
    {
        var context = await GetContextAsync(userId, sessionId);
        
        if (context != null)
        {
            context.PendingClarification = null;
            context.LastActivity = DateTime.UtcNow;
            await _dbContext.SaveChangesAsync();
        }
    }

    public string GenerateSessionId()
    {
        return $"session_{Guid.NewGuid():N}_{DateTime.UtcNow:yyyyMMddHHmmss}";
    }
}

