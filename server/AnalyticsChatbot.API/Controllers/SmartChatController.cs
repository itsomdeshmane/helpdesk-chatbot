using Microsoft.AspNetCore.Mvc;
using AnalyticsChatbot.API.Services;
using AnalyticsChatbot.API.Models;
using System.Text.Json;
using System.Text;

namespace AnalyticsChatbot.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class SmartChatController : ControllerBase
{
    private readonly IRagService _ragService;
    private readonly IClarifyingQuestionService _clarifyingQuestionService;
    private readonly IConversationContextService _contextService;
    private readonly ILlmService _llmService;
    private readonly ISqlExecutionService _sqlExecutionService;
    private readonly IGenericSchemaService _schemaService;
    private readonly IConfiguration _configuration;
    private readonly ILogger<SmartChatController> _logger;

    public SmartChatController(
        IRagService ragService,
        IClarifyingQuestionService clarifyingQuestionService,
        IConversationContextService contextService,
        ILlmService llmService,
        ISqlExecutionService sqlExecutionService,
        IGenericSchemaService schemaService,
        IConfiguration configuration,
        ILogger<SmartChatController> logger)
    {
        _ragService = ragService;
        _clarifyingQuestionService = clarifyingQuestionService;
        _contextService = contextService;
        _llmService = llmService;
        _sqlExecutionService = sqlExecutionService;
        _schemaService = schemaService;
        _configuration = configuration;
        _logger = logger;
    }

    [HttpPost("stream")]
    public async Task StreamChat([FromBody] SmartChatRequest request)
    {
        Response.ContentType = "text/event-stream";
        Response.Headers["Cache-Control"] = "no-cache";
        Response.Headers["X-Accel-Buffering"] = "no";

        await foreach (var chunk in ProcessQueryStreamAsync(request))
        {
            var json = JsonSerializer.Serialize(chunk);
            var data = $"data: {json}\n\n";
            await Response.Body.WriteAsync(Encoding.UTF8.GetBytes(data));
            await Response.Body.FlushAsync();
        }
    }

    [HttpPost("query")]
    public async Task<ActionResult<SmartChatResponse>> ProcessQuery([FromBody] SmartChatRequest request)
    {
        try
        {
            var response = new SmartChatResponse
            {
                Success = true,
                SessionId = request.SessionId ?? _contextService.GenerateSessionId()
            };

            // Step 1: Search RAG knowledge base
            var answer = await _ragService.GetAnswerAsync(request.Query, request.UserId, response.SessionId);

            if (!string.IsNullOrEmpty(answer))
            {
                response.Message = answer;
                response.Source = "knowledge_base";
                response.RequiresClarification = false;
                return Ok(response);
            }

            // Step 2: Try to answer using SQL/Analytics
            var dbConnectionString = _configuration.GetConnectionString("DefaultConnection");
            try
            {
                var sqlQuery = await _llmService.ConvertToSqlAsync(request.Query);
                
                if (!string.IsNullOrWhiteSpace(sqlQuery) && !string.IsNullOrWhiteSpace(dbConnectionString))
                {
                    var result = await _sqlExecutionService.ExecuteQueryAsync(sqlQuery, dbConnectionString, request.Query);
                    
                    if (result.Success && result.Rows != null && result.Rows.Count > 0)
                    {
                        response.Message = result.Message ?? "Here are the results";
                        response.Data = result.Data;
                        response.Rows = result.Rows;
                        response.Columns = result.Columns;
                        response.ResponseFormat = result.ResponseFormat;
                        response.Source = "database";
                        response.RequiresClarification = false;
                        return Ok(response);
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "SQL execution failed, falling back to clarifying question");
            }

            // Step 3: No answer found - ask clarifying question with available tables
            List<string>? availableTables = null;
            
            if (!string.IsNullOrWhiteSpace(dbConnectionString))
            {
                try
                {
                    var tables = await _schemaService.GetAllTablesAsync(dbConnectionString);
                    availableTables = tables.Select(t => t.TableName).ToList();
                }
                catch (Exception ex)
                {
                    _logger.LogWarning(ex, "Could not fetch available tables for clarification");
                }
            }
            
            var clarifyingQuestion = await _clarifyingQuestionService.GenerateClarifyingQuestionAsync(
                request.Query, request.UserId, response.SessionId, availableTables);

            response.Message = clarifyingQuestion ?? "I'm not sure I understand. Could you please rephrase your question?";
            response.RequiresClarification = true;
            response.Source = "clarification";

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing query");
            return StatusCode(500, new SmartChatResponse
            {
                Success = false,
                Message = $"An error occurred: {ex.Message}"
            });
        }
    }

    private async IAsyncEnumerable<StreamChunk> ProcessQueryStreamAsync(SmartChatRequest request)
    {
        var sessionId = request.SessionId ?? _contextService.GenerateSessionId();
        var dbConnectionString = _configuration.GetConnectionString("DefaultConnection");

        // Send initial status
        yield return new StreamChunk { Type = "status", Content = "Processing your question..." };

        // Step 1: Search RAG knowledge base
        yield return new StreamChunk { Type = "status", Content = "Searching knowledge base..." };
        
        var answer = await _ragService.GetAnswerAsync(request.Query, request.UserId, sessionId);

        if (!string.IsNullOrEmpty(answer))
        {
            // Stream answer word by word for better UX
            var words = answer.Split(' ');
            foreach (var word in words)
            {
                yield return new StreamChunk { Type = "text", Content = word + " " };
                await Task.Delay(30); // Small delay for streaming effect
            }
            
            yield return new StreamChunk 
            { 
                Type = "complete", 
                Content = answer,
                Source = "knowledge_base"
            };
            yield break;
        }

        // Step 2: Try SQL/Analytics
        yield return new StreamChunk { Type = "status", Content = "Analyzing data..." };
        
        ReportResult? result = null;
        string? sqlQuery = null;
        
        try
        {
            sqlQuery = await _llmService.ConvertToSqlAsync(request.Query);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "SQL generation failed");
        }
        
        if (!string.IsNullOrWhiteSpace(sqlQuery) && !string.IsNullOrWhiteSpace(dbConnectionString))
        {
            try
            {
                result = await _sqlExecutionService.ExecuteQueryAsync(sqlQuery, dbConnectionString, request.Query);
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "SQL execution failed");
            }
            
            if (result != null && result.Success && result.Rows != null && result.Rows.Count > 0)
            {
                // Stream the natural language response
                var message = result.Message ?? "Here are the results";
                var words = message.Split(' ');
                foreach (var word in words)
                {
                    yield return new StreamChunk { Type = "text", Content = word + " " };
                    await Task.Delay(30);
                }
                
                yield return new StreamChunk
                {
                    Type = "data",
                    Content = JsonSerializer.Serialize(new
                    {
                        rows = result.Rows,
                        columns = result.Columns,
                        format = result.ResponseFormat
                    })
                };
                
                yield return new StreamChunk 
                { 
                    Type = "complete",
                    Content = message,
                    Source = "database"
                };
                yield break;
            }
        }

