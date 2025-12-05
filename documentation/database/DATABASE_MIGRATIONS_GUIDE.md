# Database Migrations - Complete Guide

## 📍 Overview

All database schema and migration scripts have been centralized in:

```
backend/database/migrations/
```

This folder contains:
- ✅ Complete schema (all tables in one file)
- ✅ Individual migration scripts
- ✅ Master migration runner
- ✅ Migration tracking system

## 🚀 Quick Start

### For New Installations

```bash
cd backend/database/migrations
python run_migrations.py
```

This single command will:
1. Create the database
2. Create all tables
3. Insert default data
4. Track applied migrations
5. Skip already applied migrations

### Check What's Been Applied

```bash
cd backend/database/migrations
python run_migrations.py --status
```

## 📂 File Structure

### SQL Migration Files

| File | Purpose | Tables Created |
|------|---------|----------------|
| `00_complete_schema.sql` | Complete schema | All 12 tables |
| `01_users_authentication.sql` | User auth | users |
| `02_conversations_sessions.sql` | Chat sessions | conversations, updates chat_interactions |
| `03_context_tracking.sql` | AI context | conversation_context, context_resolution_cache |
| `04_question_generation.sql` | Questions | generated_questions, query_clarifications |

### Python Scripts

| File | Purpose |
|------|---------|
| `run_migrations.py` | Master runner - runs all migrations |

## 📊 Complete Table List

After running migrations, you'll have these 12 tables:

### 1. Authentication & Users
- **users** - User accounts with roles (admin/user/viewer)

### 2. Conversations
- **conversations** - Session management
- **chat_interactions** - Chat history with conversation links

### 3. AI Context Tracking
- **conversation_context** - AI-extracted topics and entities
- **context_resolution_cache** - Pronoun resolution cache

### 4. Knowledge Base
- **faq_questions** - FAQ storage
- **response_patterns** - Response templates

### 5. Module & Entity Management
- **query_type_patterns** - Query classification keywords
- **erp_modules** - ERP module definitions
- **erp_entities** - Entity recognition (items, customers, etc.)

### 6. Question Generation
- **generated_questions** - AI-generated module questions
- **query_clarifications** - Clarity tracking

## 🔄 Migration Tracking

The system automatically tracks applied migrations in:
- **schema_migrations** table

This ensures:
- ✅ Migrations run only once
- ✅ Safe to re-run migration script
- ✅ Clear audit trail

## 📋 Common Tasks

### Task 1: Fresh Database Setup

```bash
# Option A: Use migration runner (recommended)
cd backend/database/migrations
python run_migrations.py

# Option B: Run complete schema directly
mysql -u root -p < backend/database/migrations/00_complete_schema.sql
```

### Task 2: Add New Feature Tables

1. Create new SQL file: `05_your_feature.sql`
2. Add to migrations list in `run_migrations.py`
3. Run: `python run_migrations.py`

### Task 3: Reset Specific Table

```bash
mysql -u root -p helpdesk_db
DROP TABLE table_name;
exit

cd backend/database/migrations
python run_migrations.py --force
```

### Task 4: Verify All Tables Exist

```bash
cd backend/scripts
python test_mysql_connection.py
```

### Task 5: Create Default Admin User

```bash
cd backend/scripts
python create_users_table.py
```

Creates:
- Username: `admin`
- Password: `admin123`
- Email: `admin@example.com`

## 🔗 Integration with Existing Scripts

### Legacy Migration Scripts

The following scripts in `backend/scripts/` are now supplemented by the centralized migrations:

| Old Script | New Equivalent | Notes |
|------------|----------------|-------|
| `create_mysql_database.py` | `run_migrations.py` | Use new one |
| `migrate_add_conversations.py` | `02_conversations_sessions.sql` | Both work |
| `migrate_add_context_tracking.py` | `03_context_tracking.sql` | Both work |
| `init_question_tables.py` | `04_question_generation.sql` | Both work |
| `migrate_all_conversation_features.py` | `run_migrations.py` | Use new one |

### Recommended Approach

**For new setups:**
```bash
cd backend/database/migrations
python run_migrations.py
```

**For existing deployments:**
```bash
# Continue using your existing scripts
cd backend/scripts
python migrate_all_conversation_features.py
```

