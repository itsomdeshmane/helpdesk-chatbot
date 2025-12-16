# 🔧 Quick Fix - Create Database Tables

## The Error

```
MySql.Data.MySqlClient.MySqlException: 'Table 'erp_demo.aspnetusers' doesn't exist'
```

## Why It Happens

The application is looking for Identity tables in the wrong database. We need to:
1. Create a separate `chatbot_identity` database
2. Create all ASP.NET Identity tables there

---

## ✅ Solution - Run These SQL Commands

### Option 1: Using MySQL Workbench (Easiest)

1. Open **MySQL Workbench**
2. Connect to your localhost server
3. Copy and paste **ALL** the SQL below
4. Click **Execute** (lightning bolt icon)

### Option 2: Using MySQL Command Line

```bash
mysql -u root -p
# Enter your MySQL password when prompted
```

Then paste the SQL below.

---

## 📝 SQL Commands to Execute

```sql
-- Step 1: Create the Identity database
CREATE DATABASE IF NOT EXISTS chatbot_identity 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Step 2: Create the ERP database (if not exists)
CREATE DATABASE IF NOT EXISTS erp_demo 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Step 3: Switch to Identity database
USE chatbot_identity;

-- Step 4: Create Identity Tables

-- AspNetRoles
CREATE TABLE AspNetRoles (
    Id VARCHAR(255) NOT NULL PRIMARY KEY,
    Name VARCHAR(256) NULL,
    NormalizedName VARCHAR(256) NULL UNIQUE,
    ConcurrencyStamp TEXT NULL
) ENGINE=InnoDB;

-- AspNetUsers
CREATE TABLE AspNetUsers (
    Id VARCHAR(255) NOT NULL PRIMARY KEY,
    UserName VARCHAR(256) NULL,
    NormalizedUserName VARCHAR(256) NULL UNIQUE,
    Email VARCHAR(256) NULL,
    NormalizedEmail VARCHAR(256) NULL,
    EmailConfirmed TINYINT(1) NOT NULL DEFAULT 0,
    PasswordHash TEXT NULL,
    SecurityStamp TEXT NULL,
    ConcurrencyStamp TEXT NULL,
    PhoneNumber TEXT NULL,
    PhoneNumberConfirmed TINYINT(1) NOT NULL DEFAULT 0,
    TwoFactorEnabled TINYINT(1) NOT NULL DEFAULT 0,
    LockoutEnd DATETIME(6) NULL,
    LockoutEnabled TINYINT(1) NOT NULL DEFAULT 0,
    AccessFailedCount INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

-- AspNetUserRoles
CREATE TABLE AspNetUserRoles (
    UserId VARCHAR(255) NOT NULL,
    RoleId VARCHAR(255) NOT NULL,
    PRIMARY KEY (UserId, RoleId),
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE,
    FOREIGN KEY (RoleId) REFERENCES AspNetRoles(Id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- AspNetUserClaims
CREATE TABLE AspNetUserClaims (
    Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    UserId VARCHAR(255) NOT NULL,
    ClaimType TEXT NULL,
    ClaimValue TEXT NULL,
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- AspNetUserLogins
CREATE TABLE AspNetUserLogins (
    LoginProvider VARCHAR(128) NOT NULL,
    ProviderKey VARCHAR(128) NOT NULL,
    ProviderDisplayName TEXT NULL,
    UserId VARCHAR(255) NOT NULL,
    PRIMARY KEY (LoginProvider, ProviderKey),
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- AspNetUserTokens
CREATE TABLE AspNetUserTokens (
    UserId VARCHAR(255) NOT NULL,
    LoginProvider VARCHAR(128) NOT NULL,
    Name VARCHAR(128) NOT NULL,
    Value TEXT NULL,
    PRIMARY KEY (UserId, LoginProvider, Name),
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- AspNetRoleClaims
CREATE TABLE AspNetRoleClaims (
    Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    RoleId VARCHAR(255) NOT NULL,
    ClaimType TEXT NULL,
    ClaimValue TEXT NULL,
    FOREIGN KEY (RoleId) REFERENCES AspNetRoles(Id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Step 5: Verify tables created
SHOW TABLES;
```

---

## ✅ Verify Setup

After running the SQL, verify:

```sql
-- Check databases exist
SHOW DATABASES LIKE '%chatbot%';
SHOW DATABASES LIKE '%erp%';

-- Check tables in chatbot_identity
USE chatbot_identity;
SHOW TABLES;

-- Should show 7 tables:
-- AspNetRoles
-- AspNetUsers
-- AspNetUserRoles
-- AspNetUserClaims
-- AspNetUserLogins
-- AspNetUserTokens
-- AspNetRoleClaims
```

---

## 🚀 Test Your Application

Once the tables are created:

1. **Start your application:**
   ```bash
   dotnet run
   ```

2. **Test registration:**
   ```bash
   curl -X POST "http://localhost:5000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@example.com",
       "name": "Steve Scaramuzzino",
       "password": "Test123$"
     }'
   ```

3. **Expected Response:**
   ```json
   {
     "message": "User registered successfully",
     "email": "admin@example.com",
     "name": "Steve Scaramuzzino"
   }
   ```

---

## 📊 What You Now Have

### Two Separate Databases:

1. **`chatbot_identity`** - User authentication
   - AspNetUsers
   - AspNetRoles
   - AspNetUserRoles
   - AspNetUserClaims
   - AspNetUserLogins
   - AspNetUserTokens
   - AspNetRoleClaims

2. **`erp_demo`** - Your application data
   - (Your ERP tables go here)
   - Used for SQL queries from the chatbot

---

## 🎉 Done!

The error should be resolved. Your application will now:
- Store users in `chatbot_identity`
- Query ERP data from `erp_demo`

**If you still see errors, check:**
- MySQL is running
- Connection strings in `appsettings.json` are correct
- You ran ALL the SQL commands above


