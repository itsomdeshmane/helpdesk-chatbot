# 🗄️ Database Setup Instructions

## Overview

Your application now uses **TWO separate MySQL databases**:

1. **`chatbot_identity`** - Stores user authentication data (ASP.NET Identity tables)
2. **`erp_demo`** - Stores your ERP application data and business logic

---

## 📋 Quick Setup

### Option 1: Run SQL Script (Recommended)

1. **Open MySQL command line or MySQL Workbench**

2. **Run the setup script:**
   ```bash
   mysql -u root -proot123 < setup_databases.sql
   ```

   Or in MySQL Workbench:
   - Open `setup_databases.sql`
   - Execute the entire script

3. **Verify databases created:**
   ```sql
   SHOW DATABASES;
   ```
   
   You should see:
   - `chatbot_identity`
   - `erp_demo`

### Option 2: Manual Setup

**Step 1: Create Databases**
```sql
CREATE DATABASE chatbot_identity CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE erp_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**Step 2: Create Identity Tables**
```sql
USE chatbot_identity;
-- Then run the table creation statements from setup_databases.sql
```

---

## 🔧 Connection Strings

Your `appsettings.json` is already configured:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "server=localhost;database=erp_demo;user=root;password=root123;",
    "IdentityConnection": "server=localhost;database=chatbot_identity;user=root;password=root123;"
  }
}
```

### What Each Connection Does:

- **`IdentityConnection`** (chatbot_identity):
  - User registration
  - Login/logout
  - Password management
  - Role/claims management

- **`DefaultConnection`** (erp_demo):
  - Your ERP business data
  - SQL query execution from chatbot
  - Schema extraction for embeddings
  - Application reports

---

## ✅ Verify Setup

### 1. Check Databases Exist
```sql
SHOW DATABASES LIKE 'chatbot%';
SHOW DATABASES LIKE 'erp%';
```

### 2. Check Identity Tables Created
```sql
USE chatbot_identity;
SHOW TABLES;
```

You should see:
- AspNetUsers
- AspNetRoles
- AspNetUserRoles
- AspNetUserClaims
- AspNetUserLogins
- AspNetUserTokens
- AspNetRoleClaims

### 3. Test Application Connection

Run your application:
```bash
dotnet run
```

Try to register a user:
```bash
curl -X POST "http://localhost:5000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "name": "Steve Scaramuzzino",
    "password": "Test123$"
  }'
```

---

## 📊 Add Sample Data to ERP Demo

You can add your ERP tables to the `erp_demo` database:

```sql
USE erp_demo;

-- Example: Create sample tables
CREATE TABLE Products (
    ProductId INT AUTO_INCREMENT PRIMARY KEY,
    ProductName VARCHAR(200) NOT NULL,
    CategoryId INT,
    UnitPrice DECIMAL(10,2),
    UnitsInStock INT,
    CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Orders (
    OrderId INT AUTO_INCREMENT PRIMARY KEY,
    CustomerId INT,
    OrderDate DATETIME,
    TotalAmount DECIMAL(10,2),
    Status VARCHAR(50)
);

-- Add more tables as needed for your ERP system
```

---

## 🚀 Next Steps

After setting up the databases:

1. **Start the application:**
   ```bash
   dotnet run
   ```

2. **Register your first user:**
   - Use the registration endpoint
   - This will create records in `chatbot_identity.AspNetUsers`

3. **Generate schema embeddings:**
   ```bash
   curl -X POST "http://localhost:5000/api/schema/generate-embeddings"
   ```
   - This will analyze the `erp_demo` database schema

4. **Start querying:**
   - Ask questions about your ERP data
   - The chatbot will use `erp_demo` for SQL queries

---

## 🔍 Troubleshooting

### Error: "Access denied for user 'root'"
- Check your MySQL password
- Update connection strings in `appsettings.json`

### Error: "Database 'chatbot_identity' doesn't exist"
- Run the `setup_databases.sql` script
- Or create the database manually

### Error: "Table 'AspNetUsers' doesn't exist"
- Run the complete `setup_databases.sql` script
- Make sure all Identity tables are created

### Migration Issues
If you prefer using EF Core migrations:
```bash
dotnet ef migrations add InitialIdentity --context AppDbContext
dotnet ef database update --context AppDbContext
```

---

## 📝 Database Architecture

```
┌─────────────────────────────────────┐
│  Analytics Chatbot Application     │
└─────────────────────────────────────┘
           │              │
           │              │
           ▼              ▼
┌──────────────────┐  ┌──────────────────┐
│ chatbot_identity │  │    erp_demo      │
├──────────────────┤  ├──────────────────┤
│ AspNetUsers      │  │ Products         │
│ AspNetRoles      │  │ Orders           │
│ AspNetUserRoles  │  │ Customers        │
│ AspNetUserClaims │  │ Invoices         │
│ (Identity Data)  │  │ (Your ERP Data)  │
└──────────────────┘  └──────────────────┘
  Authentication          Business Logic
```

---

## ✨ Benefits of Separate Databases

✅ **Security** - User credentials isolated from business data  
✅ **Scalability** - Can scale databases independently  
✅ **Maintenance** - Easier to backup and restore separately  
✅ **Clarity** - Clear separation of concerns  
✅ **Flexibility** - Can deploy to different servers if needed  

---

Your databases are now properly configured! 🎉


