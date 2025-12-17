# Strict Auto Mode - Flow Diagram

## Overview

Visual representation of how the system handles queries in different modes.

## Mode Selection Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Submits Query                           │
│                  "How to reset password?"                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  Which Source Mode?    │
            └────────────┬───────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
  ┌─────────┐      ┌─────────┐    ┌──────────┐
  │  AUTO   │      │DOCUMENTS│    │ DATABASE │
  │ (STRICT)│      │(RAG+LLM)│    │(SQL Gen) │
  └────┬────┘      └────┬────┘    └────┬─────┘
       │                │               │
       │                │               │
   [See below]   [Traditional]   [Traditional]
                    Flow             Flow
```

## Strict Auto Mode Flow (NEW)

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTO MODE SELECTED                           │
│              🔒 STRICT MODE ACTIVATED                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │ Load Strict Matcher    │
            │ (Historical Q&A from   │
            │  Database)             │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │ Calculate Similarity   │
            │ Using ML Algorithms:   │
            │ • Semantic Search      │
            │ • TF-IDF               │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  Similarity ≥ 85%?     │
            └────────────┬───────────┘
                         │
                    ┌────┴────┐
                    │         │
                   YES       NO
                    │         │
                    ▼         ▼
        ┌──────────────┐  ┌──────────────────┐
        │ Return Match │  │ Return "No Info" │
        │ From Database│  │ Message          │
        │              │  │                  │
        │ ✅ Source:   │  │ ❌ Source:       │
        │  exact_match │  │  no_match        │
        └──────────────┘  └──────────────────┘
                │                 │
                │                 │
                ▼                 ▼
        ┌──────────────────────────────────┐
        │    NO LLM GENERATION OCCURS      │
        │    NO EXTERNAL KNOWLEDGE ADDED   │
        └──────────────────────────────────┘
```

## Traditional Document Mode Flow (Unchanged)

```
┌─────────────────────────────────────────────────────────────────┐
│                 DOCUMENTS MODE SELECTED                         │
│           (User explicitly requests RAG)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │ Search Vector Database │
            │ (Pinecone/Memory)      │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │ Get Top 5 Documents    │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  Pass to GPT with      │
            │  Context + Instructions│
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  GPT Generates Answer  │
            │  (Based on context)    │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  Return Generated      │
            │  Response              │
            └────────────────────────┘
```

## Traditional Database Mode Flow (Unchanged)

```
┌─────────────────────────────────────────────────────────────────┐
│                 DATABASE MODE SELECTED                          │
│         (User explicitly requests SQL query)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  Get Database Schema   │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │ Convert NL to SQL      │
            │ (Using GPT)            │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  Execute SQL Query     │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  Return Query Results  │
            └────────────────────────┘
```

## Similarity Matching Detail

