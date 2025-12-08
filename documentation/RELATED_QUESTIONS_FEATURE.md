# Related Questions Feature

## Overview

The chatbot now automatically suggests contextually relevant follow-up questions at the end of each response to guide natural conversation flow.

**Example:**

```
User: What is a Job?

Bot: A Job is a customer order that you're working on. It's the container 
that holds everything about that order... Think of a job as a project folder - 
everything related to that customer order goes in that job.

---

💡 You might also want to ask: What is the Job lifecycle?
```

---

## How It Works

### 1. AI-Powered Generation

After each response, the system:
1. Analyzes the user's question
2. Analyzes the bot's answer
3. Uses the extracted main topic (from context system)
4. Generates ONE relevant follow-up question

**Algorithm:**
```python
query = "What is a Job?"
response = "A Job is a customer order..."
main_topic = "Job"  # Extracted by context system

related_question = generate_related_question(query, response, main_topic)
# Returns: "What is the Job lifecycle?"
```

### 2. Smart Question Generation

The AI generates questions that:
- ✅ Build naturally on current topic
- ✅ Explore deeper or adjacent concepts
- ✅ Are specific to documentation (not generic)
- ✅ Are short and actionable (max 10 words)

**Examples of Good Questions:**
- "How do I create a new customer?"
- "What are the required fields?"
- "What happens if validation fails?"
- "How do I view the workflow status?"

**Bad Questions (System Avoids):**
- "Tell me more?" (too vague)
- "What else can you do?" (too generic)
- "Explain in detail?" (not specific)

### 3. Context Integration

Works seamlessly with the context tracking system:

```
User: What is a Job?
Bot: [Explains Job] + "💡 What is the Job lifecycle?"
     ^main_topic: "Job"

User: Lifecycle  [clicks on suggested question or types]
Bot: [System combines "Job" + "Lifecycle" = searches for "Job Lifecycle"]
     [Explains Job Lifecycle] + "💡 How do I create a Job?"
     ^main_topic: "Job Lifecycle"
```

---

## Technical Implementation

### Backend Components

#### 1. Related Questions Module
**File:** `backend/llm/related_questions.py`

**Key Functions:**

```python
# Generate single related question
generate_related_question(query, response, main_topic)

# Generate with caching (optimized)
get_related_question_cached(query, response, main_topic)

# Generate multiple questions (for future features)
generate_related_questions_batch(queries, responses, limit=3)
```

#### 2. Integration Points

**RAG Module** (`backend/llm/rag.py`):
```python
# After generating response
related_question = get_related_question_cached(query, answer, main_topic)

if related_question:
    answer += f"\n\n---\n\n💡 **You might also want to ask:** {related_question}"
```

**Streaming Module** (`backend/routers/streaming.py`):
```python
# Generate question
related_question = get_related_question_cached(query, full_response, main_topic)

# Stream it after main response
if related_question:
    yield separator
    yield question_text
```

### Response Format

**Text Format:**
```
[Main answer content]

---

💡 **You might also want to ask:** [Question]
```

**Markdown Rendering:**
```markdown
[Main answer]

---

💡 **You might also want to ask:** What is the Job lifecycle?
```

The `---` creates a visual separator, and the 💡 emoji makes it stand out.

---

## Configuration & Optimization

### 1. Caching

Questions are cached to avoid duplicate API calls:

```python
_question_cache = {}

# Cache key: first 50 chars of query + main_topic
cache_key = f"{query[:50]}_{main_topic or ''}"

# Cache limit: 100 entries (FIFO eviction)
```

**Benefits:**
- ⚡ Faster response for similar questions
- 💰 Reduced OpenAI API costs
- 🔄 Consistent questions for same context

### 2. Timeout & Fallback

```python
timeout=5  # 5 second timeout for question generation
```

**Behavior:**
- If generation fails → Continue without related question
- If timeout → No related question
- No impact on main response quality

### 3. Validation

Generated questions are validated:
- ✅ Length: 5-100 characters
- ✅ Format: Ends with `?`
- ✅ Content: Not empty or malformed
- ❌ Invalid → Discarded silently

---

## API Response Structure

### Regular Chat Endpoint

```json
{
  "response": "[Answer]\n\n---\n\n💡 **You might also want to ask:** [Question]",
  "session_id": "abc-123",
  "has_context": true,
  "main_topic": "Job",
  "related_question": "What is the Job lifecycle?"
}
```

### Streaming Endpoint

**Event Sequence:**
```
data: {"type": "content", "content": "[Main answer text]"}
data: {"type": "content", "content": "\n\n---\n\n"}
data: {"type": "content", "content": "💡 **You might also want to ask:** [Question]"}
data: {"type": "complete", "has_related_question": true, ...}
```

---

## Frontend Integration

### Displaying Related Questions

The question is already included in the response markdown, so it renders automatically:

```jsx
<MarkdownText text={message.content} />
// Renders:
// [Answer]
// ---
// 💡 **You might also want to ask:** What is the Job lifecycle?
```

### Making Questions Clickable (Optional Enhancement)

To make related questions clickable in the frontend:

```jsx
// Parse related questions from response
function extractRelatedQuestion(response) {
  const match = response.match(/💡 \*\*You might also want to ask:\*\* (.+)/);
  return match ? match[1] : null;
}

// Render as clickable
{relatedQuestion && (
  <div className="related-question">
    <button onClick={() => handleSend(relatedQuestion)}>
      💡 {relatedQuestion}
    </button>
  </div>
)}
```

---

## Examples

### Example 1: Job Management Flow

