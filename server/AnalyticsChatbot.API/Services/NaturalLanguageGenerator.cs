using AnalyticsChatbot.API.Models;
using System.Text;

namespace AnalyticsChatbot.API.Services;

public interface INaturalLanguageGenerator
{
    string GenerateNaturalLanguageResponse(string userQuery, ReportResult result);
}

public class NaturalLanguageGenerator : INaturalLanguageGenerator
{
    private readonly ILogger<NaturalLanguageGenerator> _logger;

    public NaturalLanguageGenerator(ILogger<NaturalLanguageGenerator> logger)
    {
        _logger = logger;
    }

    public string GenerateNaturalLanguageResponse(string userQuery, ReportResult result)
    {
        if (result.Rows == null || result.Rows.Count == 0)
        {
            return GenerateNoResultsResponse(userQuery);
        }

        var query = userQuery.ToLower().Trim();
        
        _logger.LogInformation("Generating natural language response for query: {Query}", userQuery);

        // Check query type and generate appropriate response
        if (IsCountQuery(query))
        {
            return GenerateCountResponse(query, result);
        }

        if (IsSumOrTotalQuery(query))
        {
            return GenerateSumResponse(query, result);
        }

        if (IsAverageQuery(query))
        {
            return GenerateAverageResponse(query, result);
        }

        if (IsMaxMinQuery(query))
        {
            return GenerateMaxMinResponse(query, result);
        }

        if (IsListQuery(query))
        {
            return GenerateListResponse(query, result);
        }

        if (IsSingleValueQuery(query) || (result.Rows.Count == 1 && result.Columns?.Count == 1))
        {
            return GenerateSingleValueResponse(query, result);
        }

        if (result.Rows.Count == 1)
        {
            return GenerateSingleRecordResponse(query, result);
        }

        // Default: Generate a comprehensive response
        return GenerateMultiRecordResponse(query, result);
    }

    private bool IsCountQuery(string query)
    {
        return query.Contains("how many") || query.Contains("count") || 
               query.Contains("number of") || query.Contains("total number");
    }

    private bool IsSumOrTotalQuery(string query)
    {
        return query.Contains("total") || query.Contains("sum of") || 
               query.Contains("combined");
    }

    private bool IsAverageQuery(string query)
    {
        return query.Contains("average") || query.Contains("avg") || 
               query.Contains("mean");
    }

    private bool IsMaxMinQuery(string query)
    {
        return query.Contains("maximum") || query.Contains("max") || 
               query.Contains("highest") || query.Contains("minimum") || 
               query.Contains("min") || query.Contains("lowest");
    }

    private bool IsListQuery(string query)
    {
        return query.Contains("list") || query.Contains("show me") || 
               query.Contains("what are");
    }

    private bool IsSingleValueQuery(string query)
    {
        return query.Contains("what is") || query.Contains("what's") || 
               query.Contains("when is") || query.Contains("where is") || 
               query.Contains("who is");
    }

    private string GenerateNoResultsResponse(string userQuery)
    {
        return "I couldn't find any results matching your query. Please try rephrasing your question or check if the data exists.";
    }

    private string GenerateCountResponse(string query, ReportResult result)
    {
        if (result.Rows.Count == 1 && result.Columns != null && result.Columns.Count > 0)
        {
            var firstColumn = result.Columns[0];
            var value = result.Rows[0][firstColumn];
            
            // Extract the subject and location from the query
            var subject = ExtractSubject(query);
            var location = ExtractLocation(query);
            
            // Build a more natural response
            var responseBuilder = new StringBuilder();
            responseBuilder.Append("Total available ");
            responseBuilder.Append(subject);
            
            if (!string.IsNullOrWhiteSpace(location))
            {
                responseBuilder.Append($" in {location}");
            }
            
            // Always append the value, handle null case
            if (value == null || value == DBNull.Value)
            {
                responseBuilder.Append(" is: No data available");
            }
            else if (IsNumericValue(value))
            {
                var numValue = Convert.ToInt32(value);
                responseBuilder.Append($" {(numValue == 1 ? "is" : "are")} {value}.");
            }
            else
            {
                responseBuilder.Append($" is: {value}");
            }
            
            return responseBuilder.ToString();
        }

        return $"I found {result.Rows.Count} records that match your query.";
    }

