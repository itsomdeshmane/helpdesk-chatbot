# Settings Connection Test - Debug Guide

## Issue Fixed

The database connection test was failing due to incorrect response handling in the frontend.

## Changes Made

### 1. Backend (`routers/settings.py`)
- ✅ Fixed pymysql connection parameter: `database` → `db`
- ✅ Added comprehensive logging for debugging
- ✅ Increased connection timeout to 10 seconds
- ✅ Added charset='utf8mb4' for better compatibility
- ✅ Better error messages in response

### 2. Frontend (`components/Settings.js`)
- ✅ Fixed response data access: `response.success` → `response.data.success`
- ✅ Added console logging for debugging
- ✅ Added alert messages showing actual error details
- ✅ Fixed all three endpoints: load, test, and save

### 3. API Service (`services/api.service.js`)
- ✅ Added generic `get()` method
- ✅ Added generic `post()` method
- ✅ Added generic `put()` method
- ✅ Added generic `delete()` method

## API Endpoints

The settings API is available at:

```
GET  /settings/database-connection          # Load saved connection
POST /settings/database-connection          # Save connection
POST /settings/test-database-connection     # Test connection
GET  /settings/user-connection-string       # Get connection string (internal)
```

## Testing the Connection

### 1. Open Browser Console (F12)

Check for logs when you click "Test Connection":

**Expected Logs:**
```
🌐 API Request: POST /settings/test-database-connection
Testing connection with: {host: "localhost", port: 3306, ...}
✅ API Response: /settings/test-database-connection 200
Test connection response: {data: {success: true, message: "..."}}
✅ Connection test successful
```

**If Failed:**
```
❌ Connection test failed: {message details}
```

### 2. Check Backend Terminal

Look for these logs:

**Success:**
```
Testing database connection for user {username}
Connection details: host=localhost, port=3306, database=mydb, username=user
Connection established, testing with query...
Test query result: {'test': 1}
✅ Database connection test successful
```

**Failure:**
```
❌ MySQL connection test failed: {error details}
```

## Common Issues & Solutions

### Issue 1: "Connection failed: Network error"
**Cause**: Backend not running or wrong port

**Solution**:
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Issue 2: "MySQL Error: (2003) Can't connect to MySQL"
**Cause**: MySQL server not running or wrong credentials

**Solution**:
1. Start MySQL service
2. Verify credentials:
   - Host: `localhost` or IP address
   - Port: `3306` (default)
   - Database: Must exist
   - Username/Password: Must be correct

### Issue 3: "MySQL Error: (1044) Access denied for user"
**Cause**: User doesn't have permissions

**Solution**:
```sql
GRANT ALL PRIVILEGES ON database_name.* TO 'username'@'localhost';
FLUSH PRIVILEGES;
```

### Issue 4: "MySQL Error: (1049) Unknown database"
**Cause**: Database doesn't exist

**Solution**:
```sql
CREATE DATABASE database_name;
```

### Issue 5: "response.data is undefined"
**Cause**: Old cached frontend code

**Solution**:
1. Hard refresh browser: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. Clear browser cache
3. Restart React dev server:
   ```bash
   cd frontend
   npm start
   ```

## Manual Test with cURL

Test the endpoint directly:

```bash
# Login first to get token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_user","password":"your_pass"}'

# Copy the token from response, then test connection
curl -X POST http://localhost:8000/settings/test-database-connection \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "host": "localhost",
    "port": 3306,
    "database": "test_db",
    "username": "root",
    "password": "your_password"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Connection successful"
}
```

## Verify Database Table Exists

Run this migration if the table doesn't exist:

```bash
cd backend/database/migrations
python run_migrations.py
```

Or manually create:

```sql
CREATE TABLE IF NOT EXISTS user_database_connections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    tenant_id VARCHAR(100) NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INT NOT NULL DEFAULT 3306,
    database_name VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL,
    encrypted_password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_tenant_connection (user_id, tenant_id)
);
```

## Testing Checklist

- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 3000 or 4200
- [ ] MySQL server running
- [ ] Database exists
- [ ] User has correct permissions
- [ ] Browser console open (F12)
- [ ] Backend terminal visible
- [ ] Test with correct credentials
- [ ] Check logs for detailed error messages

## Success Indicators

✅ **Frontend Console:**
- "Testing connection with: ..."
- "✅ Connection test successful"

✅ **Backend Terminal:**
- "Testing database connection for user ..."
- "✅ Database connection test successful"

✅ **UI:**
- "✓ Connection successful!" message appears

## Still Having Issues?

1. **Check browser console** for JavaScript errors
2. **Check backend terminal** for Python errors
3. **Verify MySQL credentials** by connecting manually:
   ```bash
   mysql -h localhost -P 3306 -u username -p database_name
   ```
4. **Test API endpoint** with cURL (see above)
5. **Check firewall** settings if connecting to remote database
6. **Verify React app can reach backend**: `curl http://localhost:8000/docs`

---

**The connection test should now work correctly with proper error messages!** 🎯

