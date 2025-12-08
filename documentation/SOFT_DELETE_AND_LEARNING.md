# Soft Delete & Global Learning System

## Overview

This system implements a privacy-friendly approach to conversation management that balances user privacy with system improvement:

1. **User-Specific Conversations**: Each user sees only their own chat history
2. **Soft Delete**: Users can "delete" conversations that disappear from their view
3. **Global Learning**: Deleted data is kept for analytics to improve system quality
4. **GDPR Compliance**: Automatic permanent deletion after retention period

---

## How It Works

### 1. User-Specific Conversations

Each conversation is linked to a specific user via `user_id`:

```sql
CREATE TABLE conversations (
    session_id VARCHAR(100) UNIQUE,
    user_id VARCHAR(255),  -- Links conversation to specific user
    deleted_by_user BOOLEAN DEFAULT FALSE,  -- Soft delete flag
    ...
);
```

**User sees:** Only their own conversations (filtered by `user_id`)

**APIs:**
- `GET /conversations/my-conversations` - User's conversations (excludes deleted)
- `GET /conversation/{session_id}` - Specific conversation details

### 2. Soft Delete System

When a user "deletes" a conversation:

```python
# User clicks delete button
soft_delete_conversation(session_id, retention_days=90)

# Database update:
UPDATE conversations 
SET deleted_by_user = TRUE,
    deleted_at = NOW(),
    permanent_delete_after = NOW() + 90 days
```

**From User's Perspective:**
- ✅ Conversation disappears from their history
- ✅ Clean interface, no clutter
- ✅ Can restore within retention period

**From System's Perspective:**
- ✅ Data still exists in database
- ✅ Used for analytics and learning
- ✅ Improves response quality for all users

### 3. Global Learning (Privacy-Friendly)

Analytics aggregate data from **ALL users** (including deleted conversations):

```python
# Most common questions across all users
get_global_common_questions(tenant_id)
# Returns: Aggregated statistics, no individual user data exposed

# Query patterns analysis
get_global_query_patterns(tenant_id, days=30)
# Returns: System-wide metrics for improvement
```

**Privacy Protection:**
- ❌ No individual user identification
- ❌ No personal data exposed
- ✅ Only aggregated statistics
- ✅ Helps improve system for everyone

### 4. GDPR Compliance

Automatic permanent deletion after retention period:

```python
# Background job (run daily)
permanently_delete_old_conversations(tenant_id)

# Deletes conversations where:
# - deleted_by_user = TRUE
# - permanent_delete_after < NOW()
```

**Compliance Features:**
- ⏰ Configurable retention period (default: 90 days)
- 🗑️ Automatic hard delete after retention
- 👤 User can request immediate permanent deletion
- 📊 Admin dashboard for data hygiene

---

## API Endpoints

### User-Specific (Per-User View)

#### Get My Conversations
```http
GET /conversations/my-conversations?limit=20
Authorization: Bearer <token>
```
**Returns:** User's conversations (excludes soft-deleted)

#### Delete Conversation (Soft)
```http
DELETE /conversation/{session_id}?retention_days=90
Authorization: Bearer <token>
```
**Effect:** Hidden from user, kept for learning

#### Restore Deleted Conversation
```http
POST /conversation/{session_id}/restore
Authorization: Bearer <token>
```
**Effect:** Unhides conversation, cancels permanent deletion

#### View Deleted Conversations
```http
GET /conversations/deleted-conversations?limit=20
Authorization: Bearer <token>
```
**Returns:** Recoverable deleted conversations

---

### Global Analytics (All Users, Admin Only)

#### Common Questions
```http
GET /analytics/global/common-questions?limit=10
Authorization: Bearer <admin-token>
```
**Returns:** Most asked questions (includes deleted conversations)

#### Query Patterns
```http
GET /analytics/global/query-patterns?days=30
Authorization: Bearer <admin-token>
```
**Returns:** System-wide usage patterns

#### Feedback Insights
```http
GET /analytics/global/feedback-insights?min_samples=5
Authorization: Bearer <admin-token>
```
**Returns:** Questions needing improvement based on feedback

#### Cleanup Old Data
```http
POST /analytics/global/cleanup-old-data
Authorization: Bearer <admin-token>
```
**Effect:** Permanently deletes conversations past retention period

---

## Implementation Guide

### 1. Run Migration

```bash
cd backend
python scripts/run_soft_delete_migration.py
```

