# 🔧 Fix: "name 'x_column' is not defined" Error

## 🐛 Problem Identified

**Error**: `name 'x_column' is not defined`

### Root Cause
The error occurred in `database_query_service.py` where template placeholders like `{x_column}`, `{table}`, `{amount_column}` were being used inside Python f-strings as examples for the LLM prompt. Python was trying to evaluate these as variables, causing a `NameError`.

### Location
```python
# Lines 151-165 and 217-219 in database_query_service.py
system_prompt = f"""...
- "which X has/have more than N Y" = SELECT {x_column}, COUNT(*) ...
                                                   ^^^^^^^^^ 
                                    Python tries to find this variable!
```

## ✅ Solution Applied

### Fix 1: Escape Template Placeholders in System Prompt

**Before** (Lines 151-165):
```python
GENERIC Patterns (adapt to actual table/column names from schema):
- "show X" = SELECT * FROM {table_about_X}
- "count X" = SELECT COUNT(*) as total FROM {table_about_X}
- "which X has/have more than N Y" = SELECT {x_column}, COUNT(*) as count FROM {table} GROUP BY {x_column} HAVING COUNT(*) > N
```

**After**:
```python
GENERIC Patterns (adapt to actual table/column names from schema):
- "show X" = SELECT * FROM {{table_about_X}}
- "count X" = SELECT COUNT(*) as total FROM {{table_about_X}}
- "which X has/have more than N Y" = SELECT {{x_column}}, COUNT(*) as count FROM {{table}} GROUP BY {{x_column}} HAVING COUNT(*) > N
```

**Explanation**: Double braces `{{}}` escape to single braces `{}` in f-string output, making them literal text instead of variable references.

### Fix 2: Escape Template Placeholders in User Prompt

**Before** (Lines 217-219):
```python
9. For "which/what X has/have more than N Y": Use GROUP BY {x_column} HAVING COUNT(*) > N
10. For "which/what X has/have less than N Y": Use GROUP BY {x_column} HAVING COUNT(*) < N
11. For "how many Y per X": Use GROUP BY {x_column} with COUNT(*)
```

**After**:
```python
9. For "which/what X has/have more than N Y": Use GROUP BY {{x_column}} HAVING COUNT(*) > N
10. For "which/what X has/have less than N Y": Use GROUP BY {{x_column}} HAVING COUNT(*) < N
11. For "how many Y per X": Use GROUP BY {{x_column}} with COUNT(*)
```

### Fix 3: Proper Variable Interpolation

**Before** (Line 193):
```python
context_str += "Example: 'give me this data with city' means: {last_sql_query} but add 'city' to SELECT\n"
```

**After**:
```python
context_str += f"Example: 'give me this data with city' means: {last_sql_query} but add 'city' to SELECT\n"
```

**Explanation**: Added `f` prefix to properly interpolate the actual `last_sql_query` variable value.

## 🎯 Complete List of Changes

### Modified File: `backend/llm/database_query_service.py`

1. **Line 151-165**: Escaped all template placeholders in system prompt
   - `{table_about_X}` → `{{table_about_X}}`
   - `{amount_column}` → `{{amount_column}}`
   - `{table}` → `{{table}}`
   - `{y_field}` → `{{y_field}}`
   - `{location_field}` → `{{location_field}}`
   - `{country_field}` → `{{country_field}}`
   - `{date_field}` → `{{date_field}}`
   - `{x_column}` → `{{x_column}}`

2. **Line 217-219**: Escaped template placeholders in user prompt
   - `{x_column}` → `{{x_column}}` (3 occurrences)

3. **Line 193**: Fixed variable interpolation
   - Added `f` prefix for proper string formatting

## 🔍 Verification

### Test 1: Check Prompt Generation
```python
# The prompts should now contain literal {x_column} text
# Not try to evaluate it as a Python variable
```

### Test 2: Run Query
```bash
# Test a query that triggers the aggregation pattern
"which city has more than 3 vendors"
```

### Expected Result
✅ No `NameError: name 'x_column' is not defined`
✅ Prompt correctly shows: `GROUP BY {x_column}` (literal text)
✅ SQL generation completes successfully

## 📊 Comparison with .NET Reference Code

### .NET Implementation (LlmPromptBuilder.cs)
```csharp
// .NET uses StringBuilder with simple string concatenation
var sb = new StringBuilder();
sb.AppendLine("You are a SQL expert...");
sb.AppendLine("# Instructions:");
sb.AppendLine("- Return ONLY the raw SQL query");
// No template variables - just plain text instructions
```

### Python Implementation (Fixed)
```python
# Python uses f-strings with escaped braces for examples
system_prompt = f"""You are a SQL expert...
# Instructions:
- Example pattern: SELECT {{x_column}} FROM {{table}}
# This shows {x_column} as literal text to the LLM
"""
```

**Key Difference**: 
- .NET doesn't use template placeholders in prompts
- Python can use them but must escape braces in f-strings: `{{placeholder}}`

## 🛡️ Prevention Strategy

### Rule 1: Always Escape Template Examples in F-Strings
```python
# ❌ BAD - Python will try to evaluate {variable}
prompt = f"Example: SELECT {x_column} FROM {table}"

# ✅ GOOD - Escaped braces become literal text
prompt = f"Example: SELECT {{x_column}} FROM {{table}}"

# ✅ ALTERNATIVE - Use regular strings (no f prefix) when no actual variables needed
prompt = "Example: SELECT {x_column} FROM {table}"
```

### Rule 2: Only Use Single Braces for Real Variables
```python
# ✅ CORRECT - This IS a real Python variable
query = f"Current Question: {natural_language_query}"
context = f"Previous SQL: {last_sql_query}"

# ✅ CORRECT - This is just an example for the LLM
instruction = f"Pattern: SELECT {{column_name}} FROM {{table_name}}"
```

### Rule 3: Lint Check for Unescaped Template Variables
```bash
# Search for potential issues
grep -n "= f\".*{[a-z_]*}" database_query_service.py
# Review each match to ensure it's either:
# 1. A real Python variable, OR
# 2. Properly escaped with double braces
```

## 📝 Testing Checklist

- [x] Linter shows no errors
- [x] F-string template variables properly escaped
- [x] Real Python variables properly interpolated
- [ ] Test query: "count vendors by city" ← Should work now
- [ ] Test query: "which city has more than 3 vendors" ← Should work now
- [ ] Test query: "show total by country" ← Should work now
- [ ] Server restart and integration test

## 🚀 Deployment Steps

1. **Stop backend server** (if running)
2. **Verify changes** are in `database_query_service.py`
3. **Restart backend server**:
   ```bash
   cd backend
   python -m uvicorn app:app --reload --port 8000
   ```
4. **Test the fix** with queries that use aggregation:
   - "count tickets by city"
   - "which vendor has more than 5 orders"
   - "show total by country"

## ✅ Status

- [x] **Root cause identified**: Unescaped braces in f-strings
- [x] **Solution implemented**: All template placeholders escaped
- [x] **Linter verification**: No errors
- [x] **Code review**: Matches .NET pattern
- [ ] **Integration testing**: Awaiting server restart
- [ ] **User verification**: Awaiting confirmation

## 📚 Related Documentation

- Python f-strings: https://docs.python.org/3/reference/lexical_analysis.html#f-strings
- Escaping braces in f-strings: Use `{{` and `}}` for literal braces
- .NET reference: `server/AnalyticsChatbot.API/Services/LlmPromptBuilder.cs`

---

**Fixed By**: AI Assistant
**Date**: December 16, 2025
**Status**: ✅ Complete - Ready for Testing


