using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;

namespace AnalyticsChatbot.API.Models
{
    public class AppDbContext : IdentityDbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }
        
        // Chat Session Management
        public DbSet<ChatSession> ChatSessions { get; set; }
        public DbSet<ChatMessage> ChatMessages { get; set; }
        
        // Conversation and RAG related tables
        public DbSet<ConversationHistory> ConversationHistories { get; set; }
        public DbSet<KnowledgeBase> KnowledgeBases { get; set; }
        public DbSet<ConversationContext> ConversationContexts { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Configure ChatSession - ChatMessage relationship
            modelBuilder.Entity<ChatSession>()
                .HasMany(s => s.Messages)
                .WithOne(m => m.ChatSession)
                .HasForeignKey(m => m.SessionId)
                .OnDelete(DeleteBehavior.Cascade);

            // Configure indexes for better performance
            modelBuilder.Entity<ChatSession>()
                .HasIndex(s => s.UserId);

            modelBuilder.Entity<ChatSession>()
                .HasIndex(s => s.CreatedAt);

            modelBuilder.Entity<ChatMessage>()
                .HasIndex(m => m.SessionId);

            modelBuilder.Entity<ChatMessage>()
                .HasIndex(m => m.Timestamp);
        }
    }
}
