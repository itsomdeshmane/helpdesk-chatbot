# Settings Feature Guide

## Overview

The settings feature allows users to:
1. **Toggle between Light and Dark themes**
2. **Configure database connections dynamically**
3. **Store connection credentials securely** (encrypted)

## Features

### 1. Theme Toggle (Light/Dark Mode)

**Location**: Settings → General Tab

**Features**:
- Instant theme switching
- Persisted to localStorage
- Smooth CSS transitions
- Uses CSS variables for theming

**Implementation**:
- CSS variables in `theme.css`
- Theme state managed in React
- Applied via `data-theme` attribute on `html` element

### 2. Database Connection Configuration

**Location**: Settings → Database Tab

**Features**:
- Save multiple database connections per user
- Encrypted storage of credentials
- Test connection before saving
- Auto-load existing connections

**Security**:
- Passwords encrypted using Fernet (symmetric encryption)
- Never returned to frontend
- Encrypted at rest in database
- Separate encryption key from JWT

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install cryptography==41.0.7
```

### 2. Generate Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the generated key to your `.env` file:

```env
ENCRYPTION_KEY=your-generated-44-character-key
```

### 3. Run Database Migration

```bash
cd backend/database/migrations
python run_migrations.py
```

This creates the `user_database_connections` table:
- Stores host, port, database name, username
- Encrypted password storage
- Unique constraint per user/tenant

## Database Schema

```sql
CREATE TABLE user_database_connections (
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

## API Endpoints

### GET `/api/settings/database-connection`
Get user's saved database connection (password excluded)

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "success": true,
  "data": {
    "host": "localhost",
    "port": 3306,
    "database": "my_database",
    "username": "db_user"
  }
}
```

### POST `/api/settings/database-connection`
Save/update database connection

**Headers**: `Authorization: Bearer <token>`

**Body**:
```json
{
  "host": "localhost",
  "port": 3306,
  "database": "my_database",
  "username": "db_user",
  "password": "secret"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Database connection saved successfully"
}
```

### POST `/api/settings/test-database-connection`
Test connection without saving

**Headers**: `Authorization: Bearer <token>`

**Body**: Same as save endpoint

**Response**:
```json
{
  "success": true,
  "message": "Connection successful"
}
```

### GET `/api/settings/user-connection-string`
Get connection string for internal use

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "success": true,
  "connection_string": "host=localhost;port=3306;database=my_db;user=user;password=decrypted"
}
```

## UI Components

### Settings Modal (`Settings.js`)

**Features**:
- Tab-based interface (General, Database)
- Form validation
- Loading states
- Success/error feedback
- Responsive design

**Styling**: Uses CSS variables for theme support

### Settings Button

**Location**: Left sidebar bottom

**Styling**:
```css
.settings-btn {
  width: 100%;
  background: var(--bg-primary);
  color: var(--text-primary);
  /* Theme-aware styling */
}
```

## Theme System

### CSS Variables

**Light Theme**:
```css
:root {
  --bg-primary: #ffffff;
  --text-primary: #1a1a1a;
  --accent-color: #10a37f;
  /* ... */
}
```

**Dark Theme**:
```css
[data-theme="dark"] {
  --bg-primary: #1a1a1a;
  --text-primary: #ececf1;
  --accent-color: #10a37f;
  /* ... */
}
```

### Applying Theme

```javascript
document.documentElement.setAttribute('data-theme', 'dark');
```

## Security Considerations

1. **Encryption**:
   - Uses Fernet (AES-128 in CBC mode)
   - Unique encryption key (44 characters base64)
   - PBKDF2 key derivation for extra security

2. **Password Handling**:
   - Never stored in plain text
   - Never returned to frontend
   - Encrypted before database insert
   - Decrypted only when needed for connections

3. **Key Management**:
   - Store `ENCRYPTION_KEY` in environment variables
   - Different from JWT secret
   - Never commit to git
   - Rotate regularly in production

4. **Database Security**:
   - Foreign key constraints
   - Cascade delete on user removal
   - Unique constraint per user/tenant
   - Indexes for performance

## Usage Example

### Frontend

```javascript
// Open settings
<button onClick={() => setSettingsOpen(true)}>
  Settings
</button>

// Settings component
<Settings
  isOpen={settingsOpen}
  onClose={() => setSettingsOpen(false)}
  currentTheme={theme}
  onThemeChange={setTheme}
/>
```

### Backend (Using User's Connection)

```python
from routers.settings import get_user_connection_string

# Get user's connection string
result = await get_user_connection_string(current_user=user)
connection_string = result['connection_string']

# Use for queries
db_service = get_database_query_service()
result = await db_service.execute_query(sql, connection_string)
```

## Testing

### Manual Testing

1. **Theme Toggle**:
   - Open settings
   - Switch between Light/Dark
   - Verify all UI elements update
   - Refresh page and verify persistence

2. **Database Connection**:
   - Open Settings → Database tab
   - Enter connection details
   - Click "Test Connection"
   - Verify success/failure message
   - Click "Save Connection"
   - Reload page and verify data persists

### Encryption Testing

```bash
cd backend/utils
python encryption.py
```

Expected output:
```
Original: my_secret_password123
Encrypted: gAAAAABl...
Decrypted: my_secret_password123
Test PASSED
```

## Troubleshooting

### Issue: "ENCRYPTION_KEY not found"

**Solution**: Add to `.env`:
```env
ENCRYPTION_KEY=your-generated-key
```

### Issue: "cryptography module not found"

**Solution**:
```bash
pip install cryptography==41.0.7
```

### Issue: "Table user_database_connections doesn't exist"

**Solution**:
```bash
cd backend/database/migrations
python run_migrations.py
```

### Issue: Theme not persisting

**Solution**: Check browser localStorage, ensure `theme.css` is imported

### Issue: Connection test fails

**Solution**: Check:
- Database server is running
- Credentials are correct
- Firewall allows connection
- MySQL port is accessible

## Future Enhancements

1. **Multiple Connections**:
   - Allow users to save multiple named connections
   - Connection dropdown in chat interface

2. **Connection Pooling**:
   - Cache active connections
   - Auto-reconnect on failure

3. **Import/Export**:
   - Export connection settings (encrypted)
   - Import from file

4. **Advanced Settings**:
   - Font size customization
   - Language preferences
   - Notification settings

5. **Theme Customization**:
   - Custom color schemes
   - Accent color picker
   - Font family selection

## Summary

The settings feature provides:
- ✅ Light/Dark theme toggle
- ✅ Secure database connection management
- ✅ Encrypted credential storage
- ✅ User-friendly UI
- ✅ API-first architecture
- ✅ Production-ready security

All configuration is per-user and tenant-isolated, ensuring multi-tenancy support.


