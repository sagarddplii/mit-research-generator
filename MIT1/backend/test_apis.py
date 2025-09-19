#!/usr/bin/env python3
"""
Test script to verify API keys are working correctly.
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

async def test_pubmed():
    """Test PubMed API with your key."""
    api_key = os.getenv('PUBMED_API_KEY')
    print(f"Testing PubMed API (Key: {'***' + api_key[-4:] if api_key else 'Not set'})")
    
    try:
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': 'machine learning healthcare',
                'retmax': 3,
                'retmode': 'json'
            }
            
            if api_key:
                params['api_key'] = api_key
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    count = data.get('esearchresult', {}).get('count', '0')
                    print(f"✅ PubMed: Found {count} papers")
                    return True
                else:
                    print(f"❌ PubMed: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"❌ PubMed Error: {e}")
        return False

async def test_core():
    """Test CORE API with your key."""
    api_key = os.getenv('CORE_API_KEY')
    print(f"Testing CORE API (Key: {'***' + api_key[-4:] if api_key else 'Not set'})")
    
    try:
        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        async with aiohttp.ClientSession(headers=headers) as session:
            url = "https://api.core.ac.uk/v3/search/works"
            params = {
                'q': 'artificial intelligence',
                'limit': 3
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    count = len(data.get('results', []))
                    print(f"✅ CORE: Found {count} papers")
                    if count > 0:
                        sample_title = data['results'][0].get('title', 'No title')
                        print(f"   Sample: {sample_title[:60]}...")
                    return True
                else:
                    print(f"❌ CORE: HTTP {response.status}")
                    text = await response.text()
                    print(f"   Response: {text[:100]}...")
                    return False
    except Exception as e:
        print(f"❌ CORE Error: {e}")
        return False

async def test_openalex():
    """Test OpenAlex API (no key needed)."""
    print("Testing OpenAlex API (no key required)")
    
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.openalex.org/works"
            params = {
                'search': 'machine learning',
                'per-page': 3
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    count = len(data.get('results', []))
                    print(f"✅ OpenAlex: Found {count} papers")
                    return True
                else:
                    print(f"❌ OpenAlex: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"❌ OpenAlex Error: {e}")
        return False

async def main():
    """Run all API tests."""
    print("🧪 Testing Real API Integration with Your Keys\n")
    
    results = []
    results.append(await test_pubmed())
    results.append(await test_core())
    results.append(await test_openalex())
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} APIs working")
    
    if all(results):
        print("🎉 All APIs working! Your keys are valid.")
    else:
        print("⚠️  Some APIs failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