    private string GenerateSumResponse(string query, ReportResult result)
    {
        if (result.Rows.Count == 1 && result.Columns != null && result.Columns.Count > 0)
        {
            var firstColumn = result.Columns[0];
            var value = result.Rows[0][firstColumn];
            
            var subject = ExtractSubject(query);
            var location = ExtractLocation(query);
            
            var responseBuilder = new StringBuilder();
            responseBuilder.Append("The total ");
            responseBuilder.Append(subject);
            
            if (!string.IsNullOrWhiteSpace(location))
            {
                responseBuilder.Append($" in {location}");
            }
            
            // Always append the value, handle null case
            if (value == null || value == DBNull.Value)
            {
                responseBuilder.Append(" is: No data available");
            }
            else if (IsNumericValue(value))
            {
                responseBuilder.Append($" is {FormatNumber(value)}.");
            }
            else
            {
                responseBuilder.Append($" is: {value}");
            }
            
            return responseBuilder.ToString();
        }

        return $"Based on your query, I found {result.Rows.Count} records.";
    }

    private string GenerateAverageResponse(string query, ReportResult result)
    {
        if (result.Rows.Count == 1 && result.Columns != null && result.Columns.Count > 0)
        {
            var firstColumn = result.Columns[0];
            var value = result.Rows[0][firstColumn];
            
            var subject = ExtractSubject(query);
            var location = ExtractLocation(query);
            
            var responseBuilder = new StringBuilder();
            responseBuilder.Append("The average ");
            responseBuilder.Append(subject);
            
            if (!string.IsNullOrWhiteSpace(location))
            {
                responseBuilder.Append($" in {location}");
            }
            
            // Always append the value, handle null case
            if (value == null || value == DBNull.Value)
            {
                responseBuilder.Append(" is: No data available");
            }
            else if (IsNumericValue(value))
            {
                responseBuilder.Append($" is {FormatNumber(value)}.");
            }
            else
            {
                responseBuilder.Append($" is: {value}");
            }
            
            return responseBuilder.ToString();
        }

        return $"I calculated the average from {result.Rows.Count} records.";
    }

    private string GenerateMaxMinResponse(string query, ReportResult result)
    {
        if (result.Rows.Count == 0 || result.Columns == null || result.Columns.Count == 0)
        {
            return "I couldn't determine the value from the results.";
        }

        var isMax = query.Contains("max") || query.Contains("highest");
        var isMin = query.Contains("min") || query.Contains("lowest");
        
        var sb = new StringBuilder();
        
        if (result.Rows.Count == 1)
        {
            var subject = ExtractSubject(query);
            var firstColumn = result.Columns[0];
            var value = result.Rows[0][firstColumn];
            
            if (isMax)
            {
                sb.Append($"The highest {subject} is {value}");
            }
            else if (isMin)
            {
                sb.Append($"The lowest {subject} is {value}");
            }
            else
            {
                sb.Append($"The {subject} is {value}");
            }

            // Add additional details if available
            if (result.Columns.Count > 1)
            {
                sb.Append(" (");
                for (int i = 1; i < result.Columns.Count && i < 3; i++)
                {
                    if (i > 1) sb.Append(", ");
                    sb.Append($"{result.Columns[i]}: {result.Rows[0][result.Columns[i]]}");
                }
                sb.Append(")");
            }
            
            sb.Append(".");
        }
        else
        {
            sb.Append($"I found {result.Rows.Count} records that match your criteria.");
        }

        return sb.ToString();
    }