```
👤 User: What is a Job?
🤖 Bot: A Job is a customer order that you're working on...
      💡 What is the Job lifecycle?

👤 User: Lifecycle  [or clicks the question]
🤖 Bot: The Job lifecycle includes: Created → In Progress → Quality Check...
      💡 How do I create a new Job?

👤 User: How do I create a new Job?
🤖 Bot: To create a new Job: 1. Navigate to Jobs module...
      💡 What are the required fields for a Job?
```

### Example 2: Module Exploration

```
👤 User: Tell me about the Workflow Module
🤖 Bot: The Workflow Module manages your manufacturing processes...
      💡 How do I create a workflow template?

👤 User: How do I create a workflow template?
🤖 Bot: To create a workflow template: 1. Open Workflow Designer...
      💡 What are the different workflow step types?

👤 User: What are the different workflow step types?
🤖 Bot: Workflow steps include: Operation, Inspection, Movement...
      💡 How do I assign workers to workflow steps?
```

---

## Monitoring & Analytics

### Logs

Related question generation is logged:

```
✅ Created session: abc-123
🏷️  Extracted topic: 'Job'
💡 Generated related question: 'What is the Job lifecycle?'
💾 Message saved to session
```

### Metrics to Track

**Success Rate:**
```sql
SELECT 
  COUNT(*) as total_responses,
  SUM(CASE WHEN response LIKE '%💡 **You might also want to ask:**%' THEN 1 ELSE 0 END) as with_related_q,
  (SUM(...) * 100.0 / COUNT(*)) as success_rate
FROM chat_interactions
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY);
```

**Click-Through Rate (if clickable):**
- Track how often users ask the suggested question next
- Measure engagement improvement

---

## Performance Impact

### API Calls

**Before:**
- 1 embedding API call (search)
- 1 chat completion (response)
- 1 context extraction (optional)

**After:**
- 1 embedding API call (search)
- 1 chat completion (response)
- 1 context extraction (optional)
- **+1 chat completion (related question)** ← NEW

**Mitigation:**
- ✅ Caching reduces duplicate calls
- ✅ Short max_tokens (30) = fast generation
- ✅ 5s timeout = non-blocking
- ✅ Fails silently = no impact on main response

### Response Time

**Impact:** +0.5-2s average (if cache miss)
**User Experience:** Improved (better guidance)

**Optimization:**
```python
# Use cached version
related_q = get_related_question_cached(...)  # ⚡ Instant if cached

# Parallel generation (future enhancement)
asyncio.create_task(generate_related_question(...))  # Non-blocking
```

---

## Testing

### Unit Test

```python
def test_related_question_generation():
    query = "What is a Job?"
    response = "A Job is a customer order..."
    main_topic = "Job"
    
    related_q = generate_related_question(query, response, main_topic)
    
    assert related_q is not None
    assert len(related_q) >= 5
    assert len(related_q) <= 100
    assert related_q.endswith('?')
    assert 'job' in related_q.lower() or 'workflow' in related_q.lower()
```

### Integration Test

```python
async def test_streaming_with_related_question():
    # Send query
    response = await client.post('/chat/query/stream', json={
        'query': 'What is a Job?',
        'tenant_id': 'default'
    })
    
    # Collect streamed response
    full_response = ""
    async for line in response:
        if line.startswith('data: '):
            data = json.loads(line[6:])
            if data['type'] == 'content':
                full_response += data['content']
    
    # Verify related question is present
    assert '💡 **You might also want to ask:**' in full_response
    assert full_response.count('?') >= 2  # Original Q + Related Q
```

---

## Future Enhancements

### 1. Multiple Related Questions

Generate 2-3 questions instead of one:

```
---

💡 You might also want to ask:
• What is the Job lifecycle?
• How do I create a Job?
• What are Job statuses?
```

### 2. Learning from Clicks

Track which suggested questions users click:

```sql
CREATE TABLE related_question_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_query TEXT,
    related_question TEXT,
    was_clicked BOOLEAN,
    created_at TIMESTAMP
);
```

Use this to improve question generation.

### 3. Conversation-Aware Questions

Generate questions based on entire conversation:

```python
# Instead of single Q&A
questions = generate_from_conversation_history(
    conversation_history,
    current_topic
)
```

### 4. Smart Positioning

Place questions contextually:
- After definitions → "How do I use this?"
- After how-to → "What are best practices?"
- After troubleshooting → "How do I prevent this?"

---

## Troubleshooting

### Related Questions Not Appearing

**Check logs:**
```
⚠️  Could not generate related question: [error]
```

**Common causes:**
1. OpenAI API connection issue
2. Timeout (>5s generation)
3. Invalid response format
4. Cache key collision

**Solution:**
- Check OpenAI API key
- Increase timeout if needed
- Clear cache: `_question_cache.clear()`

### Questions Not Relevant

**Improve generation:**
```python
# Adjust temperature
temperature=0.7  # Lower = more focused, Higher = more creative

# Provide better context
prompt = f"Based on {main_topic} discussion about {query}..."
```

### Performance Issues

**Optimize:**
1. Increase cache size: `max_cache=500`
2. Pre-generate for common questions
3. Use async generation: `asyncio.create_task()`

---

## Summary

✅ **Automatic related questions** at end of responses  
✅ **Context-aware** using main topic extraction  
✅ **Smart caching** to reduce API calls  
✅ **Graceful fallback** if generation fails  
✅ **No breaking changes** to existing functionality  
✅ **Improves UX** by guiding conversation flow  

The feature seamlessly enhances conversations without disrupting current behavior!