This adds:
- `deleted_by_user` column
- `deleted_at` column
- `permanent_delete_after` column
- Index for efficient queries

### 2. Update Frontend

**Delete Button:**
```javascript
async function deleteConversation(sessionId) {
    const response = await fetch(`/conversation/${sessionId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
    });
    
    // Conversation disappears from user's view
    // But kept for system learning
}
```

**Restore Feature:**
```javascript
async function restoreConversation(sessionId) {
    await fetch(`/conversation/${sessionId}/restore`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
    });
    // Conversation reappears
}
```

### 3. Setup Background Job

**Daily cleanup job (cron):**
```bash
# Add to crontab
0 2 * * * cd /path/to/backend && python scripts/cleanup_old_conversations.py
```

**Script:**
```python
from utils.conversation_manager import get_conversation_manager

def daily_cleanup():
    conv_manager = get_conversation_manager()
    deleted = conv_manager.permanently_delete_old_conversations()
    print(f"Deleted {deleted} conversations past retention period")

if __name__ == "__main__":
    daily_cleanup()
```

---

## Benefits

### For Users
- ✅ Clean interface (delete unwanted conversations)
- ✅ Privacy control (can delete anytime)
- ✅ Can restore accidentally deleted conversations
- ✅ Better responses over time (system learns)

### For System
- ✅ Learns from all conversations (including deleted)
- ✅ Identifies common questions
- ✅ Improves response quality
- ✅ Detects documentation gaps

### For Admins
- ✅ Understand system usage patterns
- ✅ Identify areas for improvement
- ✅ GDPR compliant data management
- ✅ Analytics dashboard

---

## Privacy Considerations

### What's Collected
- ✅ User queries (text)
- ✅ System responses
- ✅ Response times
- ✅ Feedback scores

### What's Protected
- ❌ No tracking across sessions after deletion
- ❌ No individual user profiling
- ❌ No personal data in analytics
- ❌ Data deleted after retention period

### Transparency
- ✅ Users informed about retention period when deleting
- ✅ Clear privacy policy
- ✅ Option for immediate permanent deletion (contact admin)
- ✅ Compliance with GDPR "right to be forgotten"

---

## Configuration

### Retention Period

**Default: 90 days** (GDPR compliant)

Change via API:
```python
# Delete with custom retention
DELETE /conversation/{session_id}?retention_days=30
```

Change system default:
```python
# In conversation_manager.py
def soft_delete_conversation(self, session_id: str, retention_days: int = 30):
```

### Permanent Delete Immediately

For users requesting immediate deletion:
```python
# Admin can force permanent delete
conversation_manager.permanently_delete_conversation(session_id)
```

---

## Testing

### Test Soft Delete
```python
# 1. Create conversation
session_id = create_session("tenant1", "user1")

# 2. Add messages
save_message(session_id, "Test", "Response")

# 3. User deletes
soft_delete_conversation(session_id)

# 4. Check user view (should be empty)
conversations = get_user_conversations("tenant1", "user1")
assert len(conversations) == 0

# 5. Check global analytics (should include it)
questions = get_global_common_questions("tenant1")
assert "Test" in [q['question'] for q in questions]

# 6. Restore
restore_conversation(session_id)

# 7. Check user view (should appear again)
conversations = get_user_conversations("tenant1", "user1")
assert len(conversations) == 1
```

---

## Monitoring

### Dashboard Metrics

**User Metrics:**
- Active conversations per user
- Deleted conversations per user
- Restore rate

**System Metrics:**
- Total queries (all users)
- Common questions
- Response quality trends
- Topics needing improvement

**Compliance Metrics:**
- Conversations pending permanent deletion
- Data retention compliance
- Cleanup job success rate

---

## Support

### User Questions

**Q: Will my deleted conversations be visible to others?**
A: No. Deleted conversations are hidden from all user views. They're only used in aggregated analytics.

**Q: Can I permanently delete immediately?**
A: Contact admin for immediate permanent deletion.

**Q: Can I see what data is used for learning?**
A: Yes, admins can provide aggregated statistics (no individual data).

### Admin Questions

**Q: How often should cleanup run?**
A: Daily is recommended. Configure in cron job.

**Q: Can I adjust retention period?**
A: Yes, configurable per tenant or per deletion.

**Q: Is this GDPR compliant?**
A: Yes, with automatic deletion after retention period and right to be forgotten.

