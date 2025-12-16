using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Collections.Generic;
using Microsoft.Extensions.Configuration;
using AnalyticsChatbot.API.Utils;

namespace AnalyticsChatbot.API.Embeddings
{
    public class SchemaEmbeddingResult
    {
        public SchemaElement Element { get; set; } = new();
        public float[] Embedding { get; set; } = new float[0];
    }

    public class SchemaEmbedder
    {
        private readonly HttpClient _httpClient;
        private readonly string _apiKey;
        public SchemaEmbedder(IConfiguration configuration)
        {
            _httpClient = new HttpClient();
            _apiKey = configuration["OpenAI:ApiKey"] ?? "YOUR_API_KEY_HERE";
        }

        public async Task<List<SchemaEmbeddingResult>> EmbedSchemaAsync(List<SchemaElement> elements)
        {
            var results = new List<SchemaEmbeddingResult>();
            foreach(var elem in elements)
            {
                var text = $"Table: {elem.TableName}, Column: {elem.ColumnName}, Description: {elem.ColumnDescription}";
                var embedding = await GetEmbeddingAsync(text);
                results.Add(new SchemaEmbeddingResult {
                    Element = elem,
                    Embedding = embedding ?? new float[0]
                });
            }
            // Save to file (schema_embeddings.json) as a sample
            var json = JsonSerializer.Serialize(results);
            await System.IO.File.WriteAllTextAsync("schema_embeddings.json", json);
            return results;
        }

        private async Task<float[]?> GetEmbeddingAsync(string input)
        {
            var requestObj = new {
                input,
                model = "text-embedding-ada-002"
            };
            var content = new StringContent(JsonSerializer.Serialize(requestObj), Encoding.UTF8, "application/json");
            _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", _apiKey);
            var response = await _httpClient.PostAsync("https://api.openai.com/v1/embeddings", content);
            if (!response.IsSuccessStatusCode) return null;
            using var respStream = await response.Content.ReadAsStreamAsync();
            using var doc = await JsonDocument.ParseAsync(respStream);
            // Parse out the vector array from the OpenAI API result
            var root = doc.RootElement.GetProperty("data");
            if (root.GetArrayLength() > 0)
                return root[0].GetProperty("embedding").EnumerateArray().Select(x => x.GetSingle()).ToArray();
            return null;
        }
    }
}
