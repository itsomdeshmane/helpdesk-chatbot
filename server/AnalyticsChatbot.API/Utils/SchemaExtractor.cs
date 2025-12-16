using System;
using System.Collections.Generic;
using System.Data;
using System.Threading.Tasks;
using MySql.Data.MySqlClient;

namespace AnalyticsChatbot.API.Utils
{
    public class SchemaElement
    {
        public string TableName { get; set; } = string.Empty;
        public string ColumnName { get; set; } = string.Empty;
        public string? ColumnDescription { get; set; }
    }

    public class SchemaExtractor
    {
        private readonly string _connectionString;
        public SchemaExtractor(string connectionString)
        {
            _connectionString = connectionString;
        }

        public async Task<List<SchemaElement>> GetSchemaAsync()
        {
            var result = new List<SchemaElement>();
            using var connection = new MySqlConnection(_connectionString);
            await connection.OpenAsync();

            var sql = @"SELECT TABLE_NAME, COLUMN_NAME, COLUMN_COMMENT FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE();";
            using var cmd = new MySqlCommand(sql, connection);

            using var reader = await cmd.ExecuteReaderAsync();
            while (await reader.ReadAsync())
            {
                var element = new SchemaElement
                {
                    TableName = reader.GetString("TABLE_NAME"),
                    ColumnName = reader.GetString("COLUMN_NAME"),
                    ColumnDescription = reader.IsDBNull("COLUMN_COMMENT") ? null : reader.GetString("COLUMN_COMMENT")
                };
                result.Add(element);
            }
            return result;
        }
    }
}
