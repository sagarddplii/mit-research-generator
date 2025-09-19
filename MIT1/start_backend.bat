@echo off
cd backend
set PUBMED_API_KEY=fe79d81ce5aa5307a82a59825f8d46ebdc08
set CORE_API_KEY=OfqBzEVpTsXAHdQingFR6C0uYxybNJ5o
set SCOPUS_API_KEY=603f13564a4b9ea34e21d5a7db073a65
set PYTHONIOENCODING=utf-8
echo Starting backend server with API keys...
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
