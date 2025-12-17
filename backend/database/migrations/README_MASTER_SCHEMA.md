# Master Database Schema

## Overview

`MASTER_SCHEMA.sql` is a **single comprehensive migration script** that contains **all database tables** required for the Helpdesk Chatbot system.

## ✨ What's Included

This master schema includes everything from all previous migrations:

### 📁 10 Major Sections

1. **Authentication & User Management**
   - `users` - User accounts and authentication
   - `user_database_connections` - Encrypted database credentials

2. **Conversation & Session Management**
   - `conversations` - Chat sessions tracking
   - `chat_interactions` - Individual messages

3. **AI Context Tracking & Resolution**
   - `conversation_context` - AI-extracted entities and topics
   - `context_resolution_cache` - Pronoun and reference resolution

4. **Knowledge Base & FAQ**
   - `faq_questions` - Frequently asked questions
   - `response_patterns` - Response formatting patterns
   - `query_type_patterns` - Dynamic keyword detection

5. **ERP Modules & Entities**
   - `erp_modules` - ERP module definitions
   - `erp_entities` - Entity recognition for queries

6. **Question Generation & Clarification**
   - `generated_questions` - AI-generated module questions
   - `query_clarifications` - Unclear query tracking

7. **Feedback & Quality Metrics**
   - `feedback` - User feedback on responses
   - `feedback_daily_stats` - Aggregated statistics
   - `quality_metrics` - Answer quality tracking
   - `cache_metrics` - Cache performance monitoring

8. **Metadata Learning System** 🤖 (NEW!)
   - `column_metadata` - Semantic column descriptions
   - `table_metadata` - Table descriptions
   - `relationship_metadata` - Database relationships
   - `query_patterns` - Common query examples
   - `semantic_types` - Reference data
   - `query_learning_data` - Query execution logs
   - `metadata_quality_metrics` - Quality tracking
   - `metadata_improvement_suggestions` - AI suggestions

9. **Default Data & Seed Values**
   - Semantic types (10 types)
   - ERP entities (18 entities)
   - Default feedback types

10. **Verification & Summary**
    - Displays success message
    - Shows all created tables

## 📊 Database Structure

```
helpdesk_db (Database)
├── Authentication (2 tables)
├── Conversations (2 tables)
├── Context Tracking (2 tables)
├── Knowledge Base (3 tables)
├── ERP System (2 tables)
├── Question Generation (2 tables)
├── Feedback System (4 tables)
└── Metadata Learning (8 tables) 🆕
    └── 25 TOTAL TABLES
```

## 🚀 How to Use

### Option 1: Fresh Installation

```bash
# Run the master schema (creates everything)
mysql -u root -p < backend/migrations/MASTER_SCHEMA.sql

# Or with specific database
mysql -u root -p your_database < backend/migrations/MASTER_SCHEMA.sql
```

### Option 2: Existing Database

The script is **idempotent** - safe to run multiple times!

```bash
# It will skip existing tables and only create missing ones
mysql -u root -p helpdesk_db < backend/migrations/MASTER_SCHEMA.sql
```

### Option 3: Using MySQL Workbench

1. Open MySQL Workbench
2. Connect to your database server
3. File → Open SQL Script
4. Select `MASTER_SCHEMA.sql`
5. Click Execute (⚡ icon)

## ✅ Verification

After running the script, you should see:

```
✅ HELPDESK CHATBOT SCHEMA CREATED SUCCESSFULLY
Total tables: 25

ℹ️  TABLES CREATED:
cache_metrics, chat_interactions, column_metadata, 
context_resolution_cache, conversation_context, conversations,
erp_entities, erp_modules, faq_questions, feedback,
feedback_daily_stats, generated_questions, metadata_improvement_suggestions,
metadata_quality_metrics, quality_metrics, query_clarifications,
query_learning_data, query_patterns, query_type_patterns,
relationship_metadata, response_patterns, semantic_types,
table_metadata, user_database_connections, users
```

### Manual Verification

```sql
-- Check all tables
SELECT COUNT(*) as total_tables 
FROM information_schema.tables 
WHERE table_schema = 'helpdesk_db';
-- Should return: 25

-- List all tables
SHOW TABLES;

-- Check specific table structure
DESCRIBE column_metadata;
DESCRIBE users;
```

## 📝 What This Replaces

This single file replaces **all** of these individual migration files:

```
✅ Replaced:
   - 00_complete_schema.sql
   - 01_users_authentication.sql
   - 02_conversations_sessions.sql
   - 03_context_tracking.sql
   - 04_question_generation.sql
   - 05_feedback_system.sql
   - 05_user_database_connections.sql
   - 06_create_column_metadata_tables.sql
   - add_db_type_column.sql
   - add_db_type_simple.sql
   
❌ You no longer need to run these individually!
```

