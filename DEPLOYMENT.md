# Deployment Guide - Phase III Todo Chatbot

Complete guide for deploying the AI-Powered Todo Chatbot to production.

## 🎯 Deployment Overview

**Target Infrastructure:**
- **Backend:** Heroku (FastAPI)
- **Frontend:** Vercel (Next.js)
- **Database:** Neon PostgreSQL (Serverless)
- **AI:** OpenAI GPT-4o-mini

**Architecture:** Fully stateless, horizontally scalable

---

## 📋 Prerequisites

Before deployment, ensure you have:

- [ ] Neon PostgreSQL account with database created
- [ ] OpenAI API key with GPT-4o-mini access
- [ ] Heroku account (paid tier recommended for production)
- [ ] Vercel account
- [ ] Git repository initialized
- [ ] GitHub account (for Vercel deployment)

---

## 🗄️ Database Setup (Neon PostgreSQL)

### 1. Create Neon Database

1. Go to [Neon Console](https://console.neon.tech)
2. Click "Create Project"
3. Select region closest to your users
4. Note down the connection string

### 2. Get Connection String

Your connection string should look like:
```
postgresql://username:password@ep-xxxxx-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
```

**Important:** Use the **pooled connection** string (contains `-pooler`) for production.

### 3. Test Connection

```bash
psql "postgresql://username:password@ep-xxxxx-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

---

## 🚀 Backend Deployment (Heroku)

---

## 🚀 Backend Deployment (Heroku)

### Step 1: Install Heroku CLI

Download and install from [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

### Step 2: Login to Heroku

```bash
heroku login
```

### Step 3: Create Heroku Application

```bash
cd backend
heroku create your-todo-chatbot-api
```

**Note:** Replace `your-todo-chatbot-api` with your preferred app name.

### Step 4: Configure Environment Variables

Set all required environment variables:

```bash
# Database URL (from Neon)
heroku config:set DATABASE_URL="postgresql://user:pass@host-pooler.region.aws.neon.tech/db?sslmode=require"

# OpenAI API Key
heroku config:set OPENAI_API_KEY="sk-your-openai-api-key"

# Application Settings
heroku config:set ENV="production"
heroku config:set DEBUG="false"
```

### Step 5: Verify Procfile

Ensure `backend/Procfile` contains:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Step 6: Deploy to Heroku

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial deployment"

# Add Heroku remote
heroku git:remote -a your-todo-chatbot-api

# Deploy
git push heroku main
```

### Step 7: Initialize Database

The application will automatically create tables on startup via the `init_db()` function in the lifespan manager.

**Verification:**
```bash
heroku logs --tail
```

Look for:
```
✓ Database connection successful
✓ Database tables initialized
```

### Step 8: Test Backend

```bash
# Open in browser
heroku open

# Or test health endpoint
curl https://your-todo-chatbot-api.herokuapp.com/health
```

Expected response:
```json
{"status": "healthy"}
```

### Step 9: Get Backend URL

```bash
heroku info
```

Note the **Web URL** - you'll need this for frontend deployment.

Example: `https://your-todo-chatbot-api.herokuapp.com`

---

## 🌐 Frontend Deployment (Vercel)
   - `DEBUG=false`

4. **Deploy**
   - Render auto-deploys
   - Run migrations in Shell: `alembic upgrade head`

## Frontend Deployment

### Vercel (Recommended)

#### Prerequisites
- Vercel account
- GitHub repository

#### Steps

1. **Import Project**
   - Go to https://vercel.com
   - Click "New Project"
   - Import your GitHub repository
   - Set root directory to `frontend`

2. **Configure Build**
   - Framework Preset: Next.js
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `.next` (auto-detected)

3. **Environment Variables**
   Add in Vercel dashboard:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.herokuapp.com
   NEXT_PUBLIC_USER_ID=demo_user
   ```

4. **Deploy**
   - Click "Deploy"
   - Vercel auto-deploys on every push to main

5. **Custom Domain (Optional)**
   - Add custom domain in Vercel settings
   - Configure DNS records

## Database Setup

### Neon PostgreSQL

Your Neon database is already in production:
- No additional deployment needed
- Connection pooling enabled by default
- Automatic backups included

#### Production Optimizations

1. **Enable Connection Pooling**
   - Already configured in `backend/app/database.py`
   - Adjust pool size if needed for high traffic

2. **Set Up Read Replicas** (Optional)
   - Available in Neon paid plans
   - Configure read-only endpoints for list operations

## Post-Deployment

### 1. Run Migrations

After first deployment:
```bash
# Heroku
heroku run alembic upgrade head

# Railway
# Run in Railway console: alembic upgrade head

# Render
# Run in Shell: alembic upgrade head
```

### 2. Test Deployment

#### Test Backend
```bash
curl -X POST "https://your-backend.herokuapp.com/api/test_user/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to test deployment"}'
```

#### Test Frontend
- Visit your Vercel URL
- Try adding/listing tasks

### 3. Monitor

#### Backend Monitoring
- Heroku: `heroku logs --tail`
- Railway: View logs in dashboard
- Render: View logs in dashboard

#### Frontend Monitoring
- Vercel Analytics (built-in)
- Vercel Logs in dashboard

### 4. Set Up CI/CD

Both Vercel and Heroku/Railway support auto-deployment:
- Push to `main` → Automatic production deployment
- Push to other branches → Preview deployments (Vercel)

## Environment Variables Summary

### Backend
```env
DATABASE_URL=postgresql://user:pass@host/db
OPENAI_API_KEY=sk-...
ENV=production
DEBUG=false
```

### Frontend
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
NEXT_PUBLIC_USER_ID=demo_user
```

