using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using AnalyticsChatbot.API.Models;
using AnalyticsChatbot.API.Services;
using System.Security.Claims;
using System.Diagnostics;
using Newtonsoft.Json;

namespace AnalyticsChatbot.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ChatController : ControllerBase
    {
        private readonly ILlmService _llmService;
        private readonly IReportService _reportService;
        private readonly ISqlExecutionService _sqlExecutionService;
        private readonly IChatSessionService _chatSessionService;
        private readonly IConfiguration _configuration;
        private readonly ILogger<ChatController> _logger;

        public ChatController(
            ILlmService llmService, 
            IReportService reportService,
            ISqlExecutionService sqlExecutionService,
            IChatSessionService chatSessionService,
            IConfiguration configuration,
            ILogger<ChatController> logger)
        {
            _llmService = llmService;
            _reportService = reportService;
            _sqlExecutionService = sqlExecutionService;
            _chatSessionService = chatSessionService;
            _configuration = configuration;
            _logger = logger;
        }

        [HttpPost("query")]
        public async Task<ActionResult<ReportResult>> ProcessQuery([FromBody] QueryRequest request)
        {
            var stopwatch = Stopwatch.StartNew();
            
            try
            {
                if (string.IsNullOrWhiteSpace(request.Query))
                {
                    return BadRequest(new ReportResult
                    {
                        Success = false,
                        Message = "Query cannot be empty"
                    });
                }

                // Get or create session
                var userId = User?.FindFirstValue(ClaimTypes.NameIdentifier) ?? "anonymous";
                var userEmail = User?.FindFirstValue(ClaimTypes.Email);
                var userName = User?.FindFirstValue(ClaimTypes.Name);
                
                var session = await _chatSessionService.GetOrCreateSessionAsync(
                    request.SessionId, 
                    userId, 
                    userEmail, 
                    userName
                );

                // Save user message
                await _chatSessionService.SaveMessageAsync(
                    session!.SessionId,
                    request.Query,
                    "user"
                );

                // Convert natural language to SQL
                var sqlQuery = await _llmService.ConvertToSqlAsync(request.Query);

                if (string.IsNullOrWhiteSpace(sqlQuery))
                {
                    var errorResult = new ReportResult
                    {
                        Success = false,
                        Message = "Failed to generate SQL query"
                    };

                    // Save error message
                    await _chatSessionService.SaveMessageAsync(
                        session.SessionId,
                        errorResult.Message,
                        "assistant",
                        sqlQuery: null,
                        responseData: null,
                        responseFormat: "error",
                        hasError: true,
                        errorMessage: errorResult.Message,
                        responseTimeMs: (int)stopwatch.ElapsedMilliseconds
                    );

                    return BadRequest(errorResult);
                }

                // Execute SQL query
                var connectionString = request.ConnectionString 
                    ?? _configuration.GetConnectionString("DefaultConnection");

                if (string.IsNullOrWhiteSpace(connectionString))
                {
                    var errorResult = new ReportResult
                    {
                        Success = false,
                        Message = "Database connection string not configured"
                    };

                    // Save error message
                    await _chatSessionService.SaveMessageAsync(
                        session.SessionId,
                        errorResult.Message,
                        "assistant",
                        sqlQuery: sqlQuery,
                        responseData: null,
                        responseFormat: "error",
                        hasError: true,
                        errorMessage: errorResult.Message,
                        responseTimeMs: (int)stopwatch.ElapsedMilliseconds
                    );

                    return BadRequest(errorResult);
                }

                var result = await _sqlExecutionService.ExecuteQueryAsync(sqlQuery, connectionString, request.Query);
                
                stopwatch.Stop();

                // Save assistant response
                var responseData = new
                {
                    result.Success,
                    result.Message,
                    result.Rows,
                    result.Columns,
                    result.ResponseFormat
                };

                await _chatSessionService.SaveMessageAsync(
                    session.SessionId,
                    result.Message ?? "Query executed successfully",
                    "assistant",
                    sqlQuery: sqlQuery,
                    responseData: JsonConvert.SerializeObject(responseData),
                    responseFormat: result.ResponseFormat,
                    hasError: !result.Success,
                    errorMessage: result.Success ? null : result.Message,
                    responseTimeMs: (int)stopwatch.ElapsedMilliseconds
                );

                // Add session ID to response
                result.SessionId = session.SessionId;

                return Ok(result);
            }
            catch (Exception ex)
            {
                stopwatch.Stop();
                _logger.LogError(ex, "Error processing query: {Query}", request.Query);
                
                // Try to save error to session if possible
                try
                {
                    var userId = User?.FindFirstValue(ClaimTypes.NameIdentifier) ?? "anonymous";
                    var session = await _chatSessionService.GetOrCreateSessionAsync(
                        request.SessionId, 
                        userId
                    );

                    await _chatSessionService.SaveMessageAsync(
                        session!.SessionId,
                        $"Internal server error: {ex.Message}",
                        "assistant",
                        sqlQuery: null,
                        responseData: null,
                        responseFormat: "error",
                        hasError: true,
                        errorMessage: ex.Message,
                        responseTimeMs: (int)stopwatch.ElapsedMilliseconds
                    );
                }
                catch (Exception saveEx)
                {
                    _logger.LogError(saveEx, "Failed to save error message to session");
                }

                return StatusCode(500, new ReportResult
                {
                    Success = false,
                    Message = $"Internal server error: {ex.Message}"
                });
            }
        }

        [HttpPost("validate-sql")]
        public async Task<ActionResult<object>> ValidateSql([FromBody] QueryRequest request)
        {
            try
            {
                var sqlQuery = await _llmService.ConvertToSqlAsync(request.Query);
                
                return Ok(new
                {
                    Success = true,
                    SqlQuery = sqlQuery,
                    OriginalQuery = request.Query
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error validating SQL");
                return StatusCode(500, new { Success = false, Message = ex.Message });
            }
        }

        [HttpGet("sessions")]
        [Authorize]
        public async Task<ActionResult<List<ChatSession>>> GetUserSessions([FromQuery] int limit = 10)
        {
            try
            {
                var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
                if (string.IsNullOrEmpty(userId))
                {
                    return Unauthorized();
                }

                var sessions = await _chatSessionService.GetUserSessionsAsync(userId, limit);
                return Ok(sessions);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting user sessions");
                return StatusCode(500, new { Message = "Failed to retrieve sessions" });
            }
        }

        [HttpGet("sessions/{sessionId}")]
        public async Task<ActionResult<ChatSession>> GetSession(string sessionId)
        {
            try
            {
                var session = await _chatSessionService.GetSessionAsync(sessionId);
                if (session == null)
                {
                    return NotFound(new { Message = "Session not found" });
                }

                // Optionally check if user owns the session
                var userId = User?.FindFirstValue(ClaimTypes.NameIdentifier);
                if (!string.IsNullOrEmpty(userId) && session.UserId != userId && userId != "anonymous")
                {
                    return Forbid();
                }

                return Ok(session);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting session {SessionId}", sessionId);
                return StatusCode(500, new { Message = "Failed to retrieve session" });
            }
        }

        [HttpGet("sessions/{sessionId}/messages")]
        public async Task<ActionResult<List<ChatMessage>>> GetSessionMessages(string sessionId)
        {
            try
            {
                var messages = await _chatSessionService.GetSessionMessagesAsync(sessionId);
                return Ok(messages);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting messages for session {SessionId}", sessionId);
                return StatusCode(500, new { Message = "Failed to retrieve messages" });
            }
        }

        [HttpDelete("sessions/{sessionId}")]
        [Authorize]
        public async Task<ActionResult> DeleteSession(string sessionId)
        {
            try
            {
                var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
                if (string.IsNullOrEmpty(userId))
                {
                    return Unauthorized();
                }

                var session = await _chatSessionService.GetSessionAsync(sessionId);
                if (session == null)
                {
                    return NotFound(new { Message = "Session not found" });
                }

                if (session.UserId != userId)
                {
                    return Forbid();
                }

                var deleted = await _chatSessionService.DeleteSessionAsync(sessionId);
                if (deleted)
                {
                    return Ok(new { Message = "Session deleted successfully" });
                }

                return BadRequest(new { Message = "Failed to delete session" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error deleting session {SessionId}", sessionId);
                return StatusCode(500, new { Message = "Failed to delete session" });
            }
        }
    }
}
