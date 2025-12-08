# Fix: User ID and Tenant ID Always Empty

## Problem

In the logs, `user_id` and `tenant_id` were always showing as empty even though users were logged in:

```
✅ User logged in: omdeshmane (Role: user)
...
{"timestamp": "...", "user_id": "", "tenant_id": "default", ...}
```

## Root Cause

The frontend **was not sending the Authorization token** in the streaming API request, so the backend couldn't identify the authenticated user.

### Frontend Issue

**Before (Wrong):**
```javascript
const response = await fetch('http://localhost:8000/chat/query/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'text/event-stream',
    // ❌ NO Authorization header!
  },
  body: JSON.stringify({...})
});
```

**Result:** Backend received no auth token → `current_user = None` → `user_id = ""` → `tenant_id = "default"`

---

## Solution

### 1. Frontend Fix: Send Authorization Token

**File:** `frontend/src/components/ChatWindow.js`

**After (Fixed):**
```javascript
// Get auth token from localStorage
const token = localStorage.getItem('token');

// Prepare headers with auth token if available
const headers = {
  'Content-Type': 'application/json',
  'Accept': 'text/event-stream',
};

if (token) {
  headers['Authorization'] = `Bearer ${token}`;  // ✅ Send token!
}

const response = await fetch('http://localhost:8000/chat/query/stream', {
  method: 'POST',
  headers: headers,
  body: JSON.stringify({...})
});
```

### 2. Backend Enhancement: Use User's Tenant

**Files:** `backend/routers/chat.py`, `backend/routers/streaming.py`

**Added logic to use authenticated user's tenant_id:**
```python
# Extract user_id and tenant_id from current_user if available
user_id = current_user.get('username') if current_user else None
user_tenant_id = current_user.get('tenant_id', 'default') if current_user else 'default'

# Override tenant_id if user is authenticated
if current_user and user_tenant_id and user_tenant_id != 'default':
    tenant_id = user_tenant_id
    print(f"   🏢 Using user's tenant: {tenant_id}")

if user_id:
    print(f"   👤 User-specific conversation: {user_id} (Tenant: {tenant_id})")
```

---

## How Authentication Works Now

### 1. User Logs In

**Request:**
```http
POST /auth/login
{
  "username": "omdeshmane",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "omdeshmane",
    "email": "om@example.com",
    "role": "user",
    "tenant_id": "company_abc"
  }
}
```

**Frontend stores token:**
```javascript
localStorage.setItem('token', access_token);
```

### 2. User Asks Question (Streaming)

**Request:**
```http
POST /chat/query/stream
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...  ✅ Token sent!
  Content-Type: application/json
Body:
{
  "query": "What is a Job?",
  "tenant_id": "default",
  "session_id": null
}
```

**Backend extracts user from token:**
```python
# In get_current_user_optional()
payload = jwt.decode(token, SECRET_KEY)
current_user = {
  "user_id": 1,
  "username": "omdeshmane",
  "email": "om@example.com",
  "role": "user",
  "tenant_id": "company_abc"
}
```

**Backend uses user's data:**
```python
user_id = "omdeshmane"           # ✅ From token
tenant_id = "company_abc"        # ✅ From token (overrides request body)
session_id = conv_manager.create_session(tenant_id, user_id)
```

**Logs now show:**
```
👤 User-specific conversation: omdeshmane (Tenant: company_abc)
✅ New session created: abc-123-def
{"user_id": "omdeshmane", "tenant_id": "company_abc", ...}
```

---

## JWT Token Structure

The authentication token contains:

```json
{
  "user_id": 1,
  "username": "omdeshmane",
  "email": "om@example.com",
  "role": "user",
  "tenant_id": "company_abc",
  "exp": 1733745600,
  "iat": 1733659200
}
```

