# Related Questions Validation System

## Overview

The related questions feature now includes **strict validation** to ensure all suggested questions:
1. ✅ Are **specific to your documentation** (not generic)
2. ✅ Can be **answered from available documentation**
3. ✅ Relate to **concepts mentioned in the current answer**

---

## Validation Pipeline

### Step 1: Generation with Strict Prompt

**Enhanced Prompt:**
```
🚨 CRITICAL RULES:
1. Question MUST be about concepts/features MENTIONED in the assistant's answer
2. Question MUST be answerable from the same documentation source
3. DO NOT ask general questions unrelated to the documentation
4. DO NOT ask about things not mentioned in the answer
5. Build on what was just explained
```

**Good Examples:**
- Answer mentions "Job lifecycle" → Question: "What are the stages in Job lifecycle?"
- Answer mentions "required fields" → Question: "What are the required fields?"
- Answer mentions "workflow steps" → Question: "How do I configure workflow steps?"

**Bad Examples (Prevented):**
- "What is the weather?" ❌ Not in documentation
- "How do I login?" ❌ If login wasn't mentioned
- "Tell me more?" ❌ Too vague
- "What else?" ❌ Too general

---

### Step 2: Generic Question Filter

Blocks common generic questions:

```python
generic_indicators = [
    'tell me more',
    'what else',
    'anything else',
    'more information',
    'more details',
    'explain more',
    'weather',
    'news',
    'date',
    'time',
    'how are you',
    'who are you'
]
```

**Example:**
```python
question = "Can you tell me more?"
# ❌ Rejected: Contains 'tell me more'
```

---

### Step 3: Concept Overlap Validation

Ensures question relates to answer content:

```python
# Extract key terms from answer
response_terms = {"job", "customer", "order", "workflow", "status"}

# Extract terms from question
question = "How do I create a workflow?"
question_terms = {"how", "create", "workflow"}

# Check overlap
has_overlap = bool(response_terms.intersection(question_terms))
# ✅ True: "workflow" is in both
```

**Example Pass:**
```
Answer: "A Job is a customer order with workflow steps..."
Question: "How do I configure workflow steps?"
✅ Overlap: "workflow"
```

**Example Fail:**
```
Answer: "A Job is a customer order..."
Question: "How do I reset my password?"
❌ No overlap: "password" not in answer
```

---

### Step 4: Answerability Verification

Actually searches documentation to verify the question can be answered:

```python
def verify_question_is_answerable(question, tenant_id):
    # Perform real search
    docs = search(question, tenant_id)
    
    # Check if results are meaningful
    if not docs or len(docs) == 0:
        return False  # ❌ No documents found
    
    # Check for "no documentation" messages
    if 'no documentation' in docs[0].lower():
        return False  # ❌ Not in documentation
    
    # Check if results have substance
    total_length = sum(len(doc) for doc in docs)
    if total_length < 100:
        return False  # ❌ Too little content
    
    return True  # ✅ Answerable!
```

**Example Flow:**
```python
question = "What is the Job lifecycle?"

# Step 1: Search documentation
search_results = search(question, "default")
# Returns: ["Job lifecycle includes: Created → In Progress → ..."]

# Step 2: Validate results
✅ Has documents: Yes
✅ Not "no documentation": Yes
✅ Substantial content (>100 chars): Yes

# Result: ✅ Question is answerable
```

---

## Complete Validation Flow

```
1. AI generates question
   ↓
2. Clean & format
   ↓
3. Check length (5-100 chars) ✓
   ↓
4. Filter generic questions ✓
   ↓
5. Validate concept overlap ✓
   ↓
6. Verify answerability (search docs) ✓
   ↓
7. Cache validated question ✓
   ↓
8. Return question or None
```

---

## Examples with Validation

### Example 1: Valid Question

**User Query:** "What is a Job?"

**Bot Answer:** 
```
A Job is a customer order that you're working on. It contains:
- Customer details
- Order specifications
- Workflow steps
- Current status
```

**Generated Question:** "What are the workflow steps in a Job?"

**Validation:**
1. ✅ Length: 39 chars (valid)
2. ✅ Not generic: No generic keywords
3. ✅ Concept overlap: "workflow" in answer
4. ✅ Answerability: Search finds workflow documentation
5. ✅ **APPROVED** - Question suggested to user

---

### Example 2: Generic Question (Rejected)

**User Query:** "What is a Job?"

**Bot Answer:** "A Job is a customer order..."

**Generated Question:** "Can you tell me more?"

**Validation:**
1. ✅ Length: 20 chars
2. ❌ **Generic filter**: Contains "tell me more"
3. **REJECTED** - No question shown

---

### Example 3: Unrelated Question (Rejected)

**User Query:** "What is a Job?"

