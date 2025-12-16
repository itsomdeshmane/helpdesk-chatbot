# 🚀 Quick Start Guide - Analytics Chatbot

## Prerequisites
- ✅ .NET 8.0 SDK installed
- ✅ MySQL 8.0+ running
- ✅ OpenAI API key (already configured in appsettings.json)

---

## Step-by-Step Setup

### 1️⃣ Database Setup

**Create your MySQL database:**
```sql
CREATE DATABASE yourdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**Update connection string in `appsettings.json`:**
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "server=localhost;database=yourdb;user=root;password=yourpassword;"
  }
}
```

### 2️⃣ Run Database Migrations (for Authentication)

```bash
# Create and apply Identity tables
dotnet ef migrations add InitialIdentity
dotnet ef database update
```

This creates the necessary ASP.NET Identity tables for user authentication.

### 3️⃣ Start the Application

```bash
dotnet run
```

The API will start at:
- **HTTP**: http://localhost:5000
- **HTTPS**: https://localhost:5001
- **Swagger UI**: http://localhost:5000/swagger

### 4️⃣ Generate Schema Embeddings

**Option A: Using Swagger**
1. Open http://localhost:5000/swagger
2. Find `POST /api/schema/generate-embeddings`
3. Click "Try it out" → "Execute"

**Option B: Using curl**
```bash
curl -X POST "http://localhost:5000/api/schema/generate-embeddings"
```

**This will:**
- Extract all tables and columns from your database
- Generate OpenAI embeddings for each schema element
- Save embeddings to `schema_embeddings.json`
- Load them into memory for vector search

⏱️ **Time:** 30-60 seconds depending on schema size

### 5️⃣ Test Your First Query

**Using Swagger:**
1. Go to Swagger UI
2. Find `POST /api/chat/query`
3. Try this query:
   ```json
   {
     "query": "Show me all records from the first table"
   }
   ```

**Using curl:**
```bash
curl -X POST "http://localhost:5000/api/chat/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me all records from the first table"}'
```

**What happens:**
1. Your query is embedded
2. System finds relevant tables/columns
3. GPT-4 generates SQL
4. SQL executes against your database
5. Results returned as JSON

---

## 🎯 Example Queries to Try

Once your embeddings are ready, try these:

### Basic Queries
```
"Show me all users"
"Count total orders"
"What are the top 5 products by sales?"
```

### Analytical Queries
```
"What's the total revenue by month?"
"Show me customers who haven't ordered in 30 days"
"Average order value by customer segment"
```

### Complex Queries
```
"Compare this year's sales to last year by category"
"Show me the top 10 customers by lifetime value"
"Which products have the highest return rate?"
```

---

## 🔐 User Authentication (Optional)

### Register a New User
```bash
curl -X POST "http://localhost:5000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "SecurePass123!"}'
```

### Login
```bash
curl -X POST "http://localhost:5000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "SecurePass123!"}'
```

---

## 📊 View Your Schema

```bash
curl -X GET "http://localhost:5000/api/schema/info"
```

Returns:
- All tables in your database
- Column names and descriptions
- Table/column counts

---

## 🐛 Troubleshooting

### "Schema embeddings not found"
**Solution:** Run `POST /api/schema/generate-embeddings` first

### "OpenAI API error"
**Solution:** 
- Check your API key in `appsettings.json`
- Verify you have API quota remaining
- Check internet connection

### "Database connection failed"
**Solution:**
- Verify MySQL is running: `mysql -u root -p`
- Check connection string is correct
- Ensure database exists

### "No relevant schema found"
**Solution:**
- Your database might be empty
- Run schema generation again
- Check that embeddings file exists

---

## 📁 Important Files

After setup, you'll see these files:

- **`schema_embeddings.json`** - Cached embeddings for fast lookup
- **`training_logs.jsonl`** - All interactions logged for training
- **`bin/`** - Compiled application

---

## 🎓 Next Steps

### Improve SQL Accuracy
1. Add column descriptions to your database schema
2. Increase `topN` parameter in `LlmService.cs` (line 53)
3. Customize prompts in `LlmPromptBuilder.cs`

### Monitor Performance
```bash
# Watch training logs in real-time
tail -f training_logs.jsonl
```

### Fine-Tune Your Model
After collecting 500+ queries:
1. Review `training_logs.jsonl`
2. Clean and format the data
3. Use OpenAI fine-tuning API
4. Deploy your custom model

---

## 🔗 API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat/query` | POST | Submit natural language query |
| `/api/schema/generate-embeddings` | POST | Generate/refresh embeddings |
| `/api/schema/info` | GET | View database schema |
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | Login user |
| `/api/report/excel` | POST | Generate Excel report |
| `/api/report/pdf` | POST | Generate PDF report |

---

## 💡 Pro Tips

1. **Refresh embeddings** after schema changes:
   ```bash
   curl -X POST "http://localhost:5000/api/schema/generate-embeddings"
   ```

2. **Monitor costs**: Check OpenAI usage dashboard regularly

3. **Add descriptions**: Update your MySQL schema with column comments for better results
   ```sql
   ALTER TABLE users MODIFY COLUMN email VARCHAR(255) COMMENT 'User email address';
   ```

4. **Tune performance**: Adjust `topN` in LlmService.cs based on your schema complexity

5. **Secure in production**: 
   - Use environment variables for secrets
   - Enable authentication on all endpoints
   - Set up proper CORS policies

---

## ✅ Verification Checklist

- [ ] Application starts without errors
- [ ] Swagger UI loads at /swagger
- [ ] Schema embeddings generated successfully
- [ ] First query returns SQL and results
- [ ] Training logs are being created
- [ ] Can view schema info

---

## 🆘 Need Help?

Check these documents:
- **`EMBEDDINGS_SETUP.md`** - Detailed embedding setup
- **`IMPLEMENTATION_SUMMARY.md`** - Complete technical overview
- **Application logs** - Check console output for errors

---

## 🎉 You're Ready!

Your next-generation AI-powered SQL chatbot is now running!

Try complex queries, monitor the training logs, and watch as your system learns from each interaction. After collecting sufficient data, you'll be ready to fine-tune your own custom model for even better performance.

**Happy querying! 🚀**

