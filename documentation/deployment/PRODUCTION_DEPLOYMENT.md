# 🚀 Production Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ Configuration
- [ ] Set all environment variables in `.env`
- [ ] Configure production database (MySQL)
- [ ] Set up Pinecone index
- [ ] Configure CORS for production domain
- [ ] Set proper log levels
- [ ] Enable rate limiting

### ✅ Security
- [ ] API keys in `.env`, not in code
- [ ] Strong MySQL password
- [ ] CORS restricted to production domains
- [ ] HTTPS configured
- [ ] File upload size limits set
- [ ] Input validation enabled

### ✅ Performance
- [ ] Set uvicorn workers (4-8 recommended)
- [ ] Configure database connection pooling
- [ ] Set up Nginx reverse proxy (recommended)
- [ ] Enable response compression
- [ ] Configure timeout limits

### ✅ Monitoring
- [ ] Error logging configured
- [ ] Set up health check monitoring
- [ ] Configure uptime alerts
- [ ] Database backup strategy in place

---

## 🛠️ Installation Steps

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install python3 python3-pip python3-venv -y

# Install MySQL
sudo apt install mysql-server -y
sudo mysql_secure_installation

# Install Nginx (optional but recommended)
sudo apt install nginx -y
```

### Step 2: Application Setup

```bash
# Create application directory
sudo mkdir -p /opt/helpdesk-chatbot
cd /opt/helpdesk-chatbot

# Clone or copy your application
git clone <your-repo> .
# OR
scp -r ./backend user@server:/opt/helpdesk-chatbot/

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install production dependencies
pip install -r backend/requirements-production.txt
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit with your production values
nano backend/.env
```

**Required values:**
```bash
OPENAI_API_KEY=sk-prod-xxx
PINECONE_API_KEY=xxx
MYSQL_HOST=localhost
MYSQL_PASSWORD=strong_password
ENV=production
CORS_ORIGINS=https://yourdomain.com
```

### Step 4: Database Setup

```bash
# Create MySQL database
mysql -u root -p << EOF
CREATE DATABASE helpdesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'helpdesk_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON helpdesk_db.* TO 'helpdesk_user'@'localhost';
FLUSH PRIVILEGES;
EOF

# Run database migrations
cd backend
python scripts/create_mysql_database.py
```

### Step 5: Load Documentation

```bash
# Place your documents in docs/ folder
mkdir -p /opt/helpdesk-chatbot/backend/docs
# Copy your PDF, DOCX, etc. files here

# Start server (it will auto-load docs on startup)
# OR manually load:
python scripts/reload_docs_to_pinecone.py
```

---

## 🚀 Deployment Options

### Option 1: Systemd Service (Recommended)

Create `/etc/systemd/system/helpdesk-chatbot.service`:

```ini
[Unit]
Description=Helpdesk Chatbot API
After=network.target mysql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/helpdesk-chatbot/backend
Environment="PATH=/opt/helpdesk-chatbot/venv/bin"
ExecStart=/opt/helpdesk-chatbot/venv/bin/gunicorn app:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --access-logfile /var/log/helpdesk/access.log \
    --error-logfile /var/log/helpdesk/error.log \
    --log-level info

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
# Create log directory
sudo mkdir -p /var/log/helpdesk
sudo chown www-data:www-data /var/log/helpdesk

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable helpdesk-chatbot
sudo systemctl start helpdesk-chatbot

# Check status
sudo systemctl status helpdesk-chatbot

# View logs
sudo journalctl -u helpdesk-chatbot -f
```

### Option 2: Docker (Alternative)

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements-production.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-production.txt

# Copy application
COPY backend/ .

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "app:app", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - MYSQL_HOST=db
      - MYSQL_USER=helpdesk_user
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
      - MYSQL_DATABASE=helpdesk_db
    depends_on:
      - db
    volumes:
      - ./backend/docs:/app/docs
      - ./backend/logs:/app/logs
    restart: unless-stopped

  db:
    image: mysql:8.0
    environment:
      - MYSQL_DATABASE=helpdesk_db
      - MYSQL_USER=helpdesk_user
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  mysql_data:
```

**Deploy:**
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

---

## 🌐 Nginx Configuration (Recommended)

Create `/etc/nginx/sites-available/helpdesk-chatbot`:

```nginx
upstream helpdesk_backend {
    server 127.0.0.1:8000;
}

# HTTP -> HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;
    
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates (use certbot for Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000" always;

    # Client body size limit (for file uploads)
    client_max_body_size 50M;

    # Timeouts
    proxy_connect_timeout 120s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;

    # Compression
    gzip on;
    gzip_types text/plain application/json application/javascript text/css;

    # API proxy
    location / {
        proxy_pass http://helpdesk_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint (bypasses rate limiting)
    location /health {
        proxy_pass http://helpdesk_backend/health;
        access_log off;
    }

    # Static files (if any)
    location /static/ {
        alias /opt/helpdesk-chatbot/backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable and restart:**
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/helpdesk-chatbot /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Get SSL certificate (Let's Encrypt)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 📊 Monitoring Setup

### 1. Health Check Monitoring

Use a service like UptimeRobot or Pingdom:

- URL: `https://yourdomain.com/health`
- Interval: 5 minutes
- Alert on: Status != 200

