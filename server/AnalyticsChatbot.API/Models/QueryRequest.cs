namespace AnalyticsChatbot.API.Models;

public class QueryRequest
{
    public string Query { get; set; } = string.Empty;
    public string? ConnectionString { get; set; }
    public string? SessionId { get; set; }
}
