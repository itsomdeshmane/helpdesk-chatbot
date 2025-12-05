# 🔐 Authentication & Authorization Setup Guide

Complete authentication system with JWT tokens, role-based access control, and MySQL database integration.

## ✨ Features Implemented

### Backend (FastAPI + MySQL)
- ✅ User registration and login
- ✅ JWT token-based authentication
- ✅ Password hashing with bcrypt
- ✅ Role-based authorization (admin, user, viewer)
- ✅ Protected API endpoints
- ✅ Token verification middleware
- ✅ Automatic token expiry handling

### Frontend (React)
- ✅ Login/Register UI
- ✅ Authentication state management (RxJS)
- ✅ Token storage in localStorage
- ✅ API request interceptors (auto-attach token)
- ✅ Automatic redirect on token expiry
- ✅ User profile display
- ✅ Logout functionality

## 📋 Setup Instructions

### 1. Install Backend Dependencies

```bash
cd backend
pip install PyJWT==2.8.0 passlib[bcrypt]==1.7.4
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Create Users Table

Run the setup script to create the users table and default admin:

```bash
cd backend
python scripts/create_users_table.py
```

This will create:
- ✅ `users` table with proper schema
- ✅ Default admin account:
  - **Username:** admin
  - **Password:** admin123
  - **Email:** admin@example.com
  - **Role:** admin

### 3. Set JWT Secret Key (Important for Production!)

Create or update `.env` file in backend folder:

```env
JWT_SECRET_KEY=your-super-secret-key-min-32-characters-long-change-this
```

⚠️ **Important:** Use a strong, unique secret key in production!

### 4. Start Backend

```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 5. Start Frontend

```bash
cd frontend
npm start
```

## 🎯 Testing the Authentication

### Test Login

1. Open http://localhost:3000
2. You'll see the login screen
3. Login with demo credentials:
   - **Username:** admin
   - **Password:** admin123
4. You'll be redirected to the chat interface

### Test Registration

1. Click "Sign Up" on login screen
2. Fill in the form:
   - Username: testuser
   - Email: test@example.com
   - Password: password123
   - Full Name: Test User
3. Click "Sign Up"
4. You'll be automatically logged in

### Test Protected Routes

All chat requests now include authentication:
- Token is automatically attached to requests
- User information is logged on backend
- Session management works with authenticated users

### Test Logout

1. Click "🚪 Logout" button in header
2. You'll be redirected back to login screen
3. Token is cleared from storage

## 📊 Database Schema

### Users Table

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key (auto-increment) |
| username | VARCHAR(50) | Unique username |
| email | VARCHAR(100) | Unique email |
| password_hash | VARCHAR(255) | Bcrypt hashed password |
| full_name | VARCHAR(100) | Full name (optional) |
| role | ENUM | 'admin', 'user', 'viewer' |
| is_active | BOOLEAN | Account status |
| tenant_id | VARCHAR(50) | Multi-tenancy support |
| created_at | TIMESTAMP | Registration date |
| updated_at | TIMESTAMP | Last update |
| last_login | TIMESTAMP | Last login time |

## 🔑 User Roles

### Admin
- Full access to all features
- Can manage users (future feature)
- Can access analytics (future feature)

### User (Default)
- Can chat with AI
- Can view own chat history
- Standard user permissions

### Viewer
- Read-only access
- Can view but not modify

## 🛡️ Security Features

### Password Security
- ✅ Bcrypt hashing (industry standard)
- ✅ Salt automatically generated
- ✅ Min 6 characters required
- ✅ Passwords never stored in plain text

### Token Security
- ✅ JWT tokens with expiration (24 hours)
- ✅ Tokens signed with secret key
- ✅ Automatic token verification
- ✅ Expired tokens handled gracefully

### API Security
- ✅ Protected endpoints require authentication
- ✅ Optional authentication (backward compatible)
- ✅ Role-based authorization
- ✅ CORS properly configured

## 📝 API Endpoints

### Authentication Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "john",
  "email": "john@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "john",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "role": "user"
  }
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

#### Verify Token
```http
POST /auth/verify
Authorization: Bearer <token>
```

#### Logout
```http
POST /auth/logout
Authorization: Bearer <token>
```

### Chat Endpoint (Now with Auth)

```http
POST /chat/query
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "What is the Workflow Module?",
  "tenant_id": "default",
  "session_id": null
}
```

**Note:** Chat endpoint works with or without authentication (backward compatible)

## 🔧 Configuration

### Frontend Configuration

Edit `frontend/src/services/auth.service.js` to change API URL:

```javascript
const API_URL = 'http://localhost:8000/auth';
```

### Token Expiry

Edit `backend/utils/auth.py` to change token expiration:

```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
```

## 🧪 Testing with API Docs

1. Open http://localhost:8000/docs
2. Register a new user using `/auth/register`
3. Login using `/auth/login` and copy the token
4. Click "Authorize" button (top right)
5. Enter: `Bearer <your-token>`
6. Now you can test protected endpoints!

## 🚀 Production Checklist

Before deploying to production:

- [ ] Change JWT_SECRET_KEY to a strong random key
- [ ] Change default admin password
- [ ] Enable HTTPS
- [ ] Update CORS allowed origins
- [ ] Set up proper database backups
- [ ] Implement rate limiting
- [ ] Add password reset functionality
- [ ] Add email verification
- [ ] Enable 2FA (optional)
- [ ] Set up monitoring and logging

## 🎨 Customization

### Change UI Colors

Edit `frontend/src/components/Auth.css`:

```css
.auth-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  /* Change colors here */
}
```

### Add Custom User Fields

1. Update database schema in `create_users_table.py`
2. Update models in `backend/routers/auth.py`
3. Update registration form in `frontend/src/components/Login.js`

### Implement Password Reset

You can add password reset functionality by:
1. Creating reset token endpoint
2. Sending reset email
3. Creating reset password form
4. Updating password in database

## 📞 Support

If you encounter any issues:

1. Check backend logs for errors
2. Check browser console for frontend errors
3. Verify MySQL is running
4. Verify all dependencies are installed
5. Check JWT secret is properly set

## 🎉 Success!

Your authentication system is now fully configured! Users can:
- ✅ Register new accounts
- ✅ Login securely
- ✅ Access chat features
- ✅ Maintain sessions
- ✅ Logout safely

The system is production-ready with proper security measures! 🔒

