using AnalyticsChatbot.API.Models;

namespace AnalyticsChatbot.API.Services
{
    public interface IChatSessionService
    {
        Task<ChatSession> CreateSessionAsync(string userId, string? userEmail = null, string? userName = null);
        Task<ChatSession?> GetSessionAsync(string sessionId);
        Task<List<ChatSession>> GetUserSessionsAsync(string userId, int limit = 10);
        Task<List<ChatMessage>> GetSessionMessagesAsync(string sessionId);
        Task<ChatMessage> SaveMessageAsync(string sessionId, string message, string role, 
            string? sqlQuery = null, string? responseData = null, string? responseFormat = null, 
            bool hasError = false, string? errorMessage = null, int? responseTimeMs = null);
        Task UpdateSessionAsync(string sessionId);
        Task<bool> DeleteSessionAsync(string sessionId);
        Task<ChatSession?> GetOrCreateSessionAsync(string? sessionId, string userId, string? userEmail = null, string? userName = null);
    }
}

