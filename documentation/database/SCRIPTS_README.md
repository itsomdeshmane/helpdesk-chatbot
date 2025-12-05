# Database Management Scripts

Collection of utility scripts for managing the helpdesk database.

---

## 🚀 **IMPORTANT: Run This First!**

### **Enable Conversation Features (Required)**

Before using the chatbot, run this **one-time migration**:

```bash
python migrate_all_conversation_features.py
```

**What it does:**
- ✅ Creates session management tables
- ✅ Enables AI-powered context tracking
- ✅ Adds intelligent pronoun resolution
- ✅ Enables multi-turn conversations with memory
- ✅ Safe to run multiple times (idempotent)

**See:** `../MIGRATION_GUIDE.md` for complete instructions.

**After migration:** Restart your server and the chatbot will remember conversation context!

---

## Scripts Overview

### 1. `clear_database.py` - Full Database Management

Comprehensive script with multiple options for clearing/resetting the database.

#### Usage

```bash
# Show database status
python clear_database.py --status

# Clear all data (with confirmation)
python clear_database.py --clear

# Clear all data (no confirmation)
python clear_database.py --clear --yes

# Clear with TRUNCATE (faster)
python clear_database.py --clear --truncate

# Drop and recreate all tables
python clear_database.py --drop

# Clear but keep entities
python clear_database.py --clear --keep-entities
```

#### Options

- `--status` - Show current database status
- `--clear` - Clear all data from tables
- `--truncate` - Use TRUNCATE instead of DELETE (faster)
- `--drop` - Drop all tables and recreate fresh
- `--keep-entities` - Preserve erp_entities table
- `--yes, -y` - Skip confirmation prompt

#### Examples

```bash
# Development: Clear everything and start fresh
python clear_database.py --drop --yes

# Testing: Clear data but keep entities
python clear_database.py --clear --truncate --keep-entities --yes

# Check what's in the database
python clear_database.py --status
```

---

### 2. `quick_clear_db.py` - Quick Chat History Clear

Simple script to clear only chat history, preserving entities and structure.

#### Usage

```bash
# Clear chat history (with confirmation)
python quick_clear_db.py

# Clear without confirmation
python quick_clear_db.py --yes
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

### 3. `test_mysql_connection.py` - Database Connection Test

Test if MySQL is properly configured and accessible.

#### Usage

```bash
python test_mysql_connection.py
```

Verifies:
- MySQL connection
- Database exists
- Tables are created
- Can read/write data

---

## Common Scenarios

### Scenario 1: Fresh Start (Development)

```bash
# Drop everything and recreate
python clear_database.py --drop --yes
```

**Result:**
- All tables dropped
- Fresh schema created
- Default entities loaded
- Ready for testing

---

### Scenario 2: Clear Test Data

```bash
# Clear data but keep structure
python clear_database.py --clear --truncate --yes
```

**Result:**
- All data deleted
- Tables remain
- Default entities reloaded
- Fast operation

---

### Scenario 3: Clear Chat History Only

```bash
# Quick clear for chat data
python quick_clear_db.py --yes
```

**Result:**
- Chat history cleared
- Entities preserved
- Modules preserved
- Minimal disruption

---

### Scenario 4: Check Database Status

```bash
# See what's in the database
python clear_database.py --status
```

**Output:**
```
DATABASE STATUS
======================================================================
Found 8 tables:

  📊 chat_interactions              45 records
  📊 erp_entities                   18 records
  📊 erp_modules                    10 records
  📊 generated_questions           120 records
  ...

Total:                              245 records
======================================================================
```

---

## Safety Features

### Confirmation Prompts

All destructive operations require confirmation unless `--yes` is used:

```
⚠️  WARNING: This will delete data from the database!
   This will DELETE all records from all tables.

Are you sure you want to continue? (yes/no):
```

### Status Display

Before clearing, the script shows what will be affected:

```
DATABASE STATUS
======================================================================
Found 5 tables:

  📊 chat_interactions              123 records
  📊 erp_entities                    18 records
  ...
```

### Preservation Options

Use `--keep-entities` to preserve important reference data:

```bash
python clear_database.py --clear --keep-entities
```

---

## Methods Comparison

### DELETE (default)
- **Speed:** Slow
- **Safe:** Yes
- **Triggers:** Yes
- **Auto-increment:** Preserved
- **Use when:** Need to preserve auto-increment values

### TRUNCATE
- **Speed:** Fast
- **Safe:** Yes  
- **Triggers:** No
- **Auto-increment:** Reset to 0
- **Use when:** Want to reset IDs and clear quickly

### DROP
- **Speed:** Fast
- **Safe:** No (recreates)
- **Triggers:** N/A
- **Auto-increment:** Reset to 0
- **Use when:** Want completely fresh start

---

## Troubleshooting

### "Connection pool not initialized"

**Problem:** Database not configured or MySQL not running

**Solution:**
1. Check if MySQL is running
2. Verify `.env` file has correct credentials
3. Run `test_mysql_connection.py`

### "Table doesn't exist"

**Problem:** Database not initialized

**Solution:**
```bash
# Reinitialize database
python clear_database.py --drop --yes
```

### "Permission denied"

**Problem:** MySQL user lacks permissions

**Solution:**
Grant permissions to your MySQL user:
```sql
GRANT ALL PRIVILEGES ON helpdesk_db.* TO 'your_user'@'localhost';
FLUSH PRIVILEGES;
```

---

## Best Practices

### Development
```bash
# Regular cleanup during development
python quick_clear_db.py --yes
```

### Testing
```bash
# Full reset before test suite
python clear_database.py --drop --yes
```

### Production
```bash
# Never use these scripts in production!
# Use proper backup/restore procedures instead
```

---

## Environment Variables

Required in `.env`:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=helpdesk_db
```

---

## Script Location

All scripts are in the `backend/scripts/` directory:

```
backend/
├── scripts/
│   ├── clear_database.py       # Full database management
│   ├── quick_clear_db.py       # Quick chat history clear
│   ├── test_mysql_connection.py # Connection test
│   └── README.md               # This file
```

---

## Support

For issues or questions:
1. Check script output for specific error messages
2. Run `test_mysql_connection.py` to verify setup
3. Check MySQL logs for database errors
4. Review `.env` configuration

