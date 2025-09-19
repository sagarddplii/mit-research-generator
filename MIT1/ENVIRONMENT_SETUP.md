# Environment Setup Guide

This guide will help you set up the environment variables needed to run the MIT Research Paper Generator application.

## Quick Setup

### 1. Backend Environment Variables

The backend requires several API keys to function properly. Edit `backend/.env` with your actual API keys:

#### Required API Keys (Minimum for basic functionality):

```bash
# OpenAI API Key (REQUIRED for paper generation)
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

#### Optional API Keys (For enhanced functionality):

```bash
# Academic Database API Keys (for better paper retrieval)
SEMANTIC_SCHOLAR_API_KEY=your-semantic-scholar-key
PUBMED_API_KEY=your-pubmed-key
CROSSREF_API_KEY=your-crossref-key
OPENALEX_API_KEY=your-openalex-key
CORE_API_KEY=your-core-key
SCOPUS_API_KEY=your-scopus-key

# Alternative LLM Provider
GEMINI_API_KEY=your-gemini-key
```

### 2. Frontend Environment Variables

The frontend configuration is in `frontend/.env`. Most settings work out of the box, but you can customize:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000  # Change if backend runs on different port

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_EXPORT=true
VITE_DEBUG_MODE=true
```

## Getting API Keys

### OpenAI API Key (Required)
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)
6. Add it to `backend/.env` as `OPENAI_API_KEY`

### Academic Database API Keys (Optional)

#### Semantic Scholar
- **Free**: No API key required for basic usage
- **With Key**: Get higher rate limits at [Semantic Scholar API](https://www.semanticscholar.org/product/api)

#### PubMed
- **Free**: No API key required
- **With Key**: Register at [NCBI](https://www.ncbi.nlm.nih.gov/account/) for higher limits

#### Crossref
- **Free**: No API key required
- **With Key**: Register at [Crossref](https://www.crossref.org/requestaccount/) for higher limits

#### OpenAlex
- **Free**: No API key required
- **With Key**: Register at [OpenAlex](https://openalex.org/) for higher limits

#### CORE
- **Free**: Register at [CORE](https://core.ac.uk/api-keys/register) for API access

#### Scopus
- **Paid**: Requires institutional access or paid subscription

## Testing Your Setup

### 1. Test Backend API Keys
```bash
cd backend
python test_apis.py
```

### 2. Test LLM Integration
```bash
cd backend
python test_llm_integration.py
```

### 3. Start the Application
```bash
# Terminal 1: Start Backend
cd backend
python simple_server.py

# Terminal 2: Start Frontend
cd frontend
npm run dev
```

## Environment File Structure

### Backend (.env)
- **API Keys**: OpenAI, academic databases
- **Server Config**: Host, port, CORS settings
- **Database**: SQLite configuration
- **Features**: Rate limiting, caching, monitoring

### Frontend (.env)
- **API Configuration**: Backend URL, timeouts
- **Feature Flags**: Analytics, export, collaboration
- **UI Settings**: Theme, animations, display limits
- **Development**: Debug mode, mock data

## Troubleshooting

### Common Issues

1. **"API key not found" errors**
   - Check that your API keys are correctly set in `backend/.env`
   - Ensure no extra spaces or quotes around the key values

2. **CORS errors in frontend**
   - Verify `CORS_ORIGINS` in `backend/.env` includes your frontend URL
   - Default includes `http://localhost:5173` for Vite dev server

3. **Backend won't start**
   - Check that all required dependencies are installed: `pip install -r requirements.txt`
   - Verify Python version (3.8+ required)

4. **Frontend can't connect to backend**
   - Ensure `VITE_API_BASE_URL` in `frontend/.env` matches your backend URL
   - Check that backend is running on the correct port

### Rate Limiting

Many academic APIs have rate limits:
- **Without API keys**: Lower limits (usually 100-1000 requests/day)
- **With API keys**: Higher limits (varies by provider)

The application includes built-in rate limiting and caching to help manage these limits.

## Production Deployment

For production deployment:

1. **Security**: Never commit real API keys to version control
2. **Environment**: Use environment variables or secure key management
3. **HTTPS**: Use HTTPS for all API communications
4. **Monitoring**: Enable logging and monitoring features
5. **Rate Limits**: Configure appropriate rate limits for your usage

## Support

If you encounter issues:
1. Check this guide first
2. Review the logs in `backend/server.log`
3. Test individual components using the test scripts
4. Ensure all dependencies are properly installed

## Example Working Configuration

Here's a minimal working configuration:

**backend/.env** (minimum required):
```bash
OPENAI_API_KEY=sk-your-openai-key-here
HOST=0.0.0.0
PORT=8000
DEBUG=true
CORS_ORIGINS=http://localhost:5173
```

**frontend/.env** (default works):
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_DEBUG_MODE=true
```

This minimal setup will allow the application to run with basic functionality using only the OpenAI API for paper generation.
