# Strict Auto Mode - Database-Only Answers

## Overview

When users select **"auto" mode**, the system now operates in **STRICT MODE**, which means:

- ✅ **ONLY returns answers that already exist in the database or documents**
- ✅ **No LLM generation of new answers**
- ✅ **No common knowledge or hallucinations**
- ✅ **No generic responses**
- ❌ **Does NOT use GPT to "fill in the gaps"**
- ❌ **Does NOT add external knowledge**

## How It Works

### Previous Behavior (Before Fix)
```
User Query → Search Documents → Pass to GPT → GPT Generates Answer
                                              ↓
                                    (Could add common knowledge)
```

### New Behavior (Strict Mode)
```
User Query → Search Historical Q&A in Database → Find Exact Match
                                                  ↓
                                         Yes: Return Match
                                         No:  Return "Don't have info"
                                                  ↓
                                         (NO LLM GENERATION)
```

## Implementation Details

### 1. Strict Answer Matcher (`backend/llm/strict_answer_matcher.py`)

A new service that:
- Loads all historical Q&A pairs from the database
- Uses ML-based similarity matching (TF-IDF + Semantic Search)
- Only returns answers if similarity is **≥85%**
- Filters out "don't have information" responses
- Returns exact match or nothing

**Key Features:**
- **Semantic Search**: Uses `sentence-transformers` for better matching
- **TF-IDF Fallback**: Uses traditional keyword matching if semantic unavailable
- **High Threshold**: Requires 85% similarity to prevent false matches
- **Tenant Isolation**: Each tenant has separate matcher

### 2. Smart Chat Integration (`backend/routers/smart_chat.py`)

Modified the `/smart/query` and `/smart/stream` endpoints:

**Changes:**
1. Added strict matcher check as **FIRST step** for auto mode
2. If exact match found (≥85% similarity):
   - Return the matched answer directly
   - Skip LLM generation completely
3. If no match found:
   - Return "I don't have this information" message
   - Do NOT proceed to LLM generation
   - Do NOT try documents or database query

## API Response Format

### When Match Found
```json
{
  "success": true,
  "message": "The actual answer from database...",
  "source": "database_exact_match",
  "matched_query": "The original question that matched",
  "similarity_score": 0.92,
  "confidence": "high",
  "session_id": "abc123"
}
```

### When No Match Found
```json
{
  "success": true,
  "message": "I don't have this exact information in my knowledge base. Please try rephrasing your question or contact support for assistance.",
  "source": "no_match",
  "requires_clarification": true,
  "session_id": "abc123"
}
```

## Configuration

### Similarity Threshold

You can adjust the strictness in `backend/routers/smart_chat.py`:

```python
exact_match = strict_matcher.find_exact_match(
    query,
    similarity_threshold=0.85,  # 85% similarity required (adjust here)
    use_semantic=True
)
```

**Recommended values:**
- `0.90` - Very strict (only near-identical questions)
- `0.85` - Strict (default, good balance)
- `0.80` - Moderate (allows more variation)
- `0.75` - Lenient (may return less relevant answers)

### Training Data

The strict matcher trains on:
- All historical Q&A from `chat_interactions` table
- Only responses with actual content (filters out "don't have" messages)
- Limited to 5000 most recent interactions per tenant

To retrain the matcher:
```python
from llm.strict_answer_matcher import clear_matcher_cache

# Clear cache to force retraining with new data
clear_matcher_cache()
```

## Other Modes (Documents/Database)

**IMPORTANT**: Strict mode **ONLY applies to "auto" source selection**.

If user explicitly selects:
- `source: "documents"` → Uses traditional RAG with LLM generation
- `source: "database"` → Converts to SQL and queries database

This ensures:
- Auto mode = Strict, database-only answers
- Manual mode = Full LLM capabilities when user explicitly requests

## Testing

### Test Endpoint

```bash
# Test strict matching
curl -X POST http://localhost:8000/api/chat/smart/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I reset my password?",
    "source": "auto",
    "tenant_id": "default"
  }'
```