    private string GenerateListResponse(string query, ReportResult result)
    {
        if (result.Columns == null || result.Columns.Count == 0)
        {
            return "I couldn't generate a list from the results.";
        }

        var subject = ExtractSubject(query);
        var location = ExtractLocation(query);
        var sb = new StringBuilder();
        
        // Make subject more natural
        if (string.IsNullOrWhiteSpace(subject) || subject == "results")
        {
            subject = "items";
        }
        
        if (result.Rows.Count == 0)
        {
            sb.Append($"I couldn't find any {subject}");
            if (!string.IsNullOrWhiteSpace(location))
            {
                sb.Append($" in {location}");
            }
            sb.Append(".");
            return sb.ToString();
        }
        else if (result.Rows.Count == 1)
        {
            var singularSubject = subject.TrimEnd('s');
            sb.Append($"I found 1 {singularSubject}");
        }
        else
        {
            // Handle plural for multiple results
            var pluralSubject = subject;
            if (!subject.EndsWith('s') && !subject.EndsWith("data") && !subject.EndsWith("information"))
            {
                pluralSubject = subject + "s";
            }
            sb.Append($"I found {result.Rows.Count} {pluralSubject}");
        }
        
        if (!string.IsNullOrWhiteSpace(location))
        {
            sb.Append($" in {location}");
        }
        
        sb.Append(":");

        return sb.ToString();
    }

    private string GenerateSingleValueResponse(string query, ReportResult result)
    {
        if (result.Columns == null || result.Columns.Count == 0)
        {
            return "I couldn't extract the value from the results.";
        }

        var firstColumn = result.Columns[0];
        var value = result.Rows[0][firstColumn];
        
        // Try to extract what the user is asking about
        var subject = ExtractSubject(query);
        
        if (query.Contains("what is") || query.Contains("what's"))
        {
            return $"The {subject} is {value}.";
        }
        else if (query.Contains("when"))
        {
            return $"It was {value}.";
        }
        else if (query.Contains("where"))
        {
            return $"It is located at {value}.";
        }
        else if (query.Contains("who"))
        {
            return $"It is {value}.";
        }
        
        return $"{firstColumn}: {value}";
    }

    private string GenerateSingleRecordResponse(string query, ReportResult result)
    {
        if (result.Columns == null || result.Columns.Count == 0)
        {
            return "I found one record but couldn't extract the details.";
        }

        var sb = new StringBuilder();
        sb.AppendLine("Here's what I found:");
        sb.AppendLine();

        foreach (var column in result.Columns)
        {
            var value = result.Rows[0][column];
            if (value != null && !string.IsNullOrEmpty(value.ToString()))
            {
                sb.AppendLine($"• {column}: {value}");
            }
        }

        return sb.ToString().TrimEnd();
    }

    private string GenerateMultiRecordResponse(string query, ReportResult result)
    {
        if (result.Columns == null || result.Columns.Count == 0)
        {
            return $"I found {result.Rows.Count} records that match your query.";
        }

        var subject = ExtractSubject(query);
        var location = ExtractLocation(query);
        var sb = new StringBuilder();
        
        // Make subject more natural
        if (string.IsNullOrWhiteSpace(subject) || subject == "results")
        {
            subject = "records";
        }
        
        if (result.Rows.Count == 0)
        {
            sb.Append($"I couldn't find any {subject}");
            if (!string.IsNullOrWhiteSpace(location))
            {
                sb.Append($" in {location}");
            }
            sb.Append(".");
            return sb.ToString();
        }
        else if (result.Rows.Count == 1)
        {
            var singularSubject = subject.TrimEnd('s');
            sb.Append($"I found 1 {singularSubject}");
        }
        else
        {
            // Handle plural for multiple results
            var pluralSubject = subject;
            if (!subject.EndsWith('s') && !subject.EndsWith("data") && !subject.EndsWith("information"))
            {
                pluralSubject = subject + "s";
            }
            sb.Append($"I found {result.Rows.Count} {pluralSubject}");
        }
        
        if (!string.IsNullOrWhiteSpace(location))
        {
            sb.Append($" in {location}");
        }
        
        sb.Append(":");
        
        return sb.ToString();
    }

