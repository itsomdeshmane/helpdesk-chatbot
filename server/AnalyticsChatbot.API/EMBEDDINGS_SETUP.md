# Vector Embeddings & AI-Powered SQL Generation - Setup Guide

## Overview

This analytics chatbot now includes an advanced AI-powered SQL generation system that uses:
- **Vector embeddings** for intelligent schema context selection
- **OpenAI GPT-4** for natural language to SQL conversion
- **Prompt optimization** to reduce token usage and costs
- **Training data logging** for future model fine-tuning

## Architecture

### Components

1. **SchemaExtractor** (`Utils/SchemaExtractor.cs`)
   - Extracts table/column metadata from MySQL database
   - Reads column descriptions from INFORMATION_SCHEMA

2. **SchemaEmbedder** (`Embeddings/SchemaEmbedder.cs`)
   - Generates OpenAI embeddings for each schema element
   - Stores embeddings in `schema_embeddings.json`

3. **QueryEmbedder** (`Embeddings/QueryEmbedder.cs`)
   - Generates embeddings for user queries

4. **VectorSearch** (`Embeddings/VectorSearch.cs`)
   - Performs cosine similarity search
   - Returns top-N most relevant schema elements

5. **LlmPromptBuilder** (`Services/LlmPromptBuilder.cs`)
   - Builds optimized prompts with pruned context
   - Formats schema for GPT-4 consumption

6. **LlmService** (`Services/LlmService.cs`)
   - Orchestrates the entire pipeline
   - Calls OpenAI API with optimized prompts
   - Logs interactions for training dataset

## Setup Instructions

### 1. Configure OpenAI API Key

Already configured in `appsettings.json`:

```json
{
  "OpenAI": {
    "ApiKey": "your-api-key-here",
    "Model": "gpt-4"
  }
}
```

### 2. Configure Database Connection

Update `ConnectionStrings:DefaultConnection` in `appsettings.json`:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "server=localhost;database=yourdb;user=root;password=yourpassword;"
  }
}
```

### 3. Generate Schema Embeddings

**Option A: Using API Endpoint**

```bash
curl -X POST "http://localhost:5000/api/schema/generate-embeddings"
```

**Option B: Using Swagger**

1. Run the application
2. Navigate to `/swagger`
3. Find `POST /api/schema/generate-embeddings`
4. Execute the endpoint

This will:
- Extract all tables and columns from your database
- Generate embeddings for each schema element
- Save to `schema_embeddings.json`

### 4. Verify Schema Information

```bash
curl -X GET "http://localhost:5000/api/schema/info"
```

This returns details about your database schema.

## How It Works

### Request Flow

```
User Query
    ↓
1. Generate query embedding (OpenAI)
    ↓
2. Vector similarity search
    ↓
3. Select top-N relevant schema elements
    ↓
4. Build optimized prompt (small context)
    ↓
5. Call GPT-4 with pruned prompt
    ↓
6. Generate SQL query
    ↓
7. Log interaction for training
    ↓
Response to user
```

### Benefits

1. **Reduced Token Usage**
   - Only relevant schema elements included in prompts
   - Typical prompt size: 500-1000 tokens vs 5000+ tokens with full schema

2. **Better Accuracy**
   - LLM focuses on relevant tables/columns
   - Less noise and confusion

3. **Training Data Collection**
   - Every interaction logged to `training_logs.jsonl`
   - Ready for fine-tuning or custom model training

4. **Scalability**
   - Works with databases of any size
   - Constant prompt size regardless of schema complexity

## Usage Examples

### Example 1: Simple Query

**User Input:**
```
Show me all orders from last month
```

**System:**
1. Embeds query
2. Finds relevant schema: `Orders.OrderId, Orders.OrderDate, Orders.CustomerId`
3. Builds prompt with only Orders table
4. Generates: `SELECT * FROM Orders WHERE OrderDate >= DATE_SUB(NOW(), INTERVAL 1 MONTH)`

### Example 2: Complex Query

**User Input:**
```
What's the total revenue by product category?
```

**System:**
1. Embeds query
2. Finds: `Products.CategoryId, Sales.Amount, Categories.Name`
3. Builds prompt with Products, Sales, Categories
4. Generates proper JOIN query

## Training Data

All interactions are logged to `training_logs.jsonl` with format:

```json
{
  "Timestamp": "2024-11-14T10:30:00Z",
  "UserQuery": "show all users",
  "RelevantSchema": [
    {
      "TableName": "Users",
      "ColumnName": "UserId",
      "Similarity": 0.85
    }
  ],
  "GeneratedSql": "SELECT * FROM Users"
}
```

### Future Fine-Tuning

Use this data to:
1. Fine-tune OpenAI models
2. Train custom models (Llama, Mistral, etc.)
3. Improve prompt engineering

## API Endpoints

### Schema Management

- `POST /api/schema/generate-embeddings` - Generate/refresh embeddings
- `GET /api/schema/info` - View current schema

### Chat/Query

- `POST /api/chat/query` - Send natural language queries (existing endpoint)

## Performance Tuning

### Adjust Top-N Results

In `LlmService.cs`, modify:

```csharp
var topMatches = _vectorSearch.FindTopMatches(queryEmbedding, topN: 10);
```

- **Lower N (5-7)**: Faster, cheaper, less context
- **Higher N (15-20)**: More context, better for complex queries

### Change OpenAI Model

In `LlmService.cs`:

```csharp
model = "gpt-3.5-turbo"  // Faster, cheaper
model = "gpt-4"           // Better accuracy
model = "gpt-4-turbo"     // Balanced
```

## Troubleshooting

### Embeddings File Not Found

Run: `POST /api/schema/generate-embeddings`

### OpenAI API Errors

- Check API key in `appsettings.json`
- Verify API quota/limits
- Check network connectivity

### Poor SQL Quality

- Increase `topN` parameter
- Add column descriptions in your database schema
- Review and fine-tune prompts in `LlmPromptBuilder.cs`

## Next Steps

1. ✅ Schema extraction
2. ✅ Vector embeddings
3. ✅ Optimized prompts
4. ✅ Training data logging
5. 🔜 Fine-tune custom model
6. 🔜 Add caching layer (Redis)
7. 🔜 Implement feedback loop
8. 🔜 A/B testing different models

## Cost Estimation

With optimized prompts:
- Query embedding: ~$0.0001 per query
- GPT-4 inference: ~$0.01-0.03 per query
- Typical cost: **~$0.03 per user query**

vs. Without optimization:
- GPT-4 with full schema: ~$0.10-0.15 per query

**Savings: 70-80%**

## Support

For issues or questions, check:
- Application logs
- `training_logs.jsonl` for debugging
- OpenAI API status page

