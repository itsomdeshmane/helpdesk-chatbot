# Related Topics Hints Feature

## Overview

When the chatbot **cannot find a direct answer** to a user's question, instead of just saying "no information found", it now:

1. 🔍 **Searches for related topics** in the documentation
2. 💡 **Suggests what IS available** that's similar/related
3. 🎯 **Guides user** to relevant information they can actually explore

---

## Problem It Solves

### Before (Bad UX):
```
👤 User: How do I configure email notifications?
🤖 Bot: I don't have information about this in the loaded documentation.

👤 User: [Frustrated, doesn't know what to do next] 😞
```

### After (Great UX):
```
👤 User: How do I configure email notifications?
🤖 Bot: I don't have specific information about "email notifications" 
       in the loaded documentation.

       However, I found related information about:
       • Notification Settings
       • User Alert Configuration
       • System Preferences

       Would you like to know about any of these?

👤 User: Tell me about Notification Settings [Continues conversation!] 😊
```

---

## How It Works

### Step 1: Detect "No Answer" Situation

When main search returns no results:
```python
# In rag.py
context_is_empty = (
    not context or 
    "No relevant documents" in context or
    len(context.strip()) < 50
)

if context_is_empty:
    # Instead of generic "no info" message
    # → Find related topics!
```

### Step 2: Extract Key Terms from Query

```python
query = "How do I configure email notifications?"

# Remove stop words
key_terms = ["configure", "email", "notifications", "configure email notifications"]
```

### Step 3: Search for Related Topics

Try alternative searches with broader terms:
```python
# Search for "configure"
search("configure", tenant_id)
→ Finds: "System Configuration", "Settings"

# Search for "notifications"  
search("notifications", tenant_id)
→ Finds: "Notification Settings", "Alert Configuration"

# Search for full query
search("configure email notifications", tenant_id)
→ Finds: Related docs about notifications
```

### Step 4: Extract Available Topics

Use AI to identify what's actually available:
```python
docs_found = ["System Configuration guide...", "Notification Settings..."]

AI extracts topics:
→ ["Notification Settings", "User Alert Configuration", "System Preferences"]
```

### Step 5: Generate Helpful Response

Format a friendly suggestion:
```
I don't have specific information about "[query]" in the loaded documentation.

However, I found related information about:
• Topic 1
• Topic 2
• Topic 3

Would you like to know about any of these?
```

---

## Examples

### Example 1: Email Notifications

**User Query:** "How do I setup email alerts?"

**Direct Search:** ❌ No results

**Related Topics Search:**
- Search "email" → Finds notification docs
- Search "alerts" → Finds alert system docs
- Search "setup" → Finds configuration docs

**AI Extracts Topics:**
- "System Notification Settings"
- "User Alert Preferences"
- "Email Configuration"

**Response:**
```
I don't have specific information about "setup email alerts" in the 
loaded documentation.

However, I found related information about:
• System Notification Settings
• User Alert Preferences  
• Email Configuration

Would you like to know about any of these?
```

---

### Example 2: Feature Not Documented

**User Query:** "How do I export data to Excel?"

**Direct Search:** ❌ No results

**Related Topics Search:**
- Search "export" → Finds data export docs
- Search "data" → Finds data management docs
- Search "Excel" → No specific Excel docs

**AI Extracts Topics:**
- "Data Export Options"
- "Report Generation"

**Response:**
```
I don't have specific information about "export data to Excel" in the 
loaded documentation.

However, I found related information about:
• Data Export Options
• Report Generation

Would you like to know about any of these?
```

---

### Example 3: Nothing Related Found

**User Query:** "How do I bake a cake?"

**Direct Search:** ❌ No results

**Related Topics Search:**
- Search "bake" → ❌ No results
- Search "cake" → ❌ No results

**No Related Topics Found**

**Response:**
```
I don't have information about this in the loaded documentation. 
Please check if the relevant document has been uploaded or contact support.
```

*(Falls back to standard message)*

---

## Technical Implementation

### Main Function

