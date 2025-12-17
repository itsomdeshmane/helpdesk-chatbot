# Database Metadata Learning System

## Overview

This system automatically learns from chat interactions to improve database column and table descriptions, resulting in more accurate SQL query generation.

## 🎯 Key Features

1. **Automatic Learning** - Every database query interaction is recorded and analyzed
2. **Smart Descriptions** - AI-generated semantic descriptions for tables and columns
3. **Continuous Improvement** - System learns from successful queries to suggest better descriptions
4. **User Feedback** - Users can rate queries to improve accuracy
5. **Auto-Apply** - High-confidence improvements are applied automatically
6. **Manual Review** - Low-confidence suggestions require manual approval

## 📋 Database Tables

### 1. `column_metadata`
Stores semantic descriptions for database columns.

```sql
- id
- tenant_id
- database_name
- table_name
- column_name
- description (TEXT) - Human-readable description
- semantic_type (location, financial, temporal, etc.)
- examples (JSON array of sample values)
- is_sensitive (PII flag)
```

### 2. `table_metadata`
Stores descriptions and context for database tables.

```sql
- id
- tenant_id
- database_name
- table_name
- description
- business_purpose
- primary_entity
- common_joins (JSON)
```

### 3. `query_learning_data`
Records every query execution for learning.

```sql
- id
- tenant_id, session_id, user_id
- natural_language_query
- generated_sql
- tables_used, columns_used
- execution_success, execution_time_ms, rows_returned
- user_feedback (positive/negative/neutral)
- user_rating (1-5)
- confidence_score
```

### 4. `metadata_improvement_suggestions`
AI-generated suggestions for improving metadata.

```sql
- id
- tenant_id, database_name, table_name, column_name
- current_description
- suggested_description
- suggestion_reason
- confidence_score
- status (pending/approved/rejected/applied)
```

### 5. `metadata_quality_metrics`
Tracks quality and usage metrics for metadata.

```sql
- tenant_id, database_name, table_name, column_name
- query_success_count, query_failure_count
- positive_feedback_count, negative_feedback_count
- times_used, last_used_at
- quality_score (calculated)
```

## 🚀 Getting Started

### Step 1: Run Migration

```bash
# Run the migration script
mysql -u root -p your_database < backend/migrations/006_create_column_metadata_tables.sql
```

### Step 2: Auto-Discover Metadata

Use the API to automatically discover and populate metadata for your database:

```bash
POST /metadata/metadata/auto-discover
{
  "tenant_id": "your-tenant-id",
  "database_name": "your_database",
  "connection_string": "host=localhost;database=your_database;user=root;password=pass"
}
```

This will:
- Scan all tables and columns
- Generate smart descriptions based on column names and types
- Detect semantic types (location, financial, temporal, etc.)
- Save to the metadata tables

### Step 3: Start Using Smart Chat

Every query through `/chat/smart/query` or `/chat/smart/stream` will:
1. Use enriched metadata in SQL generation prompts
2. Record query execution data
3. Analyze patterns for improvements
4. Suggest better descriptions automatically

## 📝 API Endpoints

### Metadata Management

#### Save Column Metadata
```bash
POST /metadata/metadata/column/save
{
  "tenant_id": "tenant1",
  "database_name": "mydb",
  "table_name": "vendors",
  "column_name": "country",
  "description": "Country where vendor is located (2-letter ISO code)",
  "semantic_type": "location",
  "examples": ["US", "IN", "UK"]
}
```

#### Save Table Metadata
```bash
POST /metadata/metadata/table/save
{
  "tenant_id": "tenant1",
  "database_name": "mydb",
  "table_name": "vendors",
  "description": "Vendor and supplier information",
  "business_purpose": "Track all vendors who supply products",
  "primary_entity": "Vendor"
}
```

#### Get Improvement Suggestions
```bash
GET /metadata/metadata/suggestions
  ?tenant_id=tenant1
  &database_name=mydb
  &status=pending
  &min_confidence=0.70
```

Response:
```json
{
  "success": true,
  "count": 5,
  "suggestions": [
    {
      "id": 123,
      "table_name": "vendors",
      "column_name": "country",
      "current_description": "Country",
      "suggested_description": "Country where vendor is located for geographic analysis",
      "confidence_score": 0.85,
      "based_on_queries_count": 12,
      "status": "pending"
    }
  ]
}
```

#### Approve Suggestion
```bash
POST /metadata/metadata/suggestions/approve
{
  "suggestion_id": 123,
  "apply_immediately": true
}
```

#### Submit User Feedback
```bash
POST /metadata/metadata/feedback
{
  "query_id": 456,
  "feedback": "positive",
  "rating": 5,
  "comment": "Exactly what I needed"
}
```

#### Get Quality Report
```bash
GET /metadata/metadata/quality-report
  ?tenant_id=tenant1
  &database_name=mydb
```

Response:
```json
{
  "success": true,
  "report": {
    "overall": {
      "total_queries": 1234,
      "successful_queries": 1100,
      "positive_feedback": 856,
      "negative_feedback": 45,
      "avg_rating": 4.2
    },
    "top_tables": [
      {
        "table_name": "vendors",
        "quality_score": 92.5,
        "times_used": 450,
        "query_success_count": 425
      }
    ],
    "improvements": {
      "pending_count": 15,
      "avg_confidence": 0.78
    }
  }
}
```

