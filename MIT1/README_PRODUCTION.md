# MIT Research Paper Generator - Production Deployment Guide

## 🚀 Quick Start

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

# Frontend  
cd frontend
npm install
npm run dev
```

### Production Deployment with Docker

```bash
# Build and run with Docker Compose
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔧 Configuration

### API Keys (Required for Full Functionality)
Add these to `backend/.env`:

```env
# Your provided API keys
PUBMED_API_KEY=fe79d81ce5aa5307a82a59825f8d46ebdc08
CORE_API_KEY=OfqBzEVpTsXAHdQingFR6C0uYxybNJ5o
SCOPUS_API_KEY=603f13564a4b9ea34e21d5a7db073a65

# Optional (free APIs)
SEMANTIC_SCHOLAR_API_KEY=
CROSSREF_API_KEY=
OPENALEX_API_KEY=

# OpenAI (optional - system works without it)
OPENAI_API_KEY=your_openai_key_here
```

### Environment Variables

**Backend (.env)**:
```env
HOST=0.0.0.0
PORT=8000
DEBUG=false
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

**Frontend (.env)**:
```env
VITE_API_BASE_URL=http://localhost:8000
# For production: VITE_API_BASE_URL=https://api.yourdomain.com
```

## 🌐 Production Features

### ✅ Real Data Sources
- **PubMed**: Medical research papers
- **CORE**: Academic publications  
- **Scopus**: Scientific literature
- **OpenAlex**: Open research database
- **arXiv**: Preprint repository
- **CrossRef**: Citation database

### ✅ Professional Paper Generation
- 17+ comprehensive sections
- Academic formatting with citations
- Professional abstracts (250-400 words)
- Downloadable formatted papers
- Real research data integration

### ✅ Production Ready
- Docker containerization
- Health checks and monitoring
- Nginx reverse proxy
- Security headers
- Gzip compression
- Error handling and logging
- Fallback data generation

## 📊 API Endpoints

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /status` - Data source status
- `POST /research-pipeline` - Full research workflow
- `POST /retrieve` - Paper retrieval only

### Usage Example
```bash
# Generate a research paper
curl -X POST http://localhost:8000/research-pipeline \
  -H "Content-Type: application/json" \
  -d '{"query": "artificial intelligence in healthcare"}'

# Check system status
curl http://localhost:8000/status
```

## 🔄 Deployment Options

### Option 1: Docker Compose (Recommended)
```bash
docker-compose up -d --build
```
- Frontend: http://localhost:80
- Backend: http://localhost:8000

### Option 2: Manual Deployment
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend
cd frontend
npm install
npm run build
# Serve dist/ with nginx or static server
```

### Option 3: Cloud Deployment
- **Heroku**: Use provided `Procfile`
- **AWS ECS**: Use Docker containers
- **Google Cloud Run**: Deploy containerized services
- **Vercel**: Frontend deployment
- **Railway**: Full-stack deployment

## 🛡️ Security & Performance

### Security Features
- CORS configuration
- Input validation
- Rate limiting ready
- Security headers
- Non-root containers

### Performance Optimizations
- API response caching
- Gzip compression
- Static asset caching
- Connection pooling ready
- Background task processing

## 📈 Monitoring & Logging

### Health Checks
- `/health` - Application health
- `/status` - Data source availability
- Docker health checks configured

### Logging
- Structured logging with timestamps
- API response codes and timing
- Error tracking and debugging
- Request/response logging

## 🚨 Troubleshooting

### Common Issues
1. **API Keys**: Ensure all keys are properly set in `.env`
2. **CORS**: Check `CORS_ORIGINS` configuration
3. **Port Conflicts**: Ensure ports 8000 and 80 are available
4. **Docker**: Run `docker-compose down` then `docker-compose up --build`

### Debug Mode
```bash
# Enable debug logging
export DEBUG=True
uvicorn api_server:app --reload --log-level debug
```

## 📝 System Requirements

### Minimum Requirements
- Python 3.11+
- Node.js 18+
- 4GB RAM
- 2 CPU cores

### Recommended Production
- 8GB+ RAM
- 4+ CPU cores
- SSD storage
- Load balancer for high traffic

## 🔗 Integration

### API Integration
```javascript
// Frontend API call
const response = await fetch('http://localhost:8000/research-pipeline', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'your research topic' })
});
const data = await response.json();
```

### Webhook Support (Future)
- Research completion notifications
- Progress updates
- Error alerts

---

## 🎯 Production Checklist

- [x] API keys configured
- [x] Environment variables set
- [x] Docker containers built
- [x] Health checks working
- [x] CORS properly configured
- [x] Security headers enabled
- [x] Logging configured
- [x] Error handling implemented
- [x] Performance optimized
- [x] Documentation complete

**System Status**: ✅ Production Ready

Access your deployed system:
- **Frontend**: http://localhost (or your domain)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
