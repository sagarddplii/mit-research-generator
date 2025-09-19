#!/usr/bin/env python3
"""
Test script to verify API keys are working and fetch real data.
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')
load_dotenv()

async def test_pubmed_api():
    """Test PubMed API with the provided key."""
    api_key = os.getenv('PUBMED_API_KEY', '')
    print(f"PubMed API Key: {api_key[:8]}..." if api_key else "No PubMed API key found")
    
    if not api_key:
        print("❌ No PubMed API key - skipping test")
        return False
    
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': 'covid',
                'retmax': 5,
                'retmode': 'json',
                'api_key': api_key
            }
            
            async with session.get(url, params=params) as response:
                print(f"PubMed API Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    ids = data.get('esearchresult', {}).get('idlist', [])
                    print(f"✅ PubMed API working - found {len(ids)} papers")
                    return True
                else:
                    print(f"❌ PubMed API failed with status {response.status}")
                    return False
    except Exception as e:
        print(f"❌ PubMed API error: {e}")
        return False

async def test_core_api():
    """Test CORE API with the provided key."""
    api_key = os.getenv('CORE_API_KEY', '')
    print(f"CORE API Key: {api_key[:8]}..." if api_key else "No CORE API key found")
    
    if not api_key:
        print("❌ No CORE API key - skipping test")
        return False
    
    try:
        headers = {'Authorization': f'Bearer {api_key}'}
        async with aiohttp.ClientSession(headers=headers) as session:
            url = "https://api.core.ac.uk/v3/search/works"
            params = {
                'q': 'covid',
                'limit': 5
            }
            
            async with session.get(url, params=params) as response:
                print(f"CORE API Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    results = data.get('results', [])
                    print(f"✅ CORE API working - found {len(results)} papers")
                    return True
                else:
                    print(f"❌ CORE API failed with status {response.status}")
                    text = await response.text()
                    print(f"Response: {text[:200]}")
                    return False
    except Exception as e:
        print(f"❌ CORE API error: {e}")
        return False

async def test_openalex_api():
    """Test OpenAlex API (free, no key needed)."""
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.openalex.org/works"
            params = {
                'search': 'covid',
                'per-page': 5,
                'mailto': 'research@mit.edu'
            }
            
            async with session.get(url, params=params) as response:
                print(f"OpenAlex API Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    results = data.get('results', [])
                    print(f"✅ OpenAlex API working - found {len(results)} papers")
                    return True
                else:
                    print(f"❌ OpenAlex API failed with status {response.status}")
                    return False
    except Exception as e:
        print(f"❌ OpenAlex API error: {e}")
        return False

async def main():
    """Test all APIs."""
    print("🧪 Testing API Keys and Data Fetching...")
    print("=" * 50)
    
    # Test environment variables
    print("Environment Variables:")
    print(f"PUBMED_API_KEY: {'✅ Set' if os.getenv('PUBMED_API_KEY') else '❌ Not set'}")
    print(f"CORE_API_KEY: {'✅ Set' if os.getenv('CORE_API_KEY') else '❌ Not set'}")
    print(f"SCOPUS_API_KEY: {'✅ Set' if os.getenv('SCOPUS_API_KEY') else '❌ Not set'}")
    print()
    
    # Test APIs
    results = []
    results.append(await test_pubmed_api())
    print()
    results.append(await test_core_api())
    print()
    results.append(await test_openalex_api())
    
    print("\n" + "=" * 50)
    working_apis = sum(results)
    print(f"📊 Summary: {working_apis}/{len(results)} APIs working")
    
    if working_apis > 0:
        print("✅ System can fetch real research data!")
    else:
        print("❌ No APIs working - check API keys and network connection")

if __name__ == "__main__":
    asyncio.run(main())
