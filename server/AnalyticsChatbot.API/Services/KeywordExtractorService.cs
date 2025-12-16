using System.Text.RegularExpressions;

namespace AnalyticsChatbot.API.Services;

public interface IKeywordExtractorService
{
    List<string> ExtractKeywords(string text);
    Dictionary<string, float> ExtractKeywordsWithWeights(string text);
}

public class KeywordExtractorService : IKeywordExtractorService
{
    private readonly ILogger<KeywordExtractorService> _logger;
    
    // Common stop words to filter out
    private readonly HashSet<string> _stopWords = new(StringComparer.OrdinalIgnoreCase)
    {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
        "be", "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "can", "this", "that", "these", "those",
        "i", "you", "he", "she", "it", "we", "they", "what", "which", "who",
        "when", "where", "why", "how", "all", "each", "every", "both", "few",
        "more", "most", "other", "some", "such", "no", "nor", "not", "only",
        "own", "same", "so", "than", "too", "very", "just", "me", "my", "your"
    };
    
    // Important technical/domain keywords (higher weight)
    private readonly HashSet<string> _importantKeywords = new(StringComparer.OrdinalIgnoreCase)
    {
        "vendor", "customer", "product", "order", "sales", "revenue", "profit",
        "employee", "department", "inventory", "warehouse", "supplier", "invoice",
        "payment", "shipment", "delivery", "price", "quantity", "total", "count",
        "average", "maximum", "minimum", "report", "analytics", "data", "query"
    };

    public KeywordExtractorService(ILogger<KeywordExtractorService> logger)
    {
        _logger = logger;
    }

    public List<string> ExtractKeywords(string text)
    {
        var keywordsWithWeights = ExtractKeywordsWithWeights(text);
        return keywordsWithWeights
            .OrderByDescending(kv => kv.Value)
            .Select(kv => kv.Key)
            .ToList();
    }

    public Dictionary<string, float> ExtractKeywordsWithWeights(string text)
    {
        if (string.IsNullOrWhiteSpace(text))
        {
            return new Dictionary<string, float>();
        }

        var keywords = new Dictionary<string, float>(StringComparer.OrdinalIgnoreCase);
        
        // Clean and tokenize the text
        var cleanText = CleanText(text);
        var tokens = Tokenize(cleanText);
        
        // Extract single words
        foreach (var token in tokens)
        {
            if (IsValidKeyword(token))
            {
                var weight = CalculateWeight(token);
                
                if (keywords.ContainsKey(token))
                {
                    keywords[token] += weight;
                }
                else
                {
                    keywords[token] = weight;
                }
            }
        }
        
        // Extract bi-grams (two-word phrases)
        var bigrams = ExtractNGrams(tokens, 2);
        foreach (var bigram in bigrams)
        {
            var phrase = string.Join(" ", bigram);
            if (IsValidPhrase(phrase))
            {
                var weight = CalculateWeight(phrase) * 1.5f; // Phrases get higher weight
                
                if (keywords.ContainsKey(phrase))
                {
                    keywords[phrase] += weight;
                }
                else
                {
                    keywords[phrase] = weight;
                }
            }
        }
        
        // Extract tri-grams (three-word phrases)
        var trigrams = ExtractNGrams(tokens, 3);
        foreach (var trigram in trigrams)
        {
            var phrase = string.Join(" ", trigram);
            if (IsValidPhrase(phrase))
            {
                var weight = CalculateWeight(phrase) * 2.0f; // Longer phrases get even higher weight
                
                if (keywords.ContainsKey(phrase))
                {
                    keywords[phrase] += weight;
                }
                else
                {
                    keywords[phrase] = weight;
                }
            }
        }
        
        // Normalize weights
        if (keywords.Any())
        {
            var maxWeight = keywords.Values.Max();
            var normalizedKeywords = keywords.ToDictionary(
                kv => kv.Key,
                kv => kv.Value / maxWeight
            );
            
            return normalizedKeywords;
        }
        
        return keywords;
    }

    private string CleanText(string text)
    {
        // Remove special characters but keep spaces and alphanumerics
        var cleaned = Regex.Replace(text, @"[^\w\s]", " ");
        
        // Remove extra whitespace
        cleaned = Regex.Replace(cleaned, @"\s+", " ");
        
        return cleaned.Trim();
    }

    private List<string> Tokenize(string text)
    {
        return text.Split(' ', StringSplitOptions.RemoveEmptyEntries)
            .Select(t => t.ToLower())
            .ToList();
    }

    private List<List<string>> ExtractNGrams(List<string> tokens, int n)
    {
        var ngrams = new List<List<string>>();
        
        for (int i = 0; i <= tokens.Count - n; i++)
        {
            ngrams.Add(tokens.Skip(i).Take(n).ToList());
        }
        
        return ngrams;
    }

    private bool IsValidKeyword(string token)
    {
        // Must be at least 3 characters (unless it's an important keyword)
        if (token.Length < 3 && !_importantKeywords.Contains(token))
        {
            return false;
        }
        
        // Not a stop word
        if (_stopWords.Contains(token))
        {
            return false;
        }
        
        // Must contain at least one letter
        if (!Regex.IsMatch(token, @"[a-zA-Z]"))
        {
            return false;
        }
        
        return true;
    }

    private bool IsValidPhrase(string phrase)
    {
        var words = phrase.Split(' ');
        
        // All words in phrase should be valid
        return words.All(w => IsValidKeyword(w));
    }

    private float CalculateWeight(string keyword)
    {
        float weight = 1.0f;
        
        // Important domain keywords get higher weight
        if (_importantKeywords.Contains(keyword))
        {
            weight *= 2.0f;
        }
        
        // Longer keywords might be more specific
        if (keyword.Length > 10)
        {
            weight *= 1.3f;
        }
        
        // Keywords with numbers might be more specific
        if (Regex.IsMatch(keyword, @"\d"))
        {
            weight *= 1.2f;
        }
        
        return weight;
    }
}

