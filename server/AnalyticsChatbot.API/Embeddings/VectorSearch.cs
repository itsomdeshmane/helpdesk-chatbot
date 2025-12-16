using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using AnalyticsChatbot.API.Utils;

namespace AnalyticsChatbot.API.Embeddings
{
    public class VectorSearchResult
    {
        public SchemaElement Element { get; set; } = new();
        public double Similarity { get; set; }
    }

    public class VectorSearch
    {
        private List<SchemaEmbeddingResult>? _cachedEmbeddings;

        public async Task LoadEmbeddingsAsync(string filePath = "schema_embeddings.json")
        {
            if (!File.Exists(filePath))
                throw new FileNotFoundException("Schema embeddings file not found. Please run schema embedding first.");
            
            var json = await File.ReadAllTextAsync(filePath);
            _cachedEmbeddings = JsonSerializer.Deserialize<List<SchemaEmbeddingResult>>(json);
        }

        public List<VectorSearchResult> FindTopMatches(float[] queryEmbedding, int topN = 10)
        {
            if (_cachedEmbeddings == null || _cachedEmbeddings.Count == 0)
                return new List<VectorSearchResult>();

            var results = new List<VectorSearchResult>();
            
            foreach (var item in _cachedEmbeddings)
            {
                var similarity = CosineSimilarity(queryEmbedding, item.Embedding);
                results.Add(new VectorSearchResult
                {
                    Element = item.Element,
                    Similarity = similarity
                });
            }

            // Return top N results sorted by similarity (descending)
            return results.OrderByDescending(x => x.Similarity).Take(topN).ToList();
        }

        private double CosineSimilarity(float[] vectorA, float[] vectorB)
        {
            if (vectorA.Length != vectorB.Length)
                return 0.0;

            double dotProduct = 0.0;
            double magnitudeA = 0.0;
            double magnitudeB = 0.0;

            for (int i = 0; i < vectorA.Length; i++)
            {
                dotProduct += vectorA[i] * vectorB[i];
                magnitudeA += vectorA[i] * vectorA[i];
                magnitudeB += vectorB[i] * vectorB[i];
            }

            magnitudeA = Math.Sqrt(magnitudeA);
            magnitudeB = Math.Sqrt(magnitudeB);

            if (magnitudeA == 0.0 || magnitudeB == 0.0)
                return 0.0;

            return dotProduct / (magnitudeA * magnitudeB);
        }
    }
}