        // Step 3: Generate clarifying question with available tables
        yield return new StreamChunk { Type = "status", Content = "Generating clarifying question..." };
        
        List<string>? availableTables = null;
        
        if (!string.IsNullOrWhiteSpace(dbConnectionString))
        {
            try
            {
                var tables = await _schemaService.GetAllTablesAsync(dbConnectionString);
                availableTables = tables.Select(t => t.TableName).ToList();
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Could not fetch available tables for clarification");
            }
        }
        
        var clarifyingQuestion = await _clarifyingQuestionService.GenerateClarifyingQuestionAsync(
            request.Query, request.UserId, sessionId, availableTables);

        var clarification = clarifyingQuestion ?? "Could you please provide more details?";
        var clarificationWords = clarification.Split(' ');
        foreach (var word in clarificationWords)
        {
            yield return new StreamChunk { Type = "text", Content = word + " " };
            await Task.Delay(40);
        }
        
        yield return new StreamChunk
        {
            Type = "complete",
            Content = clarification,
            Source = "clarification",
            RequiresClarification = true
        };
    }

    [HttpGet("schema")]
    public async Task<ActionResult<SchemaMetadata>> GetDatabaseSchema()
    {
        try
        {
            var connectionString = _configuration.GetConnectionString("DefaultConnection");
            
            if (string.IsNullOrWhiteSpace(connectionString))
            {
                return BadRequest(new { message = "Database connection not configured" });
            }
            
            var schema = await _schemaService.GetDatabaseSchemaAsync(connectionString);
            return Ok(schema);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving database schema");
            return StatusCode(500, new { message = "Error retrieving schema" });
        }
    }

    [HttpGet("history/{userId}/{sessionId}")]
    public async Task<ActionResult<List<ConversationHistory>>> GetHistory(string userId, string sessionId)
    {
        var history = await _contextService.GetConversationHistoryAsync(userId, sessionId);
        return Ok(history);
    }

    [HttpPost("knowledge")]
    public async Task<ActionResult> AddKnowledge([FromBody] AddKnowledgeRequest request)
    {
        var success = await _ragService.AddToKnowledgeBaseAsync(
            request.Question, 
            request.Answer, 
            request.Category);

        if (success)
        {
            return Ok(new { message = "Knowledge added successfully" });
        }

        return BadRequest(new { message = "Failed to add knowledge" });
    }
}

public class SmartChatRequest
{
    public string Query { get; set; } = string.Empty;
    public string UserId { get; set; } = string.Empty;
    public string? SessionId { get; set; }
}

public class SmartChatResponse
{
    public bool Success { get; set; }
    public string? Message { get; set; }
    public string? SessionId { get; set; }
    public object? Data { get; set; }
    public List<Dictionary<string, object>>? Rows { get; set; }
    public List<string>? Columns { get; set; }
    public string? ResponseFormat { get; set; }
    public string? Source { get; set; } // "knowledge_base", "database", or "clarification"
    public bool RequiresClarification { get; set; }
}

public class StreamChunk
{
    public string Type { get; set; } = string.Empty; // "status", "text", "data", "complete"
    public string Content { get; set; } = string.Empty;
    public string? Source { get; set; }
    public bool RequiresClarification { get; set; } = false;
}

public class AddKnowledgeRequest
{
    public string Question { get; set; } = string.Empty;
    public string Answer { get; set; } = string.Empty;
    public string? Category { get; set; }
}