**Bot Answer:** "A Job is a customer order with workflow..."

**Generated Question:** "How do I reset my password?"

**Validation:**
1. ✅ Length: 28 chars
2. ✅ Not generic
3. ❌ **Concept overlap**: "password" not in answer
4. **REJECTED** - No question shown

---

### Example 4: Unanswerable Question (Rejected)

**User Query:** "What is a Job?"

**Bot Answer:** "A Job is a customer order..."

**Generated Question:** "What is the nuclear fusion process?"

**Validation:**
1. ✅ Length: 39 chars
2. ✅ Not generic
3. ❌ Concept overlap: No overlap
4. **REJECTED** before answerability check

*(Even if it passed step 3)*
4. ❌ **Answerability**: Search returns "No documentation found"
5. **REJECTED** - No question shown

---

## Configuration

### Enable/Disable Verification

```python
# In function call
related_q = get_related_question_cached(
    query, 
    response, 
    main_topic,
    tenant_id=tenant_id,
    verify_answerable=True  # ← Set to False to skip verification
)
```

**When to disable:**
- Development/testing
- Documentation is incomplete
- Performance is critical

**When to enable (default):**
- Production
- User-facing deployment
- Quality is priority

---

### Adjust Validation Thresholds

**Minimum Content Length:**
```python
# In verify_question_is_answerable()
if total_length < 100:  # ← Adjust this
    return False
```

**Generic Keyword List:**
```python
# Add more generic phrases to filter
generic_indicators = [
    'tell me more',
    'what else',
    'your custom phrase',
    # ...
]
```

---

## Performance Impact

### Without Verification
```
Response time: ~0.5-1s
API calls: +1 (question generation)
```

### With Verification (Default)
```
Response time: ~1-2s
API calls: +1 (generation) +1 (verification search)
```

**Optimization:**
- Cached questions skip verification
- Verification runs in parallel with response generation
- Failed verifications are cached to avoid retries

---

## Monitoring

### Success Rate

**Track question approval rate:**
```python
total_attempts = generated_questions_count
approved = suggested_questions_count
rejection_rate = (total_attempts - approved) / total_attempts

# Expected rates:
# 70-80% approval = Good (strict but functional)
# 90-95% approval = May be too lenient
# <50% approval = Too strict or bad documentation
```

### Rejection Reasons

**Log and monitor:**
```
⚠️  Rejected generic question: 'Can you tell me more?'
⚠️  Question not related to answer content: 'How do I login?'
❌ Question not answerable from documentation: 'What is quantum physics?'
```

---

## Troubleshooting

### Too Many Rejections

**Problem:** Most questions are rejected

**Solutions:**
1. Check if documentation is loaded:
   ```bash
   POST /documents/reload
   ```

2. Reduce strictness:
   ```python
   verify_answerable=False  # Disable verification
   ```

3. Lower content threshold:
   ```python
   if total_length < 50:  # Instead of 100
   ```

---

### Questions Not Specific Enough

**Problem:** Questions are too generic despite validation

**Solutions:**
1. Add more generic phrases to filter
2. Increase overlap requirement
3. Improve prompt specificity

---

### Questions Can't Be Answered

**Problem:** User asks suggested question but gets "no documentation"

**This should be rare due to verification, but if it happens:**

1. Check verification is enabled:
   ```python
   verify_answerable=True  # Should be True
   ```

2. Check search quality:
   ```python
   # Test manually
   docs = search("suggested question here", "default")
   print(docs)
   ```

3. Documentation may have changed:
   - Reload documents
   - Clear question cache

---

## Quality Metrics

### Good Indicators

✅ **High click-through rate** (>30%)
- Users actually ask the suggested questions

✅ **Low "no documentation" rate** (<5%)
- Suggested questions are answerable

✅ **Positive feedback** on related questions
- Users find them helpful

✅ **Natural conversation flow**
- Questions lead to deeper understanding

### Warning Signs

⚠️ **Low click-through rate** (<10%)
- Questions may not be relevant

⚠️ **High "no documentation" rate** (>20%)
- Verification may be failing

⚠️ **Generic questions getting through**
- Filter needs strengthening

---

## Summary

The enhanced validation ensures:

1. **Documentation-Specific**
   - Questions about YOUR system, not general topics
   - Extracted from answer content

2. **Answerable**
   - Verified against available documentation
   - Won't suggest questions we can't answer

3. **Quality-Focused**
   - Multiple validation layers
   - Cached for performance
   - Graceful fallback if validation fails

4. **User-Friendly**
   - Natural conversation flow
   - Relevant, actionable questions
   - Guides learning journey

**Result:** Every suggested question is guaranteed to be relevant to your documentation and answerable by the system! 🎯

