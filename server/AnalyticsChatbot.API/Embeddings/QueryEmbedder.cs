using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Linq;
using Microsoft.Extensions.Configuration;

namespace AnalyticsChatbot.API.Embeddings
{
    public class QueryEmbedder
    {
        private readonly HttpClient _httpClient;
        private readonly string _apiKey;

        public QueryEmbedder(IConfiguration configuration)
        {
            _httpClient = new HttpClient();
            _apiKey = configuration["OpenAI:ApiKey"] ?? "YOUR_API_KEY_HERE";
        }

        public async Task<float[]?> GetQueryEmbeddingAsync(string query)
        {
            var requestObj = new
            {
                input = query,
                model = "text-embedding-ada-002"
            };

            var content = new StringContent(JsonSerializer.Serialize(requestObj), Encoding.UTF8, "application/json");
            _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", _apiKey);
            
            var response = await _httpClient.PostAsync("https://api.openai.com/v1/embeddings", content);
            
            if (!response.IsSuccessStatusCode)
                return null;

            using var respStream = await response.Content.ReadAsStreamAsync();
            using var doc = await JsonDocument.ParseAsync(respStream);
            
            // Parse the embedding vector from OpenAI API response
            var root = doc.RootElement.GetProperty("data");
            if (root.GetArrayLength() > 0)
            {
                return root[0].GetProperty("embedding")
                    .EnumerateArray()
                    .Select(x => x.GetSingle())
                    .ToArray();
            }

            return null;
        }
    }
}

