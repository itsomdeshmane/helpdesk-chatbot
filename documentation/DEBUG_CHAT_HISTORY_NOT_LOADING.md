# Debug: Chat History Not Loading

## Quick Debugging Steps

### Step 1: Open Browser Console

**Chrome/Edge:** Press `F12` → Console tab  
**Firefox:** Press `F12` → Console tab

### Step 2: Clear Cache and Login

```javascript
// In browser console, run:
localStorage.clear();
location.reload();
```

Then login again and watch the console output.

---

## Expected Console Output

### Successful History Load

```
🔐 Auth state service initialized
✅ Login successful: omdeshmane
🧹 Cleared local chat state
📜 Loading user conversation history...
🔄 Starting loadRecentConversation...
🔍 Fetching conversations (limit: 1)...
📡 Response status: 200
✅ Received 1 conversations
📋 Most recent conversation: abc-123 (status: active, 5 messages)
📥 Fetching full details for session: abc-123
📡 Response status: 200
✅ Successfully loaded conversation: abc-123 with 5 messages
✅ Restored 5 previous messages from session abc-123
```

### No Previous History (Normal)

```
✅ Login successful: newuser
🧹 Cleared local chat state
📜 Loading user conversation history...
🔄 Starting loadRecentConversation...
🔍 Fetching conversations (limit: 1)...
📡 Response status: 200
✅ Received 0 conversations
ℹ️  No previous conversations found (user has clean slate)
```

### Error Cases

#### Case 1: 404 Endpoint Not Found

```
❌ API error: 404 - <!DOCTYPE html>...
```

**Fix:** Backend endpoints not registered. Run:
```bash
cd backend
# Check if user_conversations router is included
grep "user_conversations" app.py
```

Should see:
```python
app.include_router(user_conversations.router, prefix="/conversations")
```

#### Case 2: 401 Unauthorized

```
❌ API error: 401 - {"detail":"Invalid authentication credentials"}
```

**Fix:** Token not being sent or is invalid.

Check:
```javascript
// In console
localStorage.getItem('token')
// Should show: "eyJ0eXAiOiJKV1QiLCJhbGc..."
```

If null or invalid, login again.

#### Case 3: Network Error

```
❌ Error fetching conversations: NetworkError
```

**Fix:** Backend not running or CORS issue.

Check:
- Backend is running: `http://localhost:8000/docs`
- CORS is configured correctly

---

## Manual API Test

### Test 1: Get My Conversations

Open browser console and run:

```javascript
const token = localStorage.getItem('token');

fetch('http://localhost:8000/conversations/my-conversations?limit=5', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(r => r.json())
.then(data => console.log('Conversations:', data))
.catch(e => console.error('Error:', e));
```

**Expected Response:**
```json
{
  "user_id": "omdeshmane",
  "conversation_count": 2,
  "conversations": [
    {
      "session_id": "abc-123",
      "title": "What is a Job?",
      "status": "active",
      "message_count": 5,
      "created_at": "2024-12-08T10:00:00",
      "updated_at": "2024-12-08T10:30:00"
    }
  ]
}
```

### Test 2: Get Conversation Details

```javascript
const token = localStorage.getItem('token');
const sessionId = 'abc-123'; // Use session_id from test 1

fetch(`http://localhost:8000/conversation/${sessionId}`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(r => r.json())
.then(data => console.log('Messages:', data))
.catch(e => console.error('Error:', e));
```

**Expected Response:**
```json
{
  "session_id": "abc-123",
  "message_count": 5,
  "messages": [
    {
      "query": "What is a Job?",
      "response": "A Job is...",
      "timestamp": "2024-12-08T10:00:00"
    }
  ]
}
```

---

## Common Issues

### Issue 1: Endpoint Returns 404

**Symptom:**
```
❌ API error: 404 - Not Found
```

**Check Backend:**
```bash
# In backend terminal, look for:
GET /conversations/my-conversations -> 404
```

**Solution:**
```bash
# Restart backend
cd backend
python app.py

# Or if using uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Verify in startup logs:
```
INFO:     Started server process
✅ Connected to Pinecone index
```

### Issue 2: User ID Not Set

**Symptom:**
Backend logs show:
```
{"user_id": "", "tenant_id": "default", ...}
```

