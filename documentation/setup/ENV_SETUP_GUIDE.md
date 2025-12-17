# Environment Setup Guide

## Backend Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# ============================================
# OpenAI Configuration (REQUIRED)
# ============================================
OPENAI_API_KEY=sk-your-openai-api-key-here

# ============================================
# Pinecone Configuration (REQUIRED for documents)
# ============================================
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_ENVIRONMENT=your-pinecone-environment
PINECONE_INDEX_NAME=helpdesk-docs

# ============================================
# MySQL Database Configuration (for Smart Chat)
# ============================================
# Database connection for SQL analytics
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_database_name
DB_USER=root
DB_PASSWORD=your_mysql_password

# Optional: Full connection string format
# DB_CONNECTION_STRING=host=localhost;database=mydb;user=root;password=pass;port=3306

# ============================================
# JWT Authentication
# ============================================
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# ============================================
# Redis Configuration (Optional - for caching)
# ============================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# ============================================
# Server Configuration
# ============================================
DEBUG=true
LOG_LEVEL=INFO
ENVIRONMENT=development

# ============================================
# CORS Configuration
# ============================================
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:4200
```

## Quick Setup Steps

### 1. OpenAI Setup
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy and paste into `OPENAI_API_KEY`

### 2. Pinecone Setup (for document search)
1. Go to https://www.pinecone.io/
2. Sign up for a free account
3. Create a new project
4. Create an index named `helpdesk-docs` with dimension 1536
5. Copy API key and environment to `.env`

### 3. MySQL Setup (for database analytics)
1. Install MySQL 8.0+ or use existing instance
2. Create a database:
   ```sql
   CREATE DATABASE helpdesk_db;
   ```
3. Update database credentials in `.env`
4. (Optional) Import sample data for testing

### 4. JWT Secret
Generate a secure random string:
```bash
# On Linux/Mac:
openssl rand -hex 32

# On Windows (PowerShell):
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }) -as [byte[]])
```

## Sample Database for Testing

If you want to test the database analytics feature, create sample tables:

```sql
-- Create sample database
CREATE DATABASE IF NOT EXISTS helpdesk_db;
USE helpdesk_db;

-- Customers table
CREATE TABLE customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10, 2),
    stock INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    product_id INT,
    quantity INT,
    total_amount DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Insert sample data
INSERT INTO customers (name, email, country, phone) VALUES
('John Doe', 'john.doe@example.com', 'USA', '+1-555-0101'),
('Jane Smith', 'jane.smith@example.com', 'UK', '+44-555-0102'),
('Bob Johnson', 'bob.johnson@example.com', 'Canada', '+1-555-0103'),
('Alice Brown', 'alice.brown@example.com', 'USA', '+1-555-0104'),
('Charlie Wilson', 'charlie.wilson@example.com', 'Australia', '+61-555-0105');

INSERT INTO products (name, category, price, stock) VALUES
('Laptop Pro', 'Electronics', 1299.99, 50),
('Wireless Mouse', 'Accessories', 29.99, 200),
('USB-C Cable', 'Accessories', 19.99, 150),
('Monitor 27"', 'Electronics', 399.99, 30),
('Keyboard Mechanical', 'Accessories', 89.99, 75);

INSERT INTO orders (customer_id, product_id, quantity, total_amount, status) VALUES
(1, 1, 1, 1299.99, 'completed'),
(2, 2, 2, 59.98, 'completed'),
(3, 4, 1, 399.99, 'pending'),
(4, 3, 3, 59.97, 'completed'),
(5, 5, 1, 89.99, 'shipped'),
(1, 2, 1, 29.99, 'completed'),
(2, 1, 1, 1299.99, 'processing');
```

## Verification

After setup, verify your configuration:

### Backend Health Check
```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "features": {
    "hybrid_search": true,
    "streaming": true,
    "smart_chat": true
  }
}
```

### Test Database Connection
```python
# In backend directory
python -c "
from llm.schema_service import get_schema_service
import asyncio

async def test():
    service = get_schema_service()
    tables = await service.get_all_tables()
    print(f'✅ Connected! Found {len(tables)} tables')
    for t in tables:
        print(f\"  - {t['table_name']}\")

asyncio.run(test())
"
```

### Test OpenAI Connection
```bash
curl http://localhost:8000/chat/smart/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "test connection",
    "source": "auto",
    "tenant_id": "default"
  }'
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pymysql'"
```bash
cd backend
pip install pymysql
```

### Issue: "OpenAI API key not found"
- Check `.env` file exists in backend directory
- Verify `OPENAI_API_KEY` is set correctly
- Restart the backend server

### Issue: "Database connection failed"
- Verify MySQL is running: `mysql -u root -p`
- Check DB credentials in `.env`
- Ensure database exists: `SHOW DATABASES;`

### Issue: "Pinecone index not found"
- Create index at https://app.pinecone.io
- Dimension must be 1536 (for OpenAI embeddings)
- Verify index name matches `PINECONE_INDEX_NAME`

## Production Considerations

When deploying to production:

1. **Security:**
   - Use strong, random JWT secrets
   - Never commit `.env` to git
   - Use environment-specific secrets
   - Enable SSL/TLS for database connections

2. **Database:**
   - Use connection pooling
   - Set appropriate timeouts
   - Use read replicas for heavy loads
   - Regular backups

3. **API Keys:**
   - Rotate keys regularly
   - Monitor usage and costs
   - Set up billing alerts
   - Use rate limiting

4. **Monitoring:**
   - Set up error tracking (Sentry, etc.)
   - Monitor API usage
   - Track response times
   - Log all database queries


