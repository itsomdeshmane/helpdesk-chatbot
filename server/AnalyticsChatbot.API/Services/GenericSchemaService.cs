using System.Data;
using MySql.Data.MySqlClient;
using Dapper;

namespace AnalyticsChatbot.API.Services;

public interface IGenericSchemaService
{
    Task<List<TableInfo>> GetAllTablesAsync(string connectionString);
    Task<List<ColumnInfo>> GetTableColumnsAsync(string connectionString, string tableName);
    Task<SchemaMetadata> GetDatabaseSchemaAsync(string connectionString);
    string ExtractTableNameFromQuery(string query, List<string> availableTables);
}

public class GenericSchemaService : IGenericSchemaService
{
    private readonly ILogger<GenericSchemaService> _logger;

    public GenericSchemaService(ILogger<GenericSchemaService> logger)
    {
        _logger = logger;
    }

    public async Task<List<TableInfo>> GetAllTablesAsync(string connectionString)
    {
        try
        {
            using var connection = new MySqlConnection(connectionString);
            await connection.OpenAsync();

            var query = @"
                SELECT 
                    TABLE_NAME as TableName,
                    TABLE_TYPE as TableType,
                    TABLE_ROWS as RowCount,
                    TABLE_COMMENT as Description
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME";

            var tables = await connection.QueryAsync<TableInfo>(query);
            return tables.ToList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting tables from database");
            return new List<TableInfo>();
        }
    }

    public async Task<List<ColumnInfo>> GetTableColumnsAsync(string connectionString, string tableName)
    {
        try
        {
            using var connection = new MySqlConnection(connectionString);
            await connection.OpenAsync();

            var query = @"
                SELECT 
                    COLUMN_NAME as ColumnName,
                    DATA_TYPE as DataType,
                    IS_NULLABLE as IsNullable,
                    COLUMN_KEY as ColumnKey,
                    COLUMN_COMMENT as Description
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = @TableName
                ORDER BY ORDINAL_POSITION";

            var columns = await connection.QueryAsync<ColumnInfo>(query, new { TableName = tableName });
            return columns.ToList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting columns for table {Table}", tableName);
            return new List<ColumnInfo>();
        }
    }

    public async Task<SchemaMetadata> GetDatabaseSchemaAsync(string connectionString)
    {
        var metadata = new SchemaMetadata
        {
            Tables = new List<TableMetadata>()
        };

        try
        {
            var tables = await GetAllTablesAsync(connectionString);

            foreach (var table in tables)
            {
                var columns = await GetTableColumnsAsync(connectionString, table.TableName);
                
                metadata.Tables.Add(new TableMetadata
                {
                    TableName = table.TableName,
                    RowCount = table.RowCount,
                    Description = table.Description,
                    Columns = columns
                });
            }

            _logger.LogInformation("Retrieved schema for {Count} tables", metadata.Tables.Count);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting database schema");
        }

        return metadata;
    }

    public string ExtractTableNameFromQuery(string query, List<string> availableTables)
    {
        if (availableTables == null || !availableTables.Any())
        {
            return string.Empty;
        }

        var queryLower = query.ToLower();

        // Try exact match first
        foreach (var table in availableTables)
        {
            if (queryLower.Contains(table.ToLower()))
            {
                return table;
            }
        }

        // Try singular/plural variations
        foreach (var table in availableTables)
        {
            var singular = table.TrimEnd('s');
            var plural = table + "s";

            if (queryLower.Contains(singular.ToLower()) || queryLower.Contains(plural.ToLower()))
            {
                return table;
            }
        }

        // Try partial matches
        foreach (var table in availableTables)
        {
            if (table.Length > 4)
            {
                var partial = table.Substring(0, Math.Min(table.Length, 6));
                if (queryLower.Contains(partial.ToLower()))
                {
                    return table;
                }
            }
        }

        return string.Empty;
    }
}

public class TableInfo
{
    public string TableName { get; set; } = string.Empty;
    public string TableType { get; set; } = string.Empty;
    public long RowCount { get; set; }
    public string? Description { get; set; }
}

public class ColumnInfo
{
    public string ColumnName { get; set; } = string.Empty;
    public string DataType { get; set; } = string.Empty;
    public string IsNullable { get; set; } = string.Empty;
    public string? ColumnKey { get; set; }
    public string? Description { get; set; }
}

public class SchemaMetadata
{
    public List<TableMetadata> Tables { get; set; } = new();
    public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;
}

public class TableMetadata
{
    public string TableName { get; set; } = string.Empty;
    public long RowCount { get; set; }
    public string? Description { get; set; }
    public List<ColumnInfo> Columns { get; set; } = new();
}

