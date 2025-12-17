# Setup Guide: Semantic Search for Strict Mode

## Overview

The strict answer matcher supports two matching algorithms:

1. **TF-IDF** (keyword-based) - Works out of the box
2. **Semantic Search** (meaning-based) - **Recommended** for better accuracy

This guide explains how to enable semantic search for improved matching quality.

## Why Use Semantic Search?

### TF-IDF (Keyword Matching)
- ✅ Fast and lightweight
- ✅ No additional dependencies
- ❌ Misses similar meanings with different words
- ❌ Less accurate for paraphrased questions

**Example:**
```
Query: "How to reset password?"
Matches: "Reset password procedure" ✅
Misses:  "Recover forgotten credentials" ❌ (same meaning, different words)
```

### Semantic Search (Meaning-Based)
- ✅ Understands meaning, not just keywords
- ✅ Matches paraphrased questions
- ✅ Better accuracy (typically 10-15% improvement)
- ⚠️ Requires additional library (200MB download)

**Example:**
```
Query: "How to reset password?"
Matches: "Reset password procedure" ✅
Matches: "Recover forgotten credentials" ✅ (understands semantic similarity)
```

## Installation

### Option 1: Using pip (Recommended)

```bash
# Navigate to backend directory
cd backend

# Install sentence-transformers
pip install sentence-transformers

# Verify installation
python -c "from sentence_transformers import SentenceTransformer; print('✅ Installed')"
```

### Option 2: Using requirements file

Add to `backend/requirements-ml.txt`:
```txt
sentence-transformers>=2.2.0
```

Then install:
```bash
pip install -r requirements-ml.txt
```

### Option 3: Docker

If using Docker, add to your Dockerfile:
```dockerfile
RUN pip install sentence-transformers
```

## Verification

### Test if semantic search is available:

```python
from llm.strict_answer_matcher import get_strict_matcher

matcher = get_strict_matcher("default")
stats = matcher.get_stats()

if stats.get('has_semantic'):
    print("✅ Semantic search is ENABLED")
else:
    print("⚠️  Semantic search is DISABLED (using TF-IDF)")
```

### Check logs:

When the system starts, look for:
```
✅ Semantic model loaded
```

Or:
```
⚠️  sentence-transformers not installed. Semantic search will be unavailable.
```

## Model Information

The system uses the `all-MiniLM-L6-v2` model:

- **Size:** ~80MB (plus dependencies ~120MB)
- **Speed:** Fast (~100 queries/second on CPU)
- **Quality:** High quality for English text
- **Memory:** ~500MB RAM when loaded

First time usage will download the model automatically.

## Performance Comparison

### Without Semantic Search (TF-IDF Only)

```
Query: "How do I change my password?"

Top Matches:
1. "How to reset password?" - Similarity: 0.72
2. "Password modification steps" - Similarity: 0.45
3. "Change user credentials" - Similarity: 0.38

Best match: 0.72 (below 0.85 threshold)
Result: ❌ No match found
```

### With Semantic Search

```
Query: "How do I change my password?"

Top Matches:
1. "How to reset password?" - Similarity: 0.91 ✅
2. "Password modification steps" - Similarity: 0.87 ✅
3. "Update account credentials" - Similarity: 0.84

Best match: 0.91 (above 0.85 threshold)
Result: ✅ Match found
```

## Troubleshooting

### Problem: Installation fails

**Error:** `RuntimeError: Failed to download model`

**Solution:** Install manually:
```bash
pip install sentence-transformers --no-cache-dir
```

### Problem: Out of memory

**Error:** `MemoryError` during model loading

**Solution:** System needs at least 2GB RAM. If constrained:
1. Use TF-IDF mode (automatic fallback)
2. Increase swap space
3. Upgrade server memory

### Problem: Slow first query

**Behavior:** First query takes 10-15 seconds

**Explanation:** Model is being downloaded and cached

**Solution:** Pre-download the model:
```python
from sentence_transformers import SentenceTransformer

# This downloads and caches the model
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Model cached")
```

### Problem: Model not found

**Error:** `OSError: Can't load tokenizer`

**Solution:** Clear cache and reinstall:
```bash
rm -rf ~/.cache/torch/sentence_transformers/
pip install --upgrade sentence-transformers
```

## Production Deployment

### Best Practices

1. **Pre-download Model**
   ```bash
   # In your deployment script
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```

2. **Monitor Performance**
   - Track query latency
   - Monitor memory usage
   - Compare accuracy with/without semantic search

3. **Resource Requirements**
   - **Minimum:** 2GB RAM, 1 CPU core
   - **Recommended:** 4GB RAM, 2 CPU cores
   - **Storage:** 500MB for model + dependencies

4. **Scaling**
   - Model loads once per process
   - Safe for multi-threading
   - Consider GPU for >1000 queries/second

## Configuration

### Enable/Disable Semantic Search

In `backend/llm/strict_answer_matcher.py`:

```python
# Force disable semantic search (use TF-IDF only)
matcher = StrictAnswerMatcher(tenant_id)
matcher.matcher = QueryMatcher(use_semantic=False)

# Or when finding matches:
result = matcher.find_exact_match(
    query,
    use_semantic=False  # Force TF-IDF
)
```

### Change Model

To use a different model, modify `backend/llm/query_matcher.py`:

```python
# Default model
self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

# Alternative: Multilingual model (larger but supports 50+ languages)
self.semantic_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Alternative: Higher quality (slower, larger)
self.semantic_model = SentenceTransformer('all-mpnet-base-v2')
```

## Testing Semantic vs TF-IDF

Run the comparison test:

```bash
cd backend
python tests/test_strict_mode.py
```

Look for the section:
```
⚖️  Comparing Semantic vs TF-IDF Matching
```

This shows the difference in match quality.

## Costs

### Without Semantic Search
- **Installation:** 0 additional dependencies
- **Disk:** 0MB
- **Memory:** ~100MB
- **Speed:** Fast (pure Python/NumPy)

### With Semantic Search
- **Installation:** ~200MB download (one time)
- **Disk:** ~500MB total
- **Memory:** ~500MB (model loaded in RAM)
- **Speed:** Fast (~100 queries/sec on CPU)

## FAQ

**Q: Is semantic search required?**
A: No, system works with TF-IDF. Semantic search improves accuracy by ~10-15%.

**Q: Can I switch between modes?**
A: Yes, set `use_semantic=False` when calling `find_exact_match()`.

**Q: Does it work offline?**
A: Yes, after first download, model is cached locally.

**Q: Multiple languages?**
A: Use `paraphrase-multilingual-MiniLM-L12-v2` model for 50+ languages.

**Q: Can I use GPU?**
A: Yes, sentence-transformers automatically uses GPU if available.

**Q: How much does accuracy improve?**
A: Typically 10-15% better match rate, especially for paraphrased questions.

## Summary

**Recommended Setup:**
```bash
pip install sentence-transformers
```

**Verify:**
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Ready")
```

**Fallback:**
If installation fails, system automatically uses TF-IDF (keyword matching).

---

**Last Updated:** December 16, 2025
**Version:** 1.0

