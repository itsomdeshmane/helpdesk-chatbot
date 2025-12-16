using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace AnalyticsChatbot.API.Models
{
    public class ChatSession
    {
        [Key]
        public string SessionId { get; set; } = Guid.NewGuid().ToString();
        
        [Required]
        public string UserId { get; set; } = string.Empty;
        
        public string? UserEmail { get; set; }
        
        public string? UserName { get; set; }
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
        
        public bool IsActive { get; set; } = true;
        
        public int MessageCount { get; set; } = 0;
        
        // Navigation property
        public virtual ICollection<ChatMessage> Messages { get; set; } = new List<ChatMessage>();
    }

    public class ChatMessage
    {
        [Key]
        public string MessageId { get; set; } = Guid.NewGuid().ToString();
        
        [Required]
        public string SessionId { get; set; } = string.Empty;
        
        [Required]
        public string Message { get; set; } = string.Empty;
        
        [Required]
        public string Role { get; set; } = string.Empty; // "user" or "assistant"
        
        public string? SqlQuery { get; set; }
        
        public string? ResponseData { get; set; } // JSON serialized data
        
        public string? ResponseFormat { get; set; } // "grid", "list", "sentence"
        
        public bool HasError { get; set; } = false;
        
        public string? ErrorMessage { get; set; }
        
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        
        public int? ResponseTimeMs { get; set; }
        
        // Navigation property
        [ForeignKey("SessionId")]
        public virtual ChatSession? ChatSession { get; set; }
    }
}