### Test Script

```python
from llm.strict_answer_matcher import get_strict_matcher

matcher = get_strict_matcher("default")

# Test queries
test_queries = [
    "How do I reset my password?",  # Should match if exists in DB
    "What is the capital of France?",  # Should NOT match (general knowledge)
]

for query in test_queries:
    result = matcher.find_exact_match(query, similarity_threshold=0.85)
    if result:
        print(f"✅ Match: {result['response'][:100]}...")
    else:
        print(f"❌ No match found")
```

## Benefits

1. **No Hallucinations**: LLM cannot add information not in database
2. **Consistent Answers**: Same question always gets same answer
3. **Verified Information**: All answers have been previously validated
4. **Fast Response**: No LLM API call needed (faster, cheaper)
5. **Audit Trail**: Can trace answer back to original Q&A pair

## Limitations

1. **Requires Historical Data**: Needs existing Q&A pairs to work
2. **Exact Match Only**: Cannot synthesize answers from multiple sources
3. **No Inference**: Cannot answer variations of questions not seen before
4. **Cold Start Problem**: New tenants with no data won't get answers

## Recommendations

### For Best Results:

1. **Populate Database**: Import common Q&A pairs before going live
2. **Regular Training**: Retrain matcher after significant data additions
3. **Monitor Similarity Scores**: Adjust threshold based on user feedback
4. **Fallback Plan**: Have support team ready for "no match" scenarios

### Migration Strategy:

1. **Phase 1**: Run in parallel, log both strict and LLM answers
2. **Phase 2**: Compare accuracy and user satisfaction
3. **Phase 3**: Switch to strict mode for production
4. **Phase 4**: Monitor "no match" rate and adjust threshold

## Troubleshooting

### Problem: Too Many "No Match" Responses

**Solution**: Lower similarity threshold
```python
similarity_threshold=0.80  # Was 0.85
```

### Problem: Irrelevant Matches

**Solution**: Increase similarity threshold
```python
similarity_threshold=0.90  # Was 0.85
```

### Problem: Matcher Not Initialized

**Solution**: Ensure database has Q&A data
```sql
SELECT COUNT(*) FROM chat_interactions WHERE tenant_id = 'your_tenant';
-- Should return > 0
```

### Problem: Semantic Search Not Working

**Solution**: Install sentence-transformers
```bash
pip install sentence-transformers
```

## Monitoring

Track these metrics:

1. **Match Rate**: % of queries that find a match
2. **Similarity Distribution**: Average similarity scores
3. **User Satisfaction**: Feedback on matched answers
4. **No-Match Queries**: Log queries with no match for future addition

## Future Enhancements

Potential improvements:

1. **Multi-Match Ranking**: Show top 3 matches instead of best only
2. **Confidence Bands**: Different thresholds for high/medium/low confidence
3. **Hybrid Mode**: Allow LLM to combine multiple partial matches
4. **Active Learning**: Prompt admin to add answers for frequent no-matches
5. **A/B Testing**: Automatically test different thresholds per tenant

## API Endpoints Affected

- `POST /api/chat/smart/query` - Non-streaming query
- `POST /api/chat/smart/stream` - Streaming query (SSE)

Both endpoints now use strict mode when `source: "auto"`.

## Configuration Files Changed

- `backend/routers/smart_chat.py` - Main integration
- `backend/llm/strict_answer_matcher.py` - New matcher service
- No environment variables added (uses existing database)

## Dependencies

**Required:**
- `scikit-learn` (already installed)
- `numpy` (already installed)

**Optional (for better matching):**
- `sentence-transformers` (recommended)

Install optional:
```bash
pip install sentence-transformers
```

## Support

For questions or issues:
1. Check logs for "STRICT MODE" messages
2. Verify database has historical data
3. Test matcher initialization manually
4. Adjust similarity threshold if needed
5. Contact development team if persistent issues

---

**Last Updated**: December 16, 2025
**Version**: 1.0
**Author**: AI Development Team