```python
def generate_not_found_response_with_hints(query: str, tenant_id: str) -> str:
    # 1. Find related topics
    related_info = find_related_topics(query, tenant_id)
    
    # 2. If found, generate helpful response
    if related_info and related_info.get('found_topics'):
        topics = related_info['found_topics']
        
        response = f"""I don't have specific information about "{query}" 
        in the loaded documentation.

However, I found related information about:
{format_topics(topics)}

Would you like to know about any of these?"""
        
        return response
    
    # 3. Fallback to standard message
    return "I don't have information about this..."
```

### Search Algorithm

```python
def find_related_topics(query: str, tenant_id: str) -> Dict:
    # Extract key terms
    terms = ["configure", "email", "notifications"]
    
    # Search with each term
    related_docs = []
    for term in terms:
        docs = search(term, tenant_id)
        if docs_are_valid(docs):
            related_docs.extend(docs[:2])
    
    # Remove duplicates
    unique_docs = list(set(related_docs))
    
    # Extract topics using AI
    topics = extract_topics_from_docs(query, unique_docs)
    
    return {
        'found_topics': topics,
        'suggestion': format_suggestion(query, topics)
    }
```

---

## Integration Points

### RAG Module (`backend/llm/rag.py`)

```python
if context_is_empty:
    # NEW: Try to find related topics
    helpful_response = generate_not_found_response_with_hints(query, tenant_id)
    return {"response": helpful_response}
```

### Streaming Module (`backend/routers/streaming.py`)

```python
if not docs or doc_count == 0:
    # NEW: Try to find related topics
    helpful_message = generate_not_found_response_with_hints(query, tenant_id)
    yield f"data: {json.dumps({'type': 'content', 'content': helpful_message})}\n\n"
```

---

## Configuration

### Enable/Disable Feature

**To disable:**
```python
# In rag.py
if context_is_empty:
    # Comment out related topics search
    # helpful_response = generate_not_found_response_with_hints(...)
    
    # Use standard message
    return {"response": "I don't have information..."}
```

### Adjust Number of Topics

```python
# In related_topics_finder.py
def extract_topics_from_docs(...):
    # Change this line:
    for topic in topics[:3]:  # Shows 3 topics
    # To:
    for topic in topics[:5]:  # Shows 5 topics
```

### Adjust Search Depth

```python
# In find_related_topics()
for term in query_terms[:3]:  # Try 3 terms
    docs = search(term, tenant_id)
    related_docs.extend(docs[:2])  # Take 2 docs per term
```

---

## Performance Impact

### Additional Processing

**When no answer found:**
- Standard: ~0.5s (just returns "no info")
- With hints: ~2-3s (searches + extracts topics)

