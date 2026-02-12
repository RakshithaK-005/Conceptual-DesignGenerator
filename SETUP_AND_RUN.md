# Frontend & Backend Integration Guide

## 🚀 Quick Start

This guide explains how to run your complete AI Architectural Design Generator system with both frontend and backend working together.

---

## 📋 Prerequisites

- **Python 3.10+** (for backend)
- **Node.js/npm** (optional, for serving frontend)
- **PostgreSQL 12+** (or use Docker)
- **Docker & Docker Compose** (recommended for database)
- **Modern web browser** (Chrome, Firefox, Edge, Safari)

---

## 🛠️ Setup Instructions

### Step 1: Clone/Organize Your Files

Your project structure should look like:
```
cap/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── routes/
│   │     ├── auth.py
│   │     ├── users.py
│   │     ├── contact.py ✨ NEW
│   │     └── ... other routes
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── contact.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── script.js ✨ UPDATED with API integration
└── README.md
```

---

## 🔧 Option A: Local Development (Recommended for Testing)

### Backend Setup

#### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### 2. Configure Environment Variables

Create/update `.env` file in `backend/`:

```env
# API Configuration
API_TITLE=AI Architectural Design Generator
API_VERSION=1.0.0
DEBUG=True

# Database (Local PostgreSQL)
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=arch_design_db

# OR use Docker PostgreSQL (see below)
# DB_HOST=db
# DB_PASSWORD=your_postgres_password

# Security
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars

# AI Models
DEVICE=cpu  # Use 'cpu' for testing, 'cuda' if you have GPU
DTYPE=float32  # Use float32 on CPU, float16 on GPU for speed

# File Uploads
UPLOAD_DIR=uploads
LOGS_DIR=logs

# CORS (includes all local development ports)
# Configured in config.py to allow localhost development
```

#### 3. Start Backend Server

**Option A1: Using Python (Requires PostgreSQL)**

```bash
# Make sure PostgreSQL is running
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option A2: Using Docker Compose (Recommended)**

```bash
# From backend directory
docker-compose up -d
```

This starts:
- `PostgreSQL` on port 5432
- `Backend API` on port 8000
- `pgAdmin` on port 5050 (optional, for database management)

**Check backend is running:**
```bash
curl http://localhost:8000/
# Expected response: {"message": "AI Architectural Design Generator API", ...}
```

---

### Frontend Setup

#### 1. Serve Frontend Files

You have several options:

**Option B1: Using Python's built-in server (Simplest)**

```bash
cd frontend
python -m http.server 8080
```

Then open: `http://localhost:8080/`

**Option B2: Using Node.js Live Server**

```bash
# Install globally (if not already installed)
npm install -g live-server

cd frontend
live-server --port=8080
```

Then open: `http://localhost:8080/`

**Option B3: Using VS Code Live Server Extension**

- Install "Live Server" extension in VS Code
- Right-click on `index.html` → "Open with Live Server"
- Default port: 5500

**Option B4: Using Docker**

```bash
# From frontend directory
docker run -d -p 80:80 -v $(pwd):/usr/share/nginx/html nginx
```

Then open: `http://localhost/`

---

### Step 2: Configure API Connection

Once the frontend loads, you'll see a settings icon (⚙️) in the top-right navbar.

1. Click the **⚙️ Settings** button
2. Enter your backend URL:
   - **Default (Local)**: `http://localhost:8000`
   - **Remote**: `http://your-server-ip:8000`
3. Click **Save**

The URL is saved to browser's localStorage, so you only need to configure it once.

---

## 🐳 Option B: Docker Compose (Complete Stack)

This is the easiest way to run everything at once.

### 1. Create docker-compose.yml for Full Stack

If you don't have a root-level docker-compose.yml:

```yaml
version: '3.9'

services:
  # PostgreSQL Database
  db:
    image: postgres:16
    container_name: arch_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: arch_design_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: arch_backend
    ports:
      - "8000:8000"
    environment:
      DB_HOST: db
      DB_USER: postgres
      DB_PASSWORD: postgres
      DB_NAME: arch_design_db
      DEBUG: "True"
      DEVICE: cpu
      DTYPE: float32
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/logs:/app/logs

  # Nginx Frontend (Optional)
  frontend:
    image: nginx:alpine
    container_name: arch_frontend
    ports:
      - "80:80"
    volumes:
      - ./frontend:/usr/share/nginx/html:ro
    depends_on:
      - backend

  # pgAdmin (Optional, for database management)
  pgadmin:
    image: dpage/pgadmin4
    container_name: arch_pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@archai.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      - db

volumes:
  postgres_data:
```

### 2. Run the Stack

```bash
cd cap  # Root directory
docker-compose up -d

# Or for testing output:
docker-compose up
```

### 3. Access the System

| Service | URL | Login |
|---------|-----|-------|
| Frontend | `http://localhost` | Go to Login |
| Backend API | `http://localhost:8000` | Swagger: `/docs` |
| Backend ReDoc | `http://localhost:8000/redoc` | - |
| PgAdmin | `http://localhost:5050` | admin@archai.com / admin |

---

## ✅ Testing the Integration

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### 2. View API Documentation

Open: `http://localhost:8000/docs`

### 3. Test Frontend Login