## 🤖 How Auto-Learning Works

### 1. Query Execution Recording
Every database query is recorded with:
- Natural language question
- Generated SQL
- Tables and columns used
- Success/failure status
- Execution time and rows returned

### 2. Pattern Analysis
The system analyzes queries to detect patterns:
- "vendors in India" → learns that "country" is used for location filtering
- "count by city" → learns that "city" is used for grouping
- "total amount" → learns that "amount" is a financial field

### 3. Suggestion Generation
Based on patterns, the system suggests improvements:
- **High confidence (>80%)**: Auto-applied immediately
- **Medium confidence (70-80%)**: Pending manual review
- **Low confidence (<70%)**: Not suggested

### 4. Quality Metrics
Tracks success rate for each table/column:
- Success rate = successful queries / total queries
- Quality score = (successes + positive feedback) / total
- Used to prioritize improvement efforts

## 📊 Semantic Types

The system recognizes these semantic types:

| Type | Description | Examples |
|------|-------------|----------|
| `identifier` | IDs and keys | id, uuid, code |
| `location` | Geographic data | country, city, address |
| `contact` | Contact info | email, phone, website |
| `temporal` | Dates and times | created_at, date, timestamp |
| `financial` | Money and amounts | price, cost, salary |
| `quantity` | Counts and quantities | stock, inventory, count |
| `status` | Status flags | active, enabled, state |
| `personal` | PII data | name, age, ssn |
| `description` | Text descriptions | notes, comment, details |
| `category` | Classifications | type, category, group |

## 🎯 Best Practices

### 1. Initial Setup
- Run auto-discovery immediately after connecting a new database
- Review and refine auto-generated descriptions
- Add business context to table descriptions

### 2. Ongoing Maintenance
- Review pending suggestions weekly
- Approve high-confidence suggestions in batches
- Monitor quality reports to identify problem areas
- Encourage users to provide feedback

### 3. Description Writing
**Good descriptions:**
- ✅ "Country where vendor is located (2-letter ISO code)"
- ✅ "Total order amount in USD before tax"
- ✅ "Customer email address for notifications"

**Bad descriptions:**
- ❌ "Country" (too vague)
- ❌ "Amount" (unclear what kind)
- ❌ "Email" (missing context)

### 4. Leveraging Learning
- Let the system run for 1-2 weeks to collect data
- Review suggestions that have high query counts
- Apply improvements in batches during off-hours
- Monitor quality score improvements

## 🔄 Integration with Smart Chat

The metadata system is automatically integrated with Smart Chat:

```python
# In smart_chat.py, the system:
# 1. Enriches schema with metadata descriptions
schema_context = schema_service.get_schema_context(
    schema, 
    tenant_id=tenant_id, 
    database_name=db_name,
    include_descriptions=True  # ← Includes metadata descriptions
)

# 2. Passes enriched schema to SQL generator
sql_query = await db_service.convert_to_sql(
    query, 
    schema_context,  # ← Contains column descriptions
    conversation_history
)

# 3. Records execution for learning
learning_service.record_query_execution(
    tenant_id=tenant_id,
    natural_query=query,
    sql_query=sql_query,
    success=result["success"],
    rows_returned=len(rows)
)
```

## 📈 Monitoring and Metrics

### Dashboard Metrics
Track these key metrics:
- **Query Success Rate**: % of queries that execute successfully
- **User Satisfaction**: Average rating from user feedback
- **Metadata Coverage**: % of columns with custom descriptions
- **Quality Score**: Aggregated quality score across all tables
- **Learning Velocity**: Rate of new suggestions generated

### Query Patterns
Monitor common patterns:
- Most queried tables
- Frequently used columns
- Common JOIN patterns
- Failed query types

## 🔒 Security Considerations

1. **PII Flagging**: Mark sensitive columns with `is_sensitive = TRUE`
2. **Access Control**: Metadata API endpoints should require authentication
3. **Audit Trail**: All changes are tracked with `created_by` and `updated_by`
4. **Tenant Isolation**: All queries are scoped to tenant_id

## 🚨 Troubleshooting

### Problem: Low Quality Scores
**Solution**: 
- Check if descriptions are too generic
- Review failed queries for patterns
- Add more specific semantic types

### Problem: No Suggestions Generated
**Solution**:
- Ensure queries are being recorded (check `query_learning_data` table)
- Lower the `min_queries_for_suggestion` threshold
- Verify database name is correctly extracted

### Problem: Auto-Apply Not Working
**Solution**:
- Check `auto_improve_threshold` setting (default 0.80)
- Verify suggestions have high confidence scores
- Check application logs for errors

## 📚 Further Reading

- [SQL Generation Architecture](./SQL_GENERATION.md)
- [Smart Chat Documentation](./SMART_CHAT.md)
- [Database Schema Guide](./DATABASE_SCHEMA.md)

## 🤝 Contributing

To improve the learning system:
1. Enhance pattern detection in `_extract_query_insights()`
2. Add new semantic types to `semantic_types` table
3. Improve confidence scoring algorithms
4. Add more intelligent description templates

