# 🚀 MIT Research Paper Generator - Deployment Guide

Complete guide to deploy the MIT Research Paper Generator with real API integrations.

## 📋 Prerequisites

### Required API Keys
1. **OpenAI API Key** (Required) - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Semantic Scholar API Key** (Optional) - Get from [Semantic Scholar API](https://www.semanticscholar.org/product/api)
3. **PubMed API Key** (Optional) - Get from [NCBI](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)
4. **CrossRef API Key** (Optional) - Email registration for higher limits
5. **OpenAlex API Key** (Optional) - No key required, but email for polite usage

### Accounts Needed
- **Render Account** (Backend hosting) - [render.com](https://render.com)
- **Vercel Account** (Frontend hosting) - [vercel.com](https://vercel.com)
- **GitHub Account** (Code repository)

## 🔧 Local Development Setup

### 1. Backend Setup
```bash
cd backend

# Create environment file
cp env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor

# Example .env content:
OPENAI_API_KEY=sk-your-actual-openai-key-here
SEMANTIC_SCHOLAR_API_KEY=your-semantic-scholar-key
PUBMED_API_KEY=your-pubmed-key
HOST=127.0.0.1
PORT=8000
DEBUG=true

# Install dependencies
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements-minimal.txt

# Start backend server
python simple_server.py
```

### 2. Frontend Setup
```bash
cd frontend

# Create environment file
cp env.example .env.local

# Edit .env.local
nano .env.local

# Example .env.local content:
VITE_API_BASE_URL=http://localhost:8000
VITE_DEBUG_MODE=true

# Install dependencies
npm install

# Start frontend dev server
npm run dev
```

### 3. Test Locally
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## 🌐 Production Deployment

### Backend Deployment (Render)

#### Step 1: Prepare Repository
```bash
# Ensure your code is pushed to GitHub
git add .
git commit -m "Add deployment configs and real API integration"
git push origin main
```

#### Step 2: Deploy to Render
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `mit-research-paper-generator-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements-minimal.txt`
   - **Start Command**: `python simple_server.py`
   - **Instance Type**: `Free` (or `Starter` for better performance)

#### Step 3: Set Environment Variables in Render
```
HOST=0.0.0.0
PORT=10000
DEBUG=false
OPENAI_API_KEY=sk-your-actual-openai-key-here
SEMANTIC_SCHOLAR_API_KEY=your-semantic-scholar-key
PUBMED_API_KEY=your-pubmed-key
CROSSREF_API_KEY=your-crossref-key
OPENALEX_API_KEY=your-openalex-key
CORS_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:3000,http://localhost:5173
```

#### Step 4: Deploy
- Click "Create Web Service"
- Wait for deployment (5-10 minutes)
- Note your backend URL: `https://your-backend-name.onrender.com`

### Frontend Deployment (Vercel)

#### Step 1: Deploy to Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# From the frontend directory
cd frontend

# Deploy
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: mit-research-paper-generator
# - Directory: ./
# - Override settings? No
```

#### Step 2: Set Environment Variables in Vercel
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to Settings → Environment Variables
4. Add:
```
VITE_API_BASE_URL=https://your-backend-name.onrender.com
VITE_ENABLE_ANALYTICS=true
VITE_DEBUG_MODE=false
```

#### Step 3: Redeploy
```bash
# Redeploy with environment variables
vercel --prod
```

## 🔄 Update CORS After Frontend Deployment

After frontend deployment, update backend CORS:

1. In Render dashboard → Your backend service → Environment
2. Update `CORS_ORIGINS`:
```
CORS_ORIGINS=https://your-frontend-domain.vercel.app
```
3. Redeploy backend

## 🧪 Testing Production Deployment

### Test Backend
```bash
# Health check
curl https://your-backend-name.onrender.com/health

# Test paper generation
curl -X POST "https://your-backend-name.onrender.com/generate" \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI in Healthcare", "requirements": {"max_papers": 10}}'
```

### Test Frontend
1. Visit `https://your-frontend-domain.vercel.app`
2. Enter a research topic
3. Click "Generate"
4. Verify it connects to backend and generates papers

## 📊 Real API Integration Features

### What Works Now:
✅ **Semantic Scholar API** - Real academic papers with abstracts, authors, citations  
✅ **CrossRef API** - DOI metadata and publication details  
✅ **OpenAlex API** - Open academic database  
✅ **PubMed API** - Biomedical literature  
✅ **arXiv API** - Preprints and research papers  
✅ **Citation Replacement** - [1], [2] placeholders → real citations  
✅ **Multiple Citation Styles** - APA, MLA, Chicago, IEEE  

### API Rate Limits (Free Tiers):
- **Semantic Scholar**: 100 requests/5 minutes (no key), 1000/5min (with key)
- **CrossRef**: No official limit, be polite
- **OpenAlex**: 10 requests/second, no daily limit
- **PubMed**: 3 requests/second (no key), 10/second (with key)
- **arXiv**: No official limit

## 🚨 Troubleshooting

### Backend Issues
```bash
# Check logs in Render dashboard
# Common issues:
# 1. Missing OPENAI_API_KEY → Add in environment variables
# 2. CORS errors → Update CORS_ORIGINS with frontend URL
# 3. Timeout errors → Check API key validity
```

### Frontend Issues
```bash
# Check browser console for errors
# Common issues:
# 1. API connection failed → Check VITE_API_BASE_URL
# 2. CORS blocked → Update backend CORS_ORIGINS
# 3. Build failures → Check for TypeScript errors
```

### API Integration Issues
```bash
# Test individual APIs:
curl "https://api.semanticscholar.org/graph/v1/paper/search?query=AI&limit=1"
curl "https://api.crossref.org/works?query=machine+learning&rows=1"
curl "https://api.openalex.org/works?search=AI&per-page=1"
```

## 🔒 Security Best Practices

### Environment Variables
- Never commit `.env` files
- Use different API keys for dev/prod
- Rotate keys regularly
- Monitor API usage

### CORS Configuration
- Specify exact domains in production
- Don't use `*` for `allow_origins` in production
- Update CORS when frontend domain changes

## 📈 Monitoring & Analytics

### Backend Monitoring
- Monitor API usage in Render dashboard
- Check error rates and response times
- Set up alerts for downtime

### Frontend Analytics
- Monitor user interactions
- Track paper generation success rates
- Monitor page load times

## 🚀 Quick Deploy Commands

### One-time Setup
```bash
# Backend
cd backend
cp env.example .env
# Edit .env with your API keys
git add . && git commit -m "Add production config" && git push

# Frontend  
cd frontend
cp env.example .env.local
# Edit .env.local
npm install -g vercel
```

### Deploy
```bash
# Deploy backend to Render (via dashboard or CLI)
# Deploy frontend to Vercel
cd frontend && vercel --prod
```

### Update Environment
```bash
# Update backend env vars in Render dashboard
# Update frontend env vars in Vercel dashboard
# Redeploy both services
```

## 🎉 Success Checklist

✅ Backend deployed to Render with real API keys  
✅ Frontend deployed to Vercel  
✅ CORS configured correctly  
✅ Environment variables set  
✅ Real paper retrieval working  
✅ Citation replacement functional  
✅ End-to-end paper generation working  

Your MIT Research Paper Generator is now live with real academic API integration! 🎓✨