## 🔄 Migration Strategy

### For New Projects
```bash
# Just run the master schema
mysql -u root -p < backend/migrations/MASTER_SCHEMA.sql
```

### For Existing Projects
```bash
# The script is safe - it won't drop or modify existing tables
mysql -u root -p helpdesk_db < backend/migrations/MASTER_SCHEMA.sql

# It will:
# ✅ Skip tables that already exist
# ✅ Add missing tables
# ✅ Insert default data (using INSERT IGNORE or ON DUPLICATE KEY)
```

## 🎯 Next Steps After Installation

1. **Verify Installation**
   ```sql
   USE helpdesk_db;
   SHOW TABLES;
   ```

2. **Create First Admin User**
   ```sql
   INSERT INTO users (username, email, password_hash, role, tenant_id)
   VALUES ('admin', 'admin@example.com', 'hashed_password_here', 'admin', 'default');
   ```

3. **Auto-Discover Metadata** (for database connections)
   ```bash
   curl -X POST http://localhost:8000/metadata/metadata/auto-discover \
     -H "Content-Type: application/json" \
     -d '{
       "tenant_id": "default",
       "database_name": "your_database",
       "connection_string": "host=localhost;database=your_database;user=root;password=pass"
     }'
   ```

4. **Start the Application**
   ```bash
   cd backend
   uvicorn app:app --reload
   ```

## 🔒 Security Notes

- The `user_database_connections` table stores **encrypted** passwords
- Default user passwords should be changed immediately
- Use environment variables for database credentials
- Review and configure tenant isolation

## 📊 Key Features

### 🤖 AI-Powered Features
- **Context Tracking**: Remembers conversation context
- **Entity Recognition**: Understands ERP entities
- **Smart Clarification**: Asks relevant questions
- **Metadata Learning**: Learns from every query
- **Auto-Improvement**: Suggests better descriptions

### 📈 Analytics & Monitoring
- User feedback tracking
- Quality metrics per query
- Cache performance monitoring
- Daily aggregated statistics
- Query success rates

### 🎯 Smart SQL Generation
- Column semantic descriptions
- Table relationship tracking
- Common query patterns
- Auto-learning from usage
- Quality-based improvements

## 🐛 Troubleshooting

### Error: "Database already exists"
✅ **This is fine!** The script uses `CREATE DATABASE IF NOT EXISTS`

### Error: "Table already exists"
✅ **This is fine!** The script uses `CREATE TABLE IF NOT EXISTS`

### Error: "Duplicate entry for key"
✅ **This is fine!** Default data uses `INSERT IGNORE` or `ON DUPLICATE KEY UPDATE`

### Want to Start Fresh?
```sql
-- ⚠️  WARNING: This will delete ALL data!
DROP DATABASE IF EXISTS helpdesk_db;

-- Then run the master schema
SOURCE backend/migrations/MASTER_SCHEMA.sql;
```

## 📚 Documentation

For more details on specific components:

- **Metadata System**: See `backend/docs/METADATA_SYSTEM.md`
- **Quick Start**: See `backend/docs/METADATA_QUICKSTART.md`
- **API Documentation**: http://localhost:8000/docs

## 🎉 Success Indicators

After successful installation, you should be able to:

✅ Create user accounts  
✅ Start chat sessions  
✅ Store conversations  
✅ Track feedback  
✅ Connect to user databases  
✅ Auto-discover metadata  
✅ Generate SQL from natural language  
✅ Learn from query patterns  
✅ Improve over time automatically  

## 💡 Pro Tips

1. **Backup Before Running**: Always backup existing data first
2. **Test in Development**: Test the schema in a dev environment first
3. **Monitor Logs**: Check application logs after migration
4. **Verify Data**: Check that default data was inserted
5. **Index Performance**: Monitor query performance and add indexes if needed

## 🔄 Version History

- **v3.0.0** (Jan 17, 2025) - Added Metadata Learning System (8 new tables)
- **v2.0.0** (Dec 3, 2024) - Added Feedback & Quality Metrics (4 tables)
- **v1.0.0** (Dec 1, 2024) - Initial comprehensive schema (17 tables)

## 📞 Support

If you encounter issues:
1. Check the logs: `tail -f backend/logs/app.log`
2. Verify tables: `SHOW TABLES;`
3. Check indexes: `SHOW INDEX FROM table_name;`
4. Review foreign keys: `SHOW CREATE TABLE table_name;`

---

**Remember**: This is the **only migration file you need to run** for a complete installation! 🎯