Both approaches work and are safe!

## 🔍 Differences: Old vs New

### Old Approach (Scattered)

```
backend/
  ├── database/
  │   ├── mysql_schema.sql
  │   └── conversation_context_schema.sql
  └── scripts/
      ├── create_mysql_database.py
      ├── create_users_table.py
      ├── migrate_add_conversations.py
      ├── migrate_add_context_tracking.py
      ├── init_question_tables.py
      └── migrate_all_conversation_features.py
```

### New Approach (Centralized)

```
backend/
  └── database/
      └── migrations/
          ├── 00_complete_schema.sql       ← All tables
          ├── 01_users_authentication.sql
          ├── 02_conversations_sessions.sql
          ├── 03_context_tracking.sql
          ├── 04_question_generation.sql
          ├── run_migrations.py            ← One runner
          └── README.md
```

**Benefits:**
- ✅ Single location for all schemas
- ✅ Clear migration order
- ✅ Automatic tracking
- ✅ Better documentation
- ✅ Easier to maintain

## 📖 Schema Documentation

### Table Relationships

```
users (authentication)
  └─ (no direct links, uses tenant_id)

conversations (sessions)
  ├─ chat_interactions (messages in conversation)
  ├─ conversation_context (AI-extracted context)
  └─ context_resolution_cache (pronoun resolution)

erp_entities (entity definitions)
  └─ (used for entity recognition)

erp_modules (module definitions)
  └─ (used for module classification)

generated_questions (AI questions)
  └─ (linked by module_name)

query_clarifications (clarity tracking)
  └─ (independent tracking)

faq_questions (knowledge base)
  └─ (independent)

response_patterns (templates)
  └─ (independent)

query_type_patterns (classification)
  └─ (independent)
```

### Key Features

1. **Multi-tenancy**: Most tables have `tenant_id` for data isolation
2. **Soft Deletes**: Use `is_active` flags instead of deleting
3. **Timestamps**: All tables track `created_at` and `updated_at`
4. **Indexes**: Optimized for common queries
5. **Foreign Keys**: Maintain referential integrity with cascading deletes
6. **JSON Columns**: Store flexible data (entities, keywords, issues)

## 🐛 Troubleshooting

### "Table already exists" error

**This is normal!** All migrations use `CREATE TABLE IF NOT EXISTS` to be idempotent.

### Foreign key constraint error

Ensure migrations run in order:
1. 00 or 01 first (creates base tables)
2. 02 (adds conversations)
3. 03 (adds context tracking - depends on conversations)
4. 04 (adds questions)

### Permission issues

Your MySQL user needs:
```sql
GRANT ALL PRIVILEGES ON helpdesk_db.* TO 'your_user'@'localhost';
FLUSH PRIVILEGES;
```

### Connection refused

Check `.env` file:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=helpdesk_db
```

## 🔐 Security Notes

1. **Change default passwords** in production!
2. **Backup** before running migrations in production
3. **Test** on dev/staging first
4. **Review** migration SQL before running
5. **Monitor** database size and performance

## 📞 Support & Maintenance

### Check Database Status

```bash
# Tables and row counts
cd backend/scripts
python test_mysql_connection.py

# Migration status
cd backend/database/migrations
python run_migrations.py --status
```

### Clear Database

```bash
# Clear all data (keeps structure)
cd backend/scripts
python clear_database.py --clear --yes

# Drop and recreate
python clear_database.py --drop --yes
```

### Backup Database

```bash
# Backup schema and data
mysqldump -u root -p helpdesk_db > backup_$(date +%Y%m%d).sql

# Restore
mysql -u root -p helpdesk_db < backup_20251203.sql
```

## 🎯 Best Practices

1. **Always backup** before migrations in production
2. **Test locally** first
3. **Run during low traffic** periods
4. **Monitor** for errors during migration
5. **Verify** tables after migration
6. **Document** any custom changes
7. **Version control** all schema changes

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-03 | Initial centralized migrations |
| - | - | Consolidated all scattered SQL files |
| - | - | Created migration tracking system |
| - | - | Added complete schema file |
| - | - | Created master migration runner |

---

**Location**: `backend/database/migrations/`
**Documentation**: `backend/database/migrations/README.md`
**Last Updated**: December 3, 2025