**When answer IS found:**
- No impact (feature doesn't run)

### Caching

Related topics are cached to improve performance:
```python
cache_key = f"{query[:100]}_{tenant_id}"
# Cached for repeated "no answer" queries
```

---

## User Experience Flow

### Flow 1: Direct Match Found
```
User: What is a Job?
→ Direct answer found
→ Returns answer immediately
→ No related topics search needed
```

### Flow 2: No Match, Related Topics Found
```
User: How do I configure email?
→ No direct answer
→ Searches for related topics
→ Finds "Notification Settings", "Alert Configuration"
→ Suggests these to user
→ User asks about one
→ Conversation continues!
```

### Flow 3: No Match, Nothing Related
```
User: How do I bake a cake?
→ No direct answer
→ Searches for related topics
→ Nothing found
→ Returns standard "no info" message
```

---

## Monitoring & Metrics

### Success Rate

Track how often related topics are found:
```sql
SELECT 
  COUNT(*) as no_answer_queries,
  SUM(CASE WHEN response LIKE '%However, I found related%' THEN 1 ELSE 0 END) as with_hints,
  (SUM(...) * 100.0 / COUNT(*)) as hint_success_rate
FROM chat_interactions
WHERE response LIKE '%don''t have%information%';
```

**Good Success Rate:** 50-70%
- Half of "no answer" queries get helpful hints

### User Engagement

Track if users follow the hints:
```sql
-- Check if user's next query is about suggested topics
SELECT 
  curr.query as original,
  next.query as follow_up,
  curr.response as hints_provided
FROM chat_interactions curr
JOIN chat_interactions next 
  ON next.conversation_id = curr.conversation_id
  AND next.message_order = curr.message_order + 1
WHERE curr.response LIKE '%However, I found related%';
```

**Good Engagement:** 30-40% follow-up rate
- Users actually explore the suggested topics

---

## Benefits

### For Users
✅ **No dead ends** - Always get some guidance
✅ **Discover related features** - Learn about similar topics
✅ **Natural navigation** - Guided to relevant content
✅ **Better UX** - Feel helped, not blocked

### For System
✅ **Improved engagement** - Fewer abandoned conversations
✅ **Better feedback** - Learn what's missing from docs
✅ **Reduced support load** - Users find related info themselves
✅ **Smart fallback** - Graceful handling of missing content

### For Admins
✅ **Identify gaps** - See what users ask but can't find
✅ **Improve documentation** - Know what to add
✅ **Track usage patterns** - Understand user needs
✅ **Quality metrics** - Measure hint effectiveness

---

## Testing

### Test Case 1: Related Topics Found

```python
def test_related_topics_found():
    query = "How do I setup email alerts?"
    tenant_id = "default"
    
    response = generate_not_found_response_with_hints(query, tenant_id)
    
    assert "I don't have specific information" in response
    assert "However, I found related" in response
    assert "Would you like to know" in response
```

### Test Case 2: No Related Topics

```python
def test_no_related_topics():
    query = "How do I bake a cake?"
    tenant_id = "default"
    
    response = generate_not_found_response_with_hints(query, tenant_id)
    
    assert "I don't have information about this" in response
    assert "However, I found related" not in response
```

### Test Case 3: Caching

```python
def test_caching():
    query = "How do I setup email?"
    tenant_id = "default"
    
    # First call
    response1 = get_related_topics_cached(query, tenant_id)
    
    # Second call (should be cached)
    response2 = get_related_topics_cached(query, tenant_id)
    
    assert response1 == response2
    # Second call should be much faster
```

---

## Future Enhancements

### 1. Clickable Suggestions

Make topics clickable in the frontend:
```jsx
{suggestedTopics.map(topic => (
  <button onClick={() => askAbout(topic)}>
    {topic}
  </button>
))}
```

### 2. Learning from Rejections

Track what users ask but can't find:
```sql
CREATE TABLE missing_topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query TEXT,
    found_related BOOLEAN,
    suggested_topics JSON,
    user_followed_up BOOLEAN,
    created_at TIMESTAMP
);
```

Use this to improve documentation.

### 3. Smart Topic Ranking

Rank suggested topics by relevance:
```python
# Score topics by:
# - Keyword overlap with query
# - Document frequency
# - User engagement history
topics_ranked = rank_by_relevance(topics, query)
```

### 4. Multi-Language Support

Translate suggestions to user's language:
```python
if user_language != 'en':
    topics = translate_topics(topics, user_language)
```

---

## Troubleshooting

### Issue: Too Many Irrelevant Suggestions

**Solution:**
1. Increase keyword overlap requirement
2. Use stricter search criteria
3. Adjust AI prompt for better topic extraction

### Issue: No Suggestions Ever

**Solution:**
1. Check if documents are loaded: `POST /documents/reload`
2. Verify search is working: Test with known terms
3. Check logs for errors

### Issue: Slow Performance

**Solution:**
1. Reduce number of search terms: `query_terms[:2]` instead of `[:3]`
2. Reduce docs per term: `docs[:1]` instead of `[:2]`
3. Enable more aggressive caching

---

## Summary

The Related Topics Hints feature transforms "dead end" responses into **helpful guidance**:

**Before:** "I don't have information about this." ❌

**After:** "I don't have that specific info, but here are related topics you can explore!" ✅

This creates a **better user experience** by:
- 🎯 Always providing value (even when direct answer isn't available)
- 🔍 Helping users discover related features
- 💡 Guiding natural exploration of documentation
- 😊 Preventing frustration from dead ends

The feature is **smart** (AI-powered), **fast** (cached), and **graceful** (falls back cleanly) - a perfect addition to the conversational AI system! 🚀

