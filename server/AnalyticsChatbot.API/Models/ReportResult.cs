namespace AnalyticsChatbot.API.Models;

public class ReportResult
{
    public bool Success { get; set; }
    public string? Message { get; set; }
    public object? Data { get; set; }
    public List<Dictionary<string, object>>? Rows { get; set; }
    public List<string>? Columns { get; set; }
    public string? ResponseFormat { get; set; } // "grid", "list", or "sentence"
    public string? SessionId { get; set; }
}
