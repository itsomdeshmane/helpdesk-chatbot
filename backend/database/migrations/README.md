# Database Migrations

Complete database schema and migration scripts for the Helpdesk Chatbot system.

## 📁 Structure

```
migrations/
├── 00_complete_schema.sql         # Complete schema (all tables)
├── 01_users_authentication.sql    # Users & auth tables
├── 02_conversations_sessions.sql  # Conversation management
├── 03_context_tracking.sql        # AI context tracking
├── 04_question_generation.sql     # Question generation tables
├── run_migrations.py              # Master migration runner
└── README.md                      # This file
```

## 🚀 Quick Start

### Option 1: Run All Migrations (Recommended)

```bash
cd backend/database/migrations
python run_migrations.py
```

This will:
- ✅ Create database if needed
- ✅ Run migrations in order
- ✅ Track applied migrations
- ✅ Skip already applied migrations
- ✅ Safe to run multiple times

### Option 2: Run Complete Schema (Fresh Install)

```bash
mysql -u root -p < 00_complete_schema.sql
```

Use this for a fresh installation with all tables at once.

## 📊 Check Migration Status

```bash
python run_migrations.py --status
```

Shows which migrations have been applied and when.

## 🔄 Force Re-run All Migrations

```bash
python run_migrations.py --force
```

Re-runs all migrations even if already applied. Use with caution!

## 📋 Migration Details

### 00_complete_schema.sql
**Complete database schema with all tables**

Contains:
- All tables in a single file
- Default data (ERP entities)
- Full indexes and foreign keys
- Safe to run multiple times (uses IF NOT EXISTS)

Tables created:
- users (authentication)
- conversations (session management)
- chat_interactions (chat history)
- conversation_context (AI context tracking)
- context_resolution_cache (pronoun resolution)
- faq_questions (knowledge base)
- response_patterns (response templates)
- query_type_patterns (query classification)
- erp_modules (module detection)
- erp_entities (entity recognition)
- generated_questions (AI-generated questions)
- query_clarifications (clarity tracking)

### 01_users_authentication.sql
**Users & Authentication**

Creates:
- `users` table with role-based access control
- Roles: admin, user, viewer
- Password hashing support
- Multi-tenant support

### 02_conversations_sessions.sql
**Conversation Session Management**

Creates:
- `conversations` table for session tracking
- Updates `chat_interactions` with conversation links
- Enables multi-turn conversations
- Session expiry support

### 03_context_tracking.sql
**AI-Powered Context Tracking**

Creates:
- `conversation_context` table (AI-extracted topics)
- `context_resolution_cache` table (pronoun resolution)
- JSON storage for entities and keywords
- Confidence scoring

### 04_question_generation.sql
**Question Generation & Clarity**

Creates:
- `generated_questions` table (AI-generated questions)
- `query_clarifications` table (clarity tracking)
- Difficulty level support (beginner, intermediate, advanced)
- Usage tracking

## 🛠️ Manual Migration

If you prefer to run migrations individually:

```bash
# Run specific migration
mysql -u root -p helpdesk_db < 01_users_authentication.sql

# Run in order
mysql -u root -p helpdesk_db < 01_users_authentication.sql
mysql -u root -p helpdesk_db < 02_conversations_sessions.sql
mysql -u root -p helpdesk_db < 03_context_tracking.sql
mysql -u root -p helpdesk_db < 04_question_generation.sql
```

## 📚 Related Scripts

### Python Migration Scripts (../scripts/)

These Python scripts provide additional functionality:

- `create_users_table.py` - Create users + default admin
- `migrate_add_conversations.py` - Add conversation support
- `migrate_add_context_tracking.py` - Add context tracking
- `init_question_tables.py` - Initialize question tables
- `migrate_all_conversation_features.py` - Run all conversation migrations

### Legacy Scripts

These are superseded by the migration runner:

```bash
# Old way (still works)
cd backend/scripts
python migrate_all_conversation_features.py

# New way (recommended)
cd backend/database/migrations
python run_migrations.py
```

## 🔍 Verify Database

After running migrations:

```bash
cd backend/scripts
python test_mysql_connection.py
```

This will show all tables and row counts.

## 📝 Adding New Migrations

To add a new migration:

1. Create a new SQL file: `05_your_feature.sql`
2. Add header with description and version
3. Use `CREATE TABLE IF NOT EXISTS` for safety
4. Add verification queries at the end
5. Update `run_migrations.py` migrations list
6. Test with `--force` flag first

Example template:

```sql
-- ============================================================================
-- MIGRATION: Your Feature Name
-- ============================================================================
-- Description of what this migration does
-- Version: 5.0
-- Date: 2025-12-03
-- ============================================================================

USE helpdesk_db;

CREATE TABLE IF NOT EXISTS your_new_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    -- your columns here
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Verification
SELECT 'Your feature created successfully' AS status;
```

## 🔐 Environment Variables

Ensure your `.env` file has:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=helpdesk_db
```

## ⚠️ Important Notes

1. **Idempotent**: All migrations are safe to run multiple times
2. **Order Matters**: Migrations have dependencies, run in order
3. **Backup First**: Always backup before running migrations in production
4. **Test Locally**: Test migrations on local/dev environment first
5. **Foreign Keys**: Some tables have foreign key constraints

## 🐛 Troubleshooting

### Migration fails with "table already exists"

This is normal and expected. The migration script handles this gracefully.

### Foreign key constraint error

Make sure migrations are run in order. Migration 03 depends on 02, etc.

### Connection refused

Check:
1. MySQL is running
2. Credentials in `.env` are correct
3. Database user has CREATE/ALTER permissions

### Permission denied

Your MySQL user needs these privileges:

```sql
GRANT ALL PRIVILEGES ON helpdesk_db.* TO 'your_user'@'localhost';
FLUSH PRIVILEGES;
```

## 📞 Support

For issues:
1. Check migration status: `python run_migrations.py --status`
2. Review error messages carefully
3. Check MySQL error log
4. Verify database permissions

---

**Last Updated**: December 3, 2025
**Version**: 1.0