**Fields used:**
- `username` → Stored as `user_id` in conversations
- `tenant_id` → Used to filter data per organization
- `role` → Used for permissions (admin, user, viewer)
- `exp` → Token expiry timestamp
- `iat` → Token issued timestamp

---

## Benefits of Fix

### 1. User-Specific Conversations ✅

Each user now has their own conversation history:

```sql
SELECT * FROM conversations WHERE user_id = 'omdeshmane';
-- Only shows omdeshmane's conversations
```

### 2. Multi-Tenant Support ✅

Each organization's data is isolated:

```sql
SELECT * FROM chat_interactions WHERE tenant_id = 'company_abc';
-- Only shows company_abc's data
```

### 3. Better Analytics ✅

Track usage per user and per tenant:

```sql
SELECT 
  user_id,
  COUNT(*) as query_count,
  AVG(response_time) as avg_time
FROM chat_interactions
WHERE tenant_id = 'company_abc'
GROUP BY user_id;
```

### 4. Proper Security ✅

Users can only see/delete their own conversations:

```python
# Only returns conversations for authenticated user
conversations = get_user_conversations(tenant_id, user_id)
```

---

## Testing

### Test 1: Check Token is Sent

**In browser console:**
```javascript
// Check token exists
console.log(localStorage.getItem('token'));

// Monitor network request
// Network tab → /chat/query/stream → Headers
// Should see: Authorization: Bearer eyJ0...
```

### Test 2: Check Logs

**Backend terminal should show:**
```
👤 User-specific conversation: omdeshmane (Tenant: company_abc)
✅ New session created: abc-123
{"user_id": "omdeshmane", "tenant_id": "company_abc", ...}
```

### Test 3: Check Database

**Query conversations table:**
```sql
SELECT session_id, user_id, tenant_id, created_at 
FROM conversations 
ORDER BY created_at DESC 
LIMIT 5;
```

**Should show:**
```
session_id                           | user_id      | tenant_id    | created_at
-------------------------------------|--------------|--------------|-------------------
abc-123-def-456                      | omdeshmane   | company_abc  | 2024-12-08 10:30:00
```

---

## Troubleshooting

### Issue: Still showing empty user_id

**Check:**
1. Token exists in localStorage: `localStorage.getItem('token')`
2. Token is valid: Decode at [jwt.io](https://jwt.io)
3. Token is being sent: Check Network tab → Headers
4. Backend is receiving token: Check backend logs

**Debug:**
```javascript
// Frontend - Check token
const token = localStorage.getItem('token');
console.log('Token:', token ? 'Present' : 'Missing');

// Backend - Check current_user
print(f"Current user: {current_user}")
```

### Issue: Wrong tenant_id

**Check user's tenant_id in database:**
```sql
SELECT username, tenant_id FROM users WHERE username = 'omdeshmane';
```

**Update if needed:**
```sql
UPDATE users SET tenant_id = 'correct_tenant' WHERE username = 'omdeshmane';
```

### Issue: Token expired

**Error:** "Token has expired"

**Solution:** Login again to get new token

---

## Files Modified

1. **`frontend/src/components/ChatWindow.js`**
   - Added Authorization header with JWT token
   - Token retrieved from localStorage

2. **`backend/routers/chat.py`**
   - Extract user_id and tenant_id from auth token
   - Use user's tenant instead of request body tenant

3. **`backend/routers/streaming.py`**
   - Extract user_id and tenant_id from auth token
   - Use user's tenant instead of request body tenant
   - Pass to session creation

---

## Summary

**Before:** ❌
- Frontend: No auth token sent
- Backend: `user_id = ""`, `tenant_id = "default"`
- Result: Anonymous sessions, no user tracking

**After:** ✅
- Frontend: Auth token sent in every request
- Backend: `user_id = "omdeshmane"`, `tenant_id = "company_abc"`
- Result: User-specific sessions, proper multi-tenant support

The system now properly tracks which user asks which question and ensures data isolation between organizations! 🎉