    private string ExtractSubject(string query)
    {
        query = query.ToLower().Trim();
        
        // Remove location phrases first (generic pattern)
        var workingQuery = System.Text.RegularExpressions.Regex.Replace(query, 
            @"\s+(in|from|at|for|with|by)\s+[a-z\s]+$", "", 
            System.Text.RegularExpressions.RegexOptions.IgnoreCase);
        
        // Remove common question words and phrases
        var cleanQuery = workingQuery
            .Replace("how many", "")
            .Replace("how much", "")
            .Replace("what is", "")
            .Replace("what's", "")
            .Replace("what are", "")
            .Replace("show me", "")
            .Replace("give me", "")
            .Replace("get me", "")
            .Replace("list all", "")
            .Replace("list of", "")
            .Replace("list", "")
            .Replace("total", "")
            .Replace("count of", "")
            .Replace("count", "")
            .Replace("number of", "")
            .Replace("average of", "")
            .Replace("average", "")
            .Replace("sum of", "")
            .Replace("sum", "")
            .Replace("available", "")
            .Replace("the", "")
            .Replace("all", "")
            .Replace("of", "")
            .Replace("are", "")
            .Replace("is", "")
            .Trim();

        // Remove extra spaces
        cleanQuery = System.Text.RegularExpressions.Regex.Replace(cleanQuery, @"\s+", " ");

        // Take first meaningful word or phrase (up to 3 words)
        var words = cleanQuery.Split(' ')
            .Where(w => !string.IsNullOrWhiteSpace(w) && w.Length > 1)
            .Take(3)
            .ToList();
        
        if (words.Any())
        {
            var subject = string.Join(" ", words);
            
            // If we have a meaningful subject, return it
            if (!string.IsNullOrWhiteSpace(subject) && subject.Length > 1)
            {
                return subject;
            }
        }

        return "results";
    }

    private string ExtractLocation(string query)
    {
        query = query.Trim();
        
        // Generic location patterns - captures any text after common prepositions
        var locationPatterns = new[]
        {
            @"\s+in\s+([a-z][a-z\s]+?)(?:\s*[?.!]|$)",
            @"\s+from\s+([a-z][a-z\s]+?)(?:\s*[?.!]|$)",
            @"\s+at\s+([a-z][a-z\s]+?)(?:\s*[?.!]|$)",
            @"\savailable\s+in\s+([a-z][a-z\s]+?)(?:\s*[?.!]|$)",
            @"\slocated\s+in\s+([a-z][a-z\s]+?)(?:\s*[?.!]|$)"
        };
        
        foreach (var pattern in locationPatterns)
        {
            var match = System.Text.RegularExpressions.Regex.Match(query, pattern, 
                System.Text.RegularExpressions.RegexOptions.IgnoreCase);
            
            if (match.Success && match.Groups.Count > 1)
            {
                var location = match.Groups[1].Value.Trim();
                
                // Capitalize each word in the location
                var words = location.Split(' ')
                    .Where(w => !string.IsNullOrWhiteSpace(w))
                    .Select(w => char.ToUpper(w[0]) + w.Substring(1).ToLower());
                
                return string.Join(" ", words);
            }
        }
        
        return string.Empty;
    }

    private bool IsNumericValue(object value)
    {
        if (value == null) return false;
        
        return value is int || value is long || value is decimal || 
               value is double || value is float || 
               decimal.TryParse(value.ToString(), out _);
    }

    private string FormatNumber(object value)
    {
        if (value == null) return "0";

        if (decimal.TryParse(value.ToString(), out var number))
        {
            // Format with thousand separators
            if (number == Math.Floor(number))
            {
                return number.ToString("N0");
            }
            return number.ToString("N2");
        }

        return value.ToString() ?? "0";
    }
}

