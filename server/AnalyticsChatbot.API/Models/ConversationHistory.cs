using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace AnalyticsChatbot.API.Models;

public class ConversationHistory
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    public string UserId { get; set; } = string.Empty;
    
    [Required]
    public string SessionId { get; set; } = string.Empty;
    
    [Required]
    public string Message { get; set; } = string.Empty;
    
    [Required]
    public string Role { get; set; } = string.Empty; // "user" or "assistant"
    
    public string? Intent { get; set; }
    
    public string? Keywords { get; set; } // Comma-separated keywords
    
    public string? Context { get; set; } // JSON string of context
    
    public float? ConfidenceScore { get; set; }
    
    public bool IsClarity { get; set; } = false; // If this is a clarifying question
    
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    
    public string? Metadata { get; set; } // JSON for additional data
}

public class KnowledgeBase
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    public string Question { get; set; } = string.Empty;
    
    [Required]
    public string Answer { get; set; } = string.Empty;
    
    public string? Keywords { get; set; }
    
    public string? Category { get; set; }
    
    public string? Embedding { get; set; } // JSON array of embedding vector
    
    public int UsageCount { get; set; } = 0;
    
    public float AverageConfidence { get; set; } = 0;
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    public DateTime? UpdatedAt { get; set; }
}

public class ConversationContext
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    public string SessionId { get; set; } = string.Empty;
    
    [Required]
    public string UserId { get; set; } = string.Empty;
    
    public string? CurrentIntent { get; set; }
    
    public string? PendingClarification { get; set; }
    
    public string? ContextData { get; set; } // JSON
    
    public DateTime LastActivity { get; set; } = DateTime.UtcNow;
    
    public bool IsActive { get; set; } = true;
}

