# Complete Scripts Reference Guide

This guide provides comprehensive documentation for all utility scripts in the helpdesk-chatbot system.

---

## Table of Contents

1. [Database Management Scripts](#database-management-scripts)
2. [Migration Scripts](#migration-scripts)
3. [Data Loading & Seeding Scripts](#data-loading--seeding-scripts)
4. [Configuration & Setup Scripts](#configuration--setup-scripts)
5. [Monitoring & Analysis Scripts](#monitoring--analysis-scripts)
6. [Testing Scripts](#testing-scripts)

---

## Database Management Scripts

### 1. `clear_database.py` - Full Database Management

Comprehensive script with multiple options for clearing/resetting the database.

**Location:** `backend/scripts/clear_database.py`

#### Usage

```bash
# Show database status
python backend/scripts/clear_database.py --status

# Clear all data (with confirmation)
python backend/scripts/clear_database.py --clear

# Clear all data (no confirmation)
python backend/scripts/clear_database.py --clear --yes

# Clear with TRUNCATE (faster)
python backend/scripts/clear_database.py --clear --truncate

# Drop and recreate all tables
python backend/scripts/clear_database.py --drop

# Clear but keep entities
python backend/scripts/clear_database.py --clear --keep-entities
```

#### Options

- `--status` - Show current database status
- `--clear` - Clear all data from tables
- `--truncate` - Use TRUNCATE instead of DELETE (faster)
- `--drop` - Drop all tables and recreate fresh
- `--keep-entities` - Preserve erp_entities table
- `--yes, -y` - Skip confirmation prompt

---

### 2. `quick_clear_db.py` - Quick Chat History Clear

Simple script to clear only chat history, preserving entities and structure.

**Location:** `backend/scripts/quick_clear_db.py`

#### Usage

```bash
# Clear chat history (with confirmation)
python backend/scripts/quick_clear_db.py

# Clear without confirmation
python backend/scripts/quick_clear_db.py --yes
```

#### What it clears:
- ✅ `chat_interactions` - All chat history
- ✅ `query_clarifications` - Clarification records
- ✅ `generated_questions` - Generated questions

#### What it preserves:
- ✅ `erp_entities` - Entity definitions
- ✅ `erp_modules` - Module configurations
- ✅ Database structure and schema

---

### 3. `create_mysql_database.py` - MySQL Database Creator

Creates the MySQL database if it doesn't exist.

**Location:** `backend/scripts/create_mysql_database.py`

#### Usage

```bash
python backend/scripts/create_mysql_database.py
```

**Purpose:** 
- Creates the MySQL database specified in your `.env` file
- Sets up proper character encoding (utf8mb4)
- Grants necessary permissions

---

### 4. `update_database_schema.py` - Schema Update Tool

Updates the database schema with new columns or modifications.

**Location:** `backend/scripts/update_database_schema.py`

#### Usage

```bash
python backend/scripts/update_database_schema.py
```

**Purpose:** 
- Adds new columns to existing tables
- Updates table structures
- Safe to run multiple times (checks before modifying)

---

## Migration Scripts

### 🚀 **IMPORTANT: Run These First!**

### 1. `migrate_all_conversation_features.py` - Complete Conversation Setup

**Location:** `backend/scripts/migrate_all_conversation_features.py`

**RUN THIS FIRST** before using the chatbot!

#### Usage

```bash
python backend/scripts/migrate_all_conversation_features.py
```

**What it does:**
- ✅ Creates session management tables
- ✅ Enables AI-powered context tracking
- ✅ Adds intelligent pronoun resolution
- ✅ Enables multi-turn conversations with memory
- ✅ Safe to run multiple times (idempotent)

---

### 2. `migrate_add_conversations.py` - Add Conversation Tables

**Location:** `backend/scripts/migrate_add_conversations.py`

Adds conversation and session tracking tables.

#### Usage

```bash
python backend/scripts/migrate_add_conversations.py
```

**Creates:**
- `conversations` table
- `conversation_sessions` table
- Session tracking columns

---

### 3. `migrate_add_context_tracking.py` - Add Context Tracking

**Location:** `backend/scripts/migrate_add_context_tracking.py`

Adds context tracking capabilities to conversations.

#### Usage

```bash
python backend/scripts/migrate_add_context_tracking.py
```

**Adds:**
- Context tracking fields
- Entity reference tracking
- Conversation continuity features

---

### 4. `run_soft_delete_migration.py` - Enable Soft Deletes

**Location:** `backend/scripts/run_soft_delete_migration.py`

Adds soft delete functionality to prevent data loss.

#### Usage

```bash
python backend/scripts/run_soft_delete_migration.py
```

**What it does:**
- Adds `deleted_at` columns
- Enables data recovery
- Preserves audit trail

---

### 5. `migrate_sqlite_to_mysql.py` - SQLite to MySQL Migration

**Location:** `backend/scripts/migrate_sqlite_to_mysql.py`

Migrates data from SQLite to MySQL database.

#### Usage

```bash
python backend/scripts/migrate_sqlite_to_mysql.py
```

**Purpose:**
- Migrates existing SQLite data to MySQL
- Preserves all relationships
- Validates data integrity

---

## Data Loading & Seeding Scripts

### 1. `reload_verax_docs.py` - Reload Verax Documentation

**Location:** `backend/scripts/reload_verax_docs.py`

Reloads Verax workflow documentation into the system.

#### Usage

```bash
python backend/scripts/reload_verax_docs.py
```

**Purpose:**
- Processes DOCX files from `docs/` folder
- Extracts text and metadata
- Loads into vector database (Pinecone)
- Updates document embeddings

---

### 2. `reload_docs_to_pinecone.py` - General Document Reloader

**Location:** `backend/scripts/reload_docs_to_pinecone.py`

Reloads all documents into Pinecone vector database.

#### Usage

```bash
python backend/scripts/reload_docs_to_pinecone.py
```

**Supports:**
- PDF files
- DOCX files
- TXT files
- Excel files
- Markdown files

---

### 3. `seed_data.py` - Database Seeder

**Location:** `backend/scripts/seed_data.py`

Seeds the database with initial test data.

#### Usage

```bash
python backend/scripts/seed_data.py
```

**Seeds:**
- ERP entities
- Module configurations
- Sample data for testing

---

### 4. `seed_query_patterns.py` - Query Pattern Seeder

**Location:** `backend/scripts/seed_query_patterns.py`

Seeds common query patterns for learning.

#### Usage

```bash
python backend/scripts/seed_query_patterns.py
```

**Purpose:**
- Adds common query patterns
- Improves query understanding
- Enhances search relevance

---

### 5. `init_question_tables.py` - Initialize Question Tables

**Location:** `backend/scripts/init_question_tables.py`

Creates and initializes tables for question generation system.

#### Usage

```bash
python backend/scripts/init_question_tables.py
```

**Creates:**
- `generated_questions` table
- `query_clarifications` table
- Related question tracking

---

## Configuration & Setup Scripts

### 1. `setup_pinecone.py` - Pinecone Setup

**Location:** `backend/scripts/setup_pinecone.py`

Sets up and configures Pinecone vector database.

#### Usage

```bash
python backend/scripts/setup_pinecone.py
```

**What it does:**
- Creates Pinecone index
- Configures dimensions (1536 for OpenAI embeddings)
- Sets up cosine similarity metric
- Validates connection

---

### 2. `fix_pinecone_index.py` - Pinecone Index Fixer

**Location:** `backend/scripts/fix_pinecone_index.py`

Fixes issues with Pinecone index configuration.

#### Usage

```bash
python backend/scripts/fix_pinecone_index.py
```

**Fixes:**
- Index configuration issues
- Dimension mismatches
- Connectivity problems

---

### 3. `create_users_table.py` - Create Users Table

**Location:** `backend/scripts/create_users_table.py`

Creates the users authentication table.

#### Usage

```bash
python backend/scripts/create_users_table.py
```

**Creates:**
- `users` table with authentication fields
- Password hashing setup
- Role-based access control fields

---

### 4. `check_config.py` - Configuration Checker

**Location:** `backend/scripts/check_config.py`

Validates system configuration and environment variables.

#### Usage

```bash
python backend/scripts/check_config.py
```

**Checks:**
- Environment variables
- API keys (OpenAI, Pinecone)
- Database configuration
- File paths
- Dependencies

---

## Monitoring & Analysis Scripts

### 1. `check_docs_status.py` - Document Status Checker

**Location:** `backend/scripts/check_docs_status.py`

Checks the status of documents in the vector database.

#### Usage

```bash
python backend/scripts/check_docs_status.py
```

**Reports:**
- Number of documents loaded
- Embedding status
- Document metadata
- Index statistics

---

### 2. `analyze_query_patterns.py` - Query Pattern Analyzer

**Location:** `backend/scripts/analyze_query_patterns.py`

Analyzes query patterns to improve system performance.

#### Usage

```bash
python backend/scripts/analyze_query_patterns.py
```

**Analyzes:**
- Common query types
- Entity usage patterns
- Search performance
- User interaction patterns

---

## Testing Scripts

### 1. `test_mysql_connection.py` - MySQL Connection Test

**Location:** `backend/scripts/test_mysql_connection.py`

Tests MySQL database connection and configuration.

#### Usage

```bash
python backend/scripts/test_mysql_connection.py
```

**Verifies:**
- MySQL connection
- Database exists
- Tables are created
- Can read/write data
- Connection pooling

---

## Common Workflows

### 🚀 Initial Setup (First Time)

```bash
# 1. Create MySQL database
python backend/scripts/create_mysql_database.py

# 2. Run all conversation migrations (IMPORTANT!)
python backend/scripts/migrate_all_conversation_features.py

# 3. Create users table
python backend/scripts/create_users_table.py

# 4. Setup Pinecone
python backend/scripts/setup_pinecone.py

# 5. Load documents
python backend/scripts/reload_verax_docs.py

# 6. Seed initial data
python backend/scripts/seed_data.py

# 7. Verify everything
python backend/scripts/check_config.py
python backend/scripts/test_mysql_connection.py
```

---

### 🔄 Development Reset

```bash
# 1. Clear database
python backend/scripts/clear_database.py --drop --yes

# 2. Reload documents
python backend/scripts/reload_verax_docs.py

# 3. Seed data
python backend/scripts/seed_data.py
```

---

### 🧪 Testing Preparation

```bash
# 1. Clear chat history only
python backend/scripts/quick_clear_db.py --yes

# 2. Reload test data
python backend/scripts/seed_data.py
```

---

### 📊 Monitoring & Maintenance

```bash
# Check database status
python backend/scripts/clear_database.py --status

# Check document status
python backend/scripts/check_docs_status.py

# Analyze query patterns
python backend/scripts/analyze_query_patterns.py

# Verify configuration
python backend/scripts/check_config.py
```

---

### 🔧 Troubleshooting

```bash
# Test database connection
python backend/scripts/test_mysql_connection.py

# Fix Pinecone issues
python backend/scripts/fix_pinecone_index.py

# Check system configuration
python backend/scripts/check_config.py
```

---

## Environment Variables Required

All scripts require proper configuration in `.env`:

```env
# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=helpdesk_db

# API Keys
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_env

# Application Settings
ENCRYPTION_KEY=your_encryption_key
```

---

## Safety & Best Practices

### ⚠️ Development
- Always run `--status` before destructive operations
- Use `quick_clear_db.py` for routine cleanup
- Test scripts in development environment first

### 🧪 Testing
- Use `clear_database.py --drop` for fresh test environments
- Seed data after clearing
- Verify with status checks

### 🚫 Production
- **NEVER** use clearing scripts in production
- Use proper backup/restore procedures
- Run migrations during maintenance windows
- Always test migrations on staging first

---

## Getting Help

### If Scripts Fail

1. **Check Configuration**
   ```bash
   python backend/scripts/check_config.py
   ```

2. **Test Database Connection**
   ```bash
   python backend/scripts/test_mysql_connection.py
   ```

3. **Verify Environment Variables**
   - Check `.env` file exists
   - Verify all required variables are set
   - Check API keys are valid

4. **Check Logs**
   - Review `backend/logs/backend.log`
   - Check MySQL error logs
   - Review script output for specific errors

### Common Issues

**"Connection pool not initialized"**
- MySQL not running or configured incorrectly
- Run `test_mysql_connection.py`

**"Table doesn't exist"**
- Database not initialized
- Run migration scripts

**"API key invalid"**
- Check OpenAI/Pinecone API keys in `.env`
- Verify keys are active

**"Permission denied"**
- MySQL user lacks permissions
- Grant necessary privileges

---

## Script Dependencies

Most scripts require:
- Python 3.8+
- MySQL 8.0+
- Environment variables configured
- Required Python packages (see `requirements.txt`)

Install dependencies:
```bash
pip install -r backend/requirements.txt
```

---

## Additional Resources

- **Backend README:** `documentation/BACKEND_README.md`
- **Database Guide:** `documentation/database/DATABASE_MIGRATIONS_GUIDE.md`
- **Setup Guide:** `documentation/setup/AUTHENTICATION_SUMMARY.md`
- **Main Documentation:** `documentation/COMPLETE_SYSTEM_DOCUMENTATION.md`

---

**Last Updated:** December 2025  
**Maintainer:** Helpdesk Chatbot Team