1. Open `http://localhost:8080/` (or your frontend URL)
2. Click **⚙️** in navbar to verify API URL is set to `http://localhost:8000`
3. Click **Login**
4. **Register** a new account:
   - Email: `test@example.com`
   - Password: `SecurePass123`
5. Login with those credentials
6. You should see "Hi, test!" in the navbar

### 4. Test Contact Form

1. Go to **Contact** page
2. Fill in the form:
   - Name: John Doe
   - Email: john@example.com
   - Subject: Test
   - Message: Hello!
3. Click **Send Message**
4. Should see success notification

---

## 🚨 Troubleshooting

### Frontend Can't Connect to Backend

**Problem**: Login fails, "Failed to connect" error

**Solutions**:
1. Check if backend is running: `curl http://localhost:8000/health`
2. Check frontend API URL via settings (⚙️) - should be `http://localhost:8000`
3. Check browser console (F12 → Console) for CORS errors
4. Ensure CORS is enabled in backend config

### CORS Errors in Console

**Error**: "Access to XMLHttpRequest at 'http://localhost:8000/...' from origin 'http://localhost:8080' has been blocked by CORS policy"

**Solutions**:
1. Update `config.py` CORS_ORIGINS to include your frontend port:
   ```python
   CORS_ORIGINS: list = [
       "http://localhost:8080",
       "http://localhost:3000",
       # ... add your port here
   ]
   ```
2. Or set `DEBUG=True` in `.env` to allow all origins
3. Restart backend after changes

### Database Connection Error

**Error**: "could not connect to server: Connection refused"

**Solutions**:
1. Make sure PostgreSQL is running: `psql --version`
2. Check database credentials in `.env`
3. Use Docker: `docker-compose up db` to run PostgreSQL in container
4. Create database manually:
   ```bash
   createdb -U postgres arch_design_db
   ```

### Login Not Working

**Error**: "Login failed. Please try again."

**Solutions**:
1. Check backend logs: `docker-compose logs backend`
2. Ensure user exists in database
3. Verify password is correct (min 8 characters)
4. Check `/token` endpoint in Swagger docs

### 403 or 401 Errors

**Problem**: Getting authorization errors

**Solutions**:
1. Make sure you're logged in (token in localStorage)
2. Check token hasn't expired (30 minutes by default)
3. Clear localStorage and login again: Open DevTools → Application → Clear Storage
4. Check `SECRET_KEY` matches between frontend and backend

---

## 📊 Database Management

### Access PgAdmin

**URL**: `http://localhost:5050`
**Email**: `admin@archai.com`
**Password**: `admin`

### Add PostgreSQL Server in PgAdmin

1. Click **Add New Server**
2. **General** tab:
   - Name: `ArchAI DB`
3. **Connection** tab:
   - Host: `db` (or `localhost` if on same machine)
   - Port: `5432`
   - Username: `postgres`
   - Password: `postgres`
   - Database: `arch_design_db`
4. Click **Save**

### View Users Table

1. Expand `ArchAI DB` → `Schemas` → `public` → `Tables`
2. Right-click `users` → **View/Edit Data** → **All Rows**

---

## 📝 Common API Endpoints

All endpoints require authentication except `/auth/login`, `/auth/register`, and `/contact`.

```bash
# Authentication
POST   /auth/register        # Create new account
POST   /token               # Login (returns JWT token)
GET    /users/me            # Get current user

# Contact
POST   /contact             # Submit contact form
GET    /contact             # Get contact info

# Projects (requires auth)
GET    /projects            # List user's projects
POST   /projects            # Create new project
GET    /projects/{id}       # Get project details
PUT    /projects/{id}       # Update project
DELETE /projects/{id}       # Delete project

# Designs (requires auth)
POST   /designs/text        # Generate design from text
POST   /designs/sketch      # Generate design from sketch
GET    /designs/{id}        # Get design details

# Analysis (requires auth)
POST   /environment/analyze # Analyze environmental metrics
POST   /compliance/validate # Validate design compliance

# Analytics
GET    /analytics/summary   # Get analytics summary
GET    /analytics/health    # Health check
```

---

## 🔐 Security Notes for Production

### Before Deploying:

1. **Change SECRET_KEY**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Update in `.env`

2. **Use Strong Database Password**:
   ```env
   DB_PASSWORD=your-very-secure-password-here
   ```

3. **Update CORS_ORIGINS**:
   ```python
   CORS_ORIGINS=["https://yourdomain.com"]
   ```

4. **Use HTTPS**:
   - Get SSL certificate (Let's Encrypt)
   - Update base URLs to `https://`

5. **Set DEBUG=False**:
   ```env
   DEBUG=False
   ```

6. **Update User Credentials**:
   - Change PgAdmin default credentials
   - Use strong passwords

---

## 📞 Support

If you encounter issues:

1. Check backend logs: `docker-compose logs backend`
2. Check frontend console: F12 → Console tab
3. Verify both services are running: `docker-compose ps`
4. Review error messages in API documentation at `/docs`

---

## 🎉 You're All Set!

Your AI Architectural Design Generator is now fully integrated and ready to use!

### Quick Summary:
- **Frontend**: Your web interface for users
- **Backend**: API server handling all business logic
- **Database**: Stores user data and projects
- **API Integration**: Frontend communicates with backend via REST APIs
- **Authentication**: JWT tokens manage user sessions

Happy designing! 🏗️✨