**Solution:** Token not being sent.

Check `ChatWindow.js`:
```javascript
// Should have:
const token = localStorage.getItem('token');
if (token) {
  headers['Authorization'] = `Bearer ${token}`;
}
```

### Issue 3: Session Belongs to Different User

**Symptom:**
Backend logs show:
```
🚨 SECURITY: User alice tried to access session belonging to bob
```

**Solution:** Working as intended! User cannot see other users' chats.

Check database:
```sql
SELECT session_id, user_id, tenant_id 
FROM conversations 
WHERE status = 'active'
ORDER BY created_at DESC
LIMIT 10;
```

---

## Database Checks

### Check if User Has Conversations

```sql
-- Replace 'omdeshmane' with actual username
SELECT 
    c.session_id,
    c.user_id,
    c.status,
    c.created_at,
    COUNT(ci.id) as message_count
FROM conversations c
LEFT JOIN chat_interactions ci ON ci.conversation_id = c.id
WHERE c.user_id = 'omdeshmane'
GROUP BY c.id
ORDER BY c.updated_at DESC;
```

**Expected:** Rows with message_count > 0

**If empty:** User has no chat history (normal for new users)

### Check if Session Has Messages

```sql
-- Replace with actual session_id
SELECT query, response, created_at
FROM chat_interactions ci
JOIN conversations c ON c.id = ci.conversation_id
WHERE c.session_id = 'abc-123'
ORDER BY ci.message_order;
```

**Expected:** Multiple rows with queries and responses

---

## Force History Load

If automatic loading isn't working, manually trigger it:

```javascript
// In browser console after login
const conversationService = require('./services/conversation.service').default;
const chatState = require('./services/chat.state').default;

(async () => {
  const result = await conversationService.loadRecentConversation();
  console.log('Result:', result);
  
  if (result.success) {
    chatState.sessionId$.next(result.sessionId);
    
    const messages = [];
    for (const msg of result.messages) {
      messages.push({ role: 'user', content: msg.query });
      messages.push({ role: 'assistant', content: msg.response });
    }
    
    chatState.messages$.next(messages);
    console.log('✅ Manually loaded history');
  }
})();
```

---

## Verification Checklist

✅ **Backend Running**
```bash
curl http://localhost:8000/docs
# Should return Swagger UI
```

✅ **Endpoints Registered**
```bash
curl http://localhost:8000/openapi.json | grep "my-conversations"
# Should show the endpoint
```

✅ **Token Exists**
```javascript
localStorage.getItem('auth_token') !== null
```

✅ **Token is Valid**
```javascript
// Decode JWT
const token = localStorage.getItem('auth_token');
const payload = JSON.parse(atob(token.split('.')[1]));
console.log('Token payload:', payload);
// Should show: {user_id, username, tenant_id, ...}
```

✅ **User Has Conversations**
```sql
SELECT COUNT(*) FROM conversations WHERE user_id = 'username';
-- Should be > 0
```

✅ **No Console Errors**
```
No red errors in browser console
```

---

## Still Not Working?

### Get Full Debug Info

Run this in browser console:

```javascript
console.log('=== DEBUG INFO ===');
console.log('Token:', localStorage.getItem('auth_token') ? 'Present' : 'Missing');
console.log('Session ID:', chatState.sessionId$.getValue());
console.log('Messages:', chatState.messages$.getValue().length);

const token = localStorage.getItem('auth_token');
if (token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    console.log('Token user:', payload.username);
    console.log('Token tenant:', payload.tenant_id);
  } catch (e) {
    console.log('Token decode error:', e);
  }
}

// Test API
const conversationService = require('./services/conversation.service').default;
conversationService.getMyConversations(5)
  .then(r => console.log('API Test Result:', r))
  .catch(e => console.error('API Test Error:', e));
```

**Share the output** for further debugging!

---

## Summary

1. **Check browser console** for error messages
2. **Verify token exists** in localStorage
3. **Test API endpoints** manually
4. **Check database** for conversations
5. **Review backend logs** for errors
6. **Force manual load** if needed

Most issues are caused by:
- Backend not running
- Endpoints not registered
- Token not being sent
- User has no chat history (normal)

