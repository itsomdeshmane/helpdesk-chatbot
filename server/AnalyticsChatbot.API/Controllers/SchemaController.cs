using Microsoft.AspNetCore.Mvc;
using AnalyticsChatbot.API.Utils;
using AnalyticsChatbot.API.Embeddings;

namespace AnalyticsChatbot.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SchemaController : ControllerBase
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<SchemaController> _logger;
        private readonly VectorSearch _vectorSearch;

        public SchemaController(
            IConfiguration configuration,
            ILogger<SchemaController> logger,
            VectorSearch vectorSearch)
        {
            _configuration = configuration;
            _logger = logger;
            _vectorSearch = vectorSearch;
        }

        /// <summary>
        /// Admin endpoint to extract schema from database and generate embeddings
        /// </summary>
        [HttpPost("generate-embeddings")]
        public async Task<IActionResult> GenerateEmbeddings([FromQuery] string? connectionString = null)
        {
            try
            {
                // Use provided connection string or fall back to configured one
                var connString = connectionString ?? _configuration.GetConnectionString("DefaultConnection");
                
                if (string.IsNullOrEmpty(connString))
                {
                    return BadRequest("No connection string provided or configured");
                }

                _logger.LogInformation("Starting schema extraction and embedding generation...");

                // Step 1: Extract schema
                var extractor = new SchemaExtractor(connString);
                var schemaElements = await extractor.GetSchemaAsync();
                _logger.LogInformation("Extracted {Count} schema elements", schemaElements.Count);

                // Step 2: Generate embeddings
                var embedder = new SchemaEmbedder(_configuration);
                var embeddings = await embedder.EmbedSchemaAsync(schemaElements);
                _logger.LogInformation("Generated embeddings for {Count} elements", embeddings.Count);

                // Step 3: Reload embeddings into VectorSearch
                await _vectorSearch.LoadEmbeddingsAsync();
                _logger.LogInformation("Reloaded embeddings into vector search");

                return Ok(new
                {
                    success = true,
                    message = $"Successfully generated embeddings for {embeddings.Count} schema elements",
                    schemaElementCount = schemaElements.Count,
                    embeddingCount = embeddings.Count
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error generating embeddings");
                return StatusCode(500, new
                {
                    success = false,
                    message = $"Error: {ex.Message}"
                });
            }
        }

        /// <summary>
        /// Get current schema information
        /// </summary>
        [HttpGet("info")]
        public async Task<IActionResult> GetSchemaInfo([FromQuery] string? connectionString = null)
        {
            try
            {
                var connString = connectionString ?? _configuration.GetConnectionString("DefaultConnection");
                
                if (string.IsNullOrEmpty(connString))
                {
                    return BadRequest("No connection string provided or configured");
                }

                var extractor = new SchemaExtractor(connString);
                var schemaElements = await extractor.GetSchemaAsync();

                var tableGroups = schemaElements
                    .GroupBy(e => e.TableName)
                    .Select(g => new
                    {
                        TableName = g.Key,
                        ColumnCount = g.Count(),
                        Columns = g.Select(e => new
                        {
                            e.ColumnName,
                            e.ColumnDescription
                        }).ToList()
                    })
                    .ToList();

                return Ok(new
                {
                    success = true,
                    tableCount = tableGroups.Count,
                    totalColumns = schemaElements.Count,
                    tables = tableGroups
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error fetching schema info");
                return StatusCode(500, new
                {
                    success = false,
                    message = $"Error: {ex.Message}"
                });
            }
        }
    }
}