### 2. Application Monitoring (Sentry)

```bash
# Install Sentry SDK
pip install sentry-sdk[fastapi]
```

Add to `app.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

# Initialize Sentry
if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,  # 10% of transactions
        environment=os.getenv("ENV", "production")
    )
```

### 3. Log Monitoring

```bash
# View real-time logs
sudo journalctl -u helpdesk-chatbot -f

# View error logs only
sudo journalctl -u helpdesk-chatbot -p err -f

# View logs from last hour
sudo journalctl -u helpdesk-chatbot --since "1 hour ago"
```

---

## 🔒 Security Hardening

### 1. Firewall Configuration

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Fail2Ban (Protection against brute force)

```bash
# Install
sudo apt install fail2ban -y

# Create jail for helpdesk
sudo nano /etc/fail2ban/jail.d/helpdesk.conf
```

```ini
[helpdesk-api]
enabled = true
port = http,https
filter = helpdesk-api
logpath = /var/log/helpdesk/access.log
maxretry = 10
bantime = 3600
findtime = 600
```

### 3. Regular Updates

```bash
# Create update script
cat > /opt/helpdesk-chatbot/update.sh << 'EOF'
#!/bin/bash
cd /opt/helpdesk-chatbot
source venv/bin/activate
git pull
pip install -r backend/requirements-production.txt --upgrade
sudo systemctl restart helpdesk-chatbot
EOF

chmod +x /opt/helpdesk-chatbot/update.sh
```

---

## 💾 Backup Strategy

### 1. Database Backup

```bash
# Create backup script
cat > /opt/helpdesk-chatbot/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/helpdesk-db"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

mysqldump -u helpdesk_user -p$MYSQL_PASSWORD helpdesk_db | \
    gzip > $BACKUP_DIR/helpdesk_db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
EOF

chmod +x /opt/helpdesk-chatbot/backup-db.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/helpdesk-chatbot/backup-db.sh") | crontab -
```

### 2. Document Backup

```bash
# Backup docs folder
rsync -av --delete /opt/helpdesk-chatbot/backend/docs/ /backups/helpdesk-docs/
```

---

## 🧪 Testing Production Deployment

```bash
# 1. Test health check
curl https://yourdomain.com/health

# 2. Test API
curl -X POST https://yourdomain.com/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query":"test", "tenant_id":"default"}'

# 3. Load test (optional)
# Install: pip install locust
locust -f tests/load_test.py --host=https://yourdomain.com
```

---

## 📈 Performance Tuning

### Gunicorn Workers

```bash
# Recommended: (2 x CPU cores) + 1
# For 4 CPU cores: 4 * 2 + 1 = 9 workers
--workers 9
```

### Database Connection Pooling

In `db_manager.py`:
```python
self.connection_pool = pooling.MySQLConnectionPool(
    pool_name="helpdesk_pool",
    pool_size=10,  # Increase for production
    pool_reset_session=True,
    ...
)
```

### Pinecone Optimization

```python
# Batch queries when possible
results = pinecone_index.query(
    vector=query_embedding,
    top_k=5,  # Adjust based on needs
    include_metadata=True
)
```

---

## 🚨 Troubleshooting

### Issue: Service won't start

```bash
# Check logs
sudo journalctl -u helpdesk-chatbot -n 50 --no-pager

# Check config
sudo systemctl cat helpdesk-chatbot

# Test manually
cd /opt/helpdesk-chatbot/backend
source ../venv/bin/activate
python app.py
```

### Issue: High memory usage

```bash
# Monitor resources
htop

# Check worker count (reduce if needed)
sudo systemctl edit helpdesk-chatbot
# Change --workers value

# Restart service
sudo systemctl restart helpdesk-chatbot
```

### Issue: Slow responses

```bash
# Check database
mysql -u helpdesk_user -p
SHOW PROCESSLIST;

# Check Pinecone latency
python scripts/check_config.py

# Enable query caching (add to .env)
ENABLE_QUERY_CACHE=true
```

---

## 📞 Support

**Quick Commands:**
```bash
# Start service
sudo systemctl start helpdesk-chatbot

# Stop service
sudo systemctl stop helpdesk-chatbot

# Restart service
sudo systemctl restart helpdesk-chatbot

# View logs
sudo journalctl -u helpdesk-chatbot -f

# Check status
sudo systemctl status helpdesk-chatbot

# Test configuration
python backend/scripts/check_config.py
```

---

## ✅ Post-Deployment Checklist

After deployment, verify:

- [ ] Health check returns 200 OK
- [ ] API responds to test queries
- [ ] Database is accessible
- [ ] Pinecone is connected
- [ ] Logs are writing correctly
- [ ] SSL certificate is valid
- [ ] Monitoring is active
- [ ] Backups are running
- [ ] Error tracking is working
- [ ] Performance is acceptable

---

**Your helpdesk chatbot is now production-ready! 🚀**




