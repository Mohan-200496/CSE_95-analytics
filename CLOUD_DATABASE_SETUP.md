# CLOUD DATABASE SETUP FOR PUNJAB ROZGAR PORTAL

## 🌐 **CLOUD DATABASE PROVIDERS**

### **1. 🐘 PostgreSQL Cloud Providers**

#### **A) Render PostgreSQL (Recommended)**
```bash
# Free tier: 90 days, then $7/month
# URL format: postgresql://user:password@host:port/database
DATABASE_URL=postgresql://user:password@dpg-xxxxx-a.oregon-postgres.render.com/database_name
```

#### **B) Supabase (Recommended)**
```bash
# Free tier: 500MB, 2 concurrent connections
# URL format: postgresql://postgres:[password]@[host]:5432/postgres
DATABASE_URL=postgresql://postgres:password@db.supabase.co:5432/postgres
```

#### **C) Neon (Serverless PostgreSQL)**
```bash
# Free tier: 0.5 GB storage, 1 compute hour
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/database
```

#### **D) Railway**
```bash
# $5/month, generous free tier
DATABASE_URL=postgresql://postgres:password@containers-us-west-x.railway.app:5432/railway
```

#### **E) Heroku PostgreSQL**
```bash
# Hobby tier: $5/month, 10k rows
DATABASE_URL=postgresql://user:password@host.compute-1.amazonaws.com:5432/database
```

---

### **2. 🏗️ **SETUP INSTRUCTIONS**

#### **Option A: Supabase (Easiest)**

1. **Create Account**: Go to [supabase.com](https://supabase.com)
2. **Create Project**: 
   - Project name: `punjab-rozgar-portal`
   - Database password: `YourSecurePassword123!`
   - Region: `Southeast Asia (Singapore)` or closest
3. **Get Connection String**:
   - Go to Settings → Database
   - Copy connection string
   - Format: `postgresql://postgres:[YOUR-PASSWORD]@[PROJECT-REF].supabase.co:5432/postgres`

#### **Option B: Render PostgreSQL**

1. **Create Account**: Go to [render.com](https://render.com)
2. **Create PostgreSQL Database**:
   - Database Name: `punjab_rozgar_db` 
   - User: `punjab_user`
   - Region: Choose closest to your users
3. **Get Connection Info**:
   - Internal: Use for backend connection
   - External: Use for direct database access

---

### **3. 🔧 **ENVIRONMENT CONFIGURATION**

#### **Backend Environment Variables**
```bash
# .env file for backend
DATABASE_URL=postgresql://postgres:password@host:5432/database
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_CONNECT_TIMEOUT=30
DATABASE_ECHO=false
```

#### **Production Environment Variables (Render)**
```bash
# Set in Render dashboard
DATABASE_URL=postgresql://postgres:password@host:5432/database
SECRET_KEY=your-super-secret-production-key-here
DEBUG=false
CORS_ORIGINS=https://punjab-rozgar-portal1.onrender.com
```

---

### **4. 📊 **DATABASE MIGRATION SCRIPT**