## Security Checklist

- ✅ Never commit `.env` files
- ✅ Use environment variables for secrets
- ✅ Enable HTTPS (auto on Heroku/Vercel)
- ✅ Configure CORS for frontend domain only
- ✅ Use connection pooling
- ✅ Set `DEBUG=false` in production

## Scaling

### Backend Scaling

**Horizontal Scaling** (Add more instances):
- Heroku: `heroku ps:scale web=2`
- Railway/Render: Adjust in dashboard

**Vertical Scaling** (Bigger instances):
- Upgrade dyno/plan size

### Frontend Scaling
- Vercel handles this automatically
- CDN distribution included

### Database Scaling
- Neon auto-scales compute
- Upgrade plan for more storage/connections

## Costs

### Free Tier
- **Heroku**: Free dynos (sleeps after 30 min inactivity)
- **Railway**: $5 free credit/month
- **Render**: Free tier with limitations
- **Vercel**: Free for personal projects
- **Neon**: Free tier (0.5GB storage)

### Estimated Costs (Low Traffic)
- Backend: $7-25/month
- Frontend: Free (Vercel)
- Database: Free (Neon)
- **Total**: $7-25/month

## Troubleshooting

### Build Failures

**Backend build fails**:
- Check `requirements.txt` is up to date
- Verify Python version in `runtime.txt`

**Frontend build fails**:
- Run `npm install` locally first
- Check for TypeScript errors

### Runtime Errors

**Database connection fails**:
- Verify `DATABASE_URL` is set correctly
- Check Neon IP allowlist (if enabled)

**OpenAI API errors**:
- Verify API key is valid
- Check OpenAI account has credits

### Performance Issues

**Slow response times**:
- Enable connection pooling (already configured)
- Increase backend instances
- Use Redis for caching (advanced)

## Rollback

### Heroku
```bash
heroku releases
heroku rollback v123
```

### Vercel
- Go to Deployments
- Select previous deployment
- Click "Promote to Production"

## Backup & Recovery

### Database Backups
- Neon: Automatic daily backups (7-day retention)
- Manual backup: Use `pg_dump`

### Code Backups
- Git repository is your backup
- Use tags for releases: `git tag v1.0.0`

## Monitoring & Alerts

### Recommended Tools
- **Sentry**: Error tracking
- **Datadog**: Performance monitoring
- **Better Uptime**: Uptime monitoring

### Basic Health Checks
- Backend: `/health` endpoint
- Set up Uptime Robot (free) to ping every 5 min

## Support

For deployment issues:
1. Check platform-specific documentation
2. Review logs for error messages
3. Verify environment variables
4. Test locally first

Good luck with your deployment! 🚀
