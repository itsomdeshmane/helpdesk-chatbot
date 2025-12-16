using System.Collections.Generic;
using System.Text;
using AnalyticsChatbot.API.Embeddings;

namespace AnalyticsChatbot.API.Services
{
    public interface ILlmPromptBuilder
    {
        string BuildPrompt(string userQuery, List<VectorSearchResult> relevantSchema);
    }

    public class LlmPromptBuilder : ILlmPromptBuilder
    {
        public string BuildPrompt(string userQuery, List<VectorSearchResult> relevantSchema)
        {
            var sb = new StringBuilder();
            
            sb.AppendLine("You are a SQL expert. Generate a SQL query based on the user's question and the relevant database schema provided.");
            sb.AppendLine();
            sb.AppendLine("# Relevant Database Schema:");
            
            // Group by table for better readability
            var tableGroups = relevantSchema
                .GroupBy(x => x.Element.TableName)
                .OrderByDescending(g => g.Max(x => x.Similarity));
            
            foreach (var tableGroup in tableGroups)
            {
                sb.AppendLine($"\nTable: {tableGroup.Key}");
                sb.AppendLine("Columns:");
                foreach (var item in tableGroup.OrderByDescending(x => x.Similarity))
                {
                    var desc = string.IsNullOrWhiteSpace(item.Element.ColumnDescription) 
                        ? "" 
                        : $" - {item.Element.ColumnDescription}";
                    sb.AppendLine($"  - {item.Element.ColumnName}{desc}");
                }
            }
            
            sb.AppendLine();
            sb.AppendLine("# User Question:");
            sb.AppendLine(userQuery);
            sb.AppendLine();
            sb.AppendLine("# CRITICAL Instructions:");
            sb.AppendLine("- Return ONLY the raw SQL query");
            sb.AppendLine("- Do NOT include any explanations, comments, or markdown");
            sb.AppendLine("- Do NOT start with phrases like 'Here is', 'The query is', etc.");
            sb.AppendLine("- Use proper MySQL syntax");
            sb.AppendLine("- Use only the tables and columns from the schema above");
            sb.AppendLine("- Start directly with SELECT, INSERT, UPDATE, DELETE, or SHOW");
            sb.AppendLine("- If schema is insufficient, return: SELECT 1 as message, 'Insufficient schema information' as details");
            sb.AppendLine();
            sb.AppendLine("Return the SQL query now:");
            
            return sb.ToString();
        }
    }
}

