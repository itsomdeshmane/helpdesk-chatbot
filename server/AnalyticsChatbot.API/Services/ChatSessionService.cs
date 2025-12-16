using AnalyticsChatbot.API.Models;
using Microsoft.EntityFrameworkCore;

namespace AnalyticsChatbot.API.Services
{
    public class ChatSessionService : IChatSessionService
    {
        private readonly AppDbContext _context;
        private readonly ILogger<ChatSessionService> _logger;

        public ChatSessionService(AppDbContext context, ILogger<ChatSessionService> logger)
        {
            _context = context;
            _logger = logger;
        }

        public async Task<ChatSession> CreateSessionAsync(string userId, string? userEmail = null, string? userName = null)
        {
            var session = new ChatSession
            {
                SessionId = Guid.NewGuid().ToString(),
                UserId = userId,
                UserEmail = userEmail,
                UserName = userName,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow,
                IsActive = true,
                MessageCount = 0
            };

            _context.ChatSessions.Add(session);
            await _context.SaveChangesAsync();

            _logger.LogInformation("Created new chat session {SessionId} for user {UserId}", session.SessionId, userId);
            
            return session;
        }

        public async Task<ChatSession?> GetSessionAsync(string sessionId)
        {
            return await _context.ChatSessions
                .Include(s => s.Messages)
                .FirstOrDefaultAsync(s => s.SessionId == sessionId);
        }

        public async Task<List<ChatSession>> GetUserSessionsAsync(string userId, int limit = 10)
        {
            return await _context.ChatSessions
                .Where(s => s.UserId == userId)
                .OrderByDescending(s => s.UpdatedAt)
                .Take(limit)
                .Include(s => s.Messages)
                .ToListAsync();
        }

        public async Task<List<ChatMessage>> GetSessionMessagesAsync(string sessionId)
        {
            return await _context.ChatMessages
                .Where(m => m.SessionId == sessionId)
                .OrderBy(m => m.Timestamp)
                .ToListAsync();
        }

        public async Task<ChatMessage> SaveMessageAsync(
            string sessionId, 
            string message, 
            string role,
            string? sqlQuery = null,
            string? responseData = null,
            string? responseFormat = null,
            bool hasError = false,
            string? errorMessage = null,
            int? responseTimeMs = null)
        {
            var chatMessage = new ChatMessage
            {
                MessageId = Guid.NewGuid().ToString(),
                SessionId = sessionId,
                Message = message,
                Role = role,
                SqlQuery = sqlQuery,
                ResponseData = responseData,
                ResponseFormat = responseFormat,
                HasError = hasError,
                ErrorMessage = errorMessage,
                ResponseTimeMs = responseTimeMs,
                Timestamp = DateTime.UtcNow
            };

            _context.ChatMessages.Add(chatMessage);
            
            // Update session
            var session = await _context.ChatSessions.FindAsync(sessionId);
            if (session != null)
            {
                session.MessageCount++;
                session.UpdatedAt = DateTime.UtcNow;
            }

            await _context.SaveChangesAsync();

            _logger.LogInformation("Saved message {MessageId} to session {SessionId}", chatMessage.MessageId, sessionId);

            return chatMessage;
        }

        public async Task UpdateSessionAsync(string sessionId)
        {
            var session = await _context.ChatSessions.FindAsync(sessionId);
            if (session != null)
            {
                session.UpdatedAt = DateTime.UtcNow;
                await _context.SaveChangesAsync();
            }
        }

        public async Task<bool> DeleteSessionAsync(string sessionId)
        {
            var session = await _context.ChatSessions
                .Include(s => s.Messages)
                .FirstOrDefaultAsync(s => s.SessionId == sessionId);

            if (session == null)
                return false;

            _context.ChatSessions.Remove(session);
            await _context.SaveChangesAsync();

            _logger.LogInformation("Deleted session {SessionId}", sessionId);
            
            return true;
        }

        public async Task<ChatSession?> GetOrCreateSessionAsync(
            string? sessionId, 
            string userId, 
            string? userEmail = null, 
            string? userName = null)
        {
            // If sessionId provided, try to get existing session
            if (!string.IsNullOrEmpty(sessionId))
            {
                var existingSession = await GetSessionAsync(sessionId);
                if (existingSession != null && existingSession.UserId == userId)
                {
                    return existingSession;
                }
            }

            // Create new session
            return await CreateSessionAsync(userId, userEmail, userName);
        }
    }
}

