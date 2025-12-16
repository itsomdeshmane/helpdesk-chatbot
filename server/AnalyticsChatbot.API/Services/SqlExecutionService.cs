using MySql.Data.MySqlClient;
using AnalyticsChatbot.API.Models;
using System.Data;
using Dapper;

namespace AnalyticsChatbot.API.Services;

public interface ISqlExecutionService
{
    Task<ReportResult> ExecuteQueryAsync(string sqlQuery, string connectionString, string? userQuery = null);
}

public class SqlExecutionService : ISqlExecutionService
{
    private readonly ILogger<SqlExecutionService> _logger;
    private readonly IResponseFormatAnalyzer _formatAnalyzer;
    private readonly INaturalLanguageGenerator _nlGenerator;

    public SqlExecutionService(
        ILogger<SqlExecutionService> logger, 
        IResponseFormatAnalyzer formatAnalyzer,
        INaturalLanguageGenerator nlGenerator)
    {
        _logger = logger;
        _formatAnalyzer = formatAnalyzer;
        _nlGenerator = nlGenerator;
    }

    public async Task<ReportResult> ExecuteQueryAsync(string sqlQuery, string connectionString, string? userQuery = null)
    {
        var result = new ReportResult
        {
            Success = false,
            Rows = new List<Dictionary<string, object>>(),
            Columns = new List<string>()
        };

        try
        {
            if (string.IsNullOrWhiteSpace(connectionString))
            {
                result.Message = "Connection string is not configured";
                return result;
            }

            using var connection = new MySqlConnection(connectionString);
            await connection.OpenAsync();

            var dapperResults = (await connection.QueryAsync(sqlQuery)).ToList();

            // Get columns from the first row if present
            if (dapperResults.Count > 0)
            {
                var firstRow = (IDictionary<string, object>)dapperResults[0];
                foreach (var col in firstRow.Keys)
                {
                    result.Columns.Add(col);
                }
            }

            // Convert each row to Dictionary<string, object>
            foreach (IDictionary<string, object> row in dapperResults)
            {
                var dictRow = new Dictionary<string, object>();
                foreach (var kvp in row)
                {
                    dictRow[kvp.Key] = kvp.Value ?? DBNull.Value;
                }
                result.Rows.Add(dictRow);
            }

            result.Success = true;
            
            // Determine response format based on user query
            if (!string.IsNullOrWhiteSpace(userQuery))
            {
                result.ResponseFormat = _formatAnalyzer.DetermineResponseFormat(
                    userQuery, 
                    result.Rows.Count, 
                    result.Columns.Count);
                
                // Generate natural language response
                var naturalLanguageResponse = _nlGenerator.GenerateNaturalLanguageResponse(userQuery, result);
                result.Message = naturalLanguageResponse;
            }
            else
            {
                // Default to sentence if no user query provided
                result.ResponseFormat = "sentence";
                result.Message = $"Query executed successfully. {result.Rows.Count} row(s) returned.";
            }
            
            _logger.LogInformation("SQL query executed successfully: {RowCount} rows, Format: {Format}", 
                result.Rows.Count, result.ResponseFormat);
        }
        catch (MySqlException ex)
        {
            _logger.LogError(ex, "MySQL execution error");
            result.Message = $"MySQL Error: {ex.Message}";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing query");
            result.Message = $"Error: {ex.Message}";
        }

        return result;
    }
}