```
┌─────────────────────────────────────────────────────────────────┐
│               User Query: "How to reset password?"              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  Load Historical Q&A:  │
            │                        │
            │  Q1: "Reset password?" │───── Similarity: 0.95 ✅
            │  Q2: "Change password?"│───── Similarity: 0.88 ✅
            │  Q3: "User creation?"  │───── Similarity: 0.45 ❌
            │  Q4: "Weather today?"  │───── Similarity: 0.12 ❌
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  Filter by Threshold   │
            │  (Keep only ≥ 0.85)    │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  Best Match: Q1        │
            │  Similarity: 0.95      │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  Return Q1's Answer    │
            │  (From Database)       │
            └────────────────────────┘
```

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                             │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SMART CHAT ROUTER                            │
│                 (smart_chat.py)                                 │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ if source == "auto":                                     │  │
│  │    ┌─────────────────────────────────────────────────┐   │  │
│  │    │ 🔒 STRICT MODE                                  │   │  │
│  │    │                                                  │   │  │
│  │    │ 1. Initialize Strict Matcher                    │   │  │
│  │    │    ├─ Load Q&A from DB                          │   │  │
│  │    │    ├─ Train ML Model                            │   │  │
│  │    │    └─ Cache for Performance                     │   │  │
│  │    │                                                  │   │  │
│  │    │ 2. Find Match                                   │   │  │
│  │    │    ├─ Calculate Similarity                      │   │  │
│  │    │    ├─ Apply Threshold (0.85)                    │   │  │
│  │    │    └─ Return Best Match or None                 │   │  │
│  │    │                                                  │   │  │
│  │    │ 3. Return Response                              │   │  │
│  │    │    ├─ Match Found: Return DB Answer            │   │  │
│  │    │    └─ No Match: Return "No Info" Message       │   │  │
│  │    └─────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE TO USER                             │
│                                                                 │
│  ✅ Match Found:                                               │
│     - Response from database                                   │
│     - No LLM generation                                        │
│     - Source: "database_exact_match"                           │
│                                                                 │
│  ❌ No Match Found:                                            │
│     - "Don't have info" message                                │
│     - No LLM generation                                        │
│     - Source: "no_match"                                       │
└─────────────────────────────────────────────────────────────────┘
```

## Comparison: Before vs After

### BEFORE (Old Behavior)

```
User Query
    │
    ▼
Search Documents
    │
    ▼
Found Documents? ─── Yes ──→ Pass to GPT ──→ GPT Generates Answer
    │                                              │
    No                                            │
    │                                             │
    ▼                                             │
Try Database Query ──→ Success? ─── Yes ─────────┤
    │                      │                      │
    No                     No                     │
    │                      │                      │
    ▼                      ▼                      │
Clarifying Question  Empty Result                │
    │                      │                      │
    └──────────────────────┴──────────────────────┘
                           │
                           ▼
                    ⚠️ COULD ADD COMMON KNOWLEDGE
```

### AFTER (New Behavior)

```
User Query (source: "auto")
    │
    ▼
🔒 STRICT MODE: Search Historical Q&A
    │
    ▼
Find Match (≥85% similarity)?
    │
    ├─── Yes ──→ Return Exact Match (Database)
    │                   │
    │                   ▼
    │              ✅ NO LLM USED
    │
    └─── No ───→ Return "No Info" Message
                        │
                        ▼
                   ✅ NO LLM USED
                   ✅ NO GENERATION
                   ✅ NO COMMON KNOWLEDGE
```

## Security & Quality Benefits

```
┌─────────────────────────────────────────────────────────────────┐
│                      STRICT MODE BENEFITS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔒 Security                                                    │
│     ├─ No LLM hallucinations                                   │
│     ├─ No external knowledge injection                         │
│     └─ Complete audit trail                                    │
│                                                                 │
│  ✅ Quality                                                     │
│     ├─ Consistent answers                                      │
│     ├─ Verified information only                               │
│     └─ High similarity threshold (85%)                         │
│                                                                 │
│  ⚡ Performance                                                 │
│     ├─ Faster (no GPT API call)                                │
│     ├─ Cheaper (no LLM costs)                                  │
│     └─ Cacheable results                                       │
│                                                                 │
│  📊 Monitoring                                                  │
│     ├─ Track match rates                                       │
│     ├─ Identify knowledge gaps                                 │
│     └─ Improve over time                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Key Takeaways

1. **Auto Mode = Strict Mode** 🔒
   - Only returns exact matches from database
   - No LLM generation
   - No common knowledge

2. **Other Modes Unchanged** 📄
   - "documents" still uses RAG + LLM
   - "database" still converts to SQL
   - Full functionality preserved

3. **High Quality Bar** 🎯
   - 85% similarity threshold
   - Filters out poor responses
   - Semantic + TF-IDF matching

4. **Clear Responses** 💬
   - Match found: Returns DB answer
   - No match: Clear "don't have info" message
   - Always includes confidence score

---

**Visual Guide Version:** 1.0
**Last Updated:** December 16, 2025

