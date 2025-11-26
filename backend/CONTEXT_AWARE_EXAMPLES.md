# Context-Aware Clarification Examples

This document shows real examples of how the improved system maintains context.

## Example 1: Purchasing Module

### User Query
```
"how to purchasing"
```

### What System Does
1. **Detects Intent**: `how_to` (user wants to know how to do something)
2. **Extracts Topic**: `Purchasing` (user is asking about Purchasing module)
3. **Generates Contextual Questions**:
   - "What specific task do you want to perform in **Purchasing**?"
   - "Are you asking about creating, updating, or viewing something in **Purchasing**?"

### Why This is Better
- ✅ Acknowledges user mentioned Purchasing
- ✅ Stays focused on Purchasing module
- ✅ Helps narrow down the specific task
- ❌ Doesn't ask "which module?" (user already said Purchasing!)

---

## Example 2: Sales Setup

### User Query
```
"setup sales"
```

### What System Does
1. **Detects Intent**: `setup` (user wants to configure/setup)
2. **Extracts Topic**: `Sales` (user is working with Sales)
3. **Generates Contextual Questions**:
   - "What part of **Sales** are you trying to set up?"
   - "Are you doing initial setup or configuration of **Sales**?"
   - "What step are you currently on?"

### Why This is Better
- ✅ Keeps Sales in focus
- ✅ Asks relevant setup questions
- ✅ Acknowledges the setup context
- ❌ Doesn't change subject to other modules

---

## Example 3: Inventory Troubleshooting

### User Query
```
"inventory not working"
```

### What System Does
1. **Detects Intent**: `troubleshoot` (user has a problem)
2. **Extracts Topic**: `Inventory` (the problem is with Inventory)
3. **Generates Contextual Questions**:
   - "What specifically is not working in **Inventory**?"
   - "What were you trying to do in **Inventory** when this happened?"
   - "What happens when you try? (error message, unexpected result, etc.)"

### Why This is Better
- ✅ Maintains Inventory focus
- ✅ Asks troubleshooting-specific questions
- ✅ Gets details about the Inventory problem
- ❌ Doesn't ask about unrelated features

---

## Example 4: Vague "Help" Query

### User Query
```
"help"
```

### What System Does
1. **Detects Intent**: `general` (very vague)
2. **Extracts Topic**: None detected
3. **Generates Contextual Questions**:
   - "What specific topic would you like to know about?"
   - "Which module or feature are you interested in?"
   - "What are you trying to accomplish?"

### Why This is Appropriate
- ✅ No prior context to maintain
- ✅ Asks general exploration questions
- ✅ Helps user articulate their need
- ✅ Doesn't assume any specific module

---

## Example 5: Create Something

### User Query
```
"create in purchasing"
```

### What System Does
1. **Detects Intent**: `create` (user wants to create something)
2. **Extracts Topic**: `Purchasing`
3. **Generates Contextual Questions**:
   - "What do you want to create in **Purchasing**?"
   - "Are you trying to create a new purchase order, vendor, or requisition in **Purchasing**?"

### Why This is Better
- ✅ Understands creation intent
- ✅ Stays in Purchasing context
- ✅ Suggests common creation options
- ❌ Doesn't ask about unrelated modules

---

## Example 6: Error Message

### User Query
```
"error in sales"
```

### What System Does
1. **Detects Intent**: `troubleshoot` (error = problem)
2. **Extracts Topic**: `Sales`
3. **Generates Contextual Questions**:
   - "What error message are you seeing in **Sales**?"
   - "When does this error occur in **Sales**? (e.g., when creating a record, when saving, etc.)"
   - "Which screen in **Sales** are you working in?"

### Why This is Better
- ✅ Recognizes it's an error situation
- ✅ Maintains Sales context
- ✅ Asks error-specific questions
- ❌ Doesn't drift to other topics

---

## Example 7: Clear Question (No Clarification Needed)

### User Query
```
"What are the main features of the Purchasing module in Verax ERP?"
```

### What System Does
1. **Detects Intent**: `what_is` (definition/list question)
2. **Extracts Topic**: `Purchasing`
3. **Clarity Check**: Query is relatively clear (has context, specific module, clear intent)
4. **Decision**: Provide answer directly (may do quick AI check for edge cases)

### Result
- ✅ No unnecessary clarification
- ✅ System recognizes query has enough context
- ✅ Proceeds to answer the question

---

## Example 8: Multiple Topics

### User Query
```
"tell me about sales and purchasing"
```

### What System Does
1. **Detects Intent**: `general` (multiple topics)
2. **Extracts Topics**: `Sales`, `Purchasing`
3. **Recognizes**: Multiple topics in one query
4. **Generates Contextual Questions**:
   - "Let's focus on one topic at a time. Which would you like to discuss first: **Sales** or **Purchasing**?"
   - "Would you like me to address each topic separately?"

### Why This is Better
- ✅ Recognizes multiple topics
- ✅ Lists the exact topics mentioned (Sales, Purchasing)
- ✅ Offers to handle them separately
- ❌ Doesn't just say "pick one module" (specifies which ones)

---

## Key Principles

### ✅ DO
1. **Detect intent** before asking questions
2. **Extract topics** mentioned by user
3. **Maintain context** in all clarifying questions
4. **Use specific** module/feature names user mentioned
5. **Ask relevant** questions based on intent type

### ❌ DON'T
1. Ask about things user already specified
2. Change the subject or module
3. Use generic questions that ignore context
4. Assume different module than mentioned
5. Lose track of conversation topic

---

## Testing Your Own Queries

To test any query:

```python
from llm.clarity_detector import analyze_query_clarity

query = "your test query here"
result = analyze_query_clarity(query)

print(f"Intent: {result['query_type']}")
print(f"Clear: {result['is_clear']}")
print(f"Score: {result['clarity_score']}")

if not result['is_clear']:
    print("Clarifying Questions:")
    for q in result['suggestions']:
        print(f"  - {q}")
```

Or use the test script:
```bash
cd backend
python test_contextual_clarity.py
```

---

## Summary

The system now:
- 🎯 **Understands** what users are asking about
- 🎯 **Maintains** the conversation context
- 🎯 **Generates** relevant, focused clarifying questions
- 🎯 **Doesn't mislead** or change topics
- 🎯 **Stays helpful** and contextually appropriate

**Result**: Much better user experience! 🎉

