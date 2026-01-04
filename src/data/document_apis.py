"""
Document API responses for reference
Creates docs/api_examples.json with sample responses from all 3 APIs
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def fetch_polymarket_example():
    """Get example Polymarket response"""
    try:
        url = "https://gamma-api.polymarket.com/markets"
        response = requests.get(url, params={"limit": 2}, timeout=10)
        response.raise_for_status()
        
        markets = response.json()
        return {
            "status": "success",
            "endpoint": url,
            "method": "GET",
            "params": {"limit": 2},
            "response_sample": markets[0] if markets else None,
            "notes": "Returns list of prediction markets. No API key required."
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def fetch_crypto_com_example():
    """Get example Crypto.com response"""
    try:
        url = "https://api.crypto.com/v2/public/get-ticker"
        params = {"instrument_name": "BTC_USD"}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return {
            "status": "success",
            "endpoint": url,
            "method": "GET",
            "params": params,
            "response_sample": data,
            "notes": "Returns current price and 24h data. No API key required."
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def fetch_newsapi_example():
    """Get example NewsAPI response"""
    api_key = os.getenv("NEWS_API_KEY")
    
    if not api_key or api_key == "your_newsapi_key_here":
        return {
            "status": "error",
            "error": "NEWS_API_KEY not configured in .env file"
        }
    
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "Bitcoin",
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": 1,
            "apiKey": api_key
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Remove API key from documentation
        safe_params = params.copy()
        safe_params['apiKey'] = "YOUR_API_KEY_HERE"
        
        return {
            "status": "success",
            "endpoint": url,
            "method": "GET",
            "params": safe_params,
            "response_sample": data['articles'][0] if data.get('articles') else None,
            "notes": "Returns news articles. Requires free API key from newsapi.org. Rate limit: 100 requests/day on free tier."
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def main():
    print("="*60)
    print("📝 DOCUMENTING API RESPONSES")
    print("="*60)
    
    # Fetch examples from all APIs
    print("\n1️⃣  Fetching Polymarket example...")
    polymarket = fetch_polymarket_example()
    print(f"   Status: {polymarket['status']}")
    
    print("\n2️⃣  Fetching Crypto.com example...")
    crypto_com = fetch_crypto_com_example()
    print(f"   Status: {crypto_com['status']}")
    
    print("\n3️⃣  Fetching NewsAPI example...")
    newsapi = fetch_newsapi_example()
    print(f"   Status: {newsapi['status']}")
    
    # Create comprehensive documentation
    documentation = {
        "generated_at": datetime.now().isoformat(),
        "purpose": "API response examples for AI Prediction Market project",
        "apis": {
            "polymarket": {
                "name": "Polymarket",
                "description": "Decentralized prediction market platform",
                "authentication": "None required",
                "base_url": "https://gamma-api.polymarket.com",
                "rate_limit": "Unknown, but generous for free usage",
                "example": polymarket
            },
            "crypto_com": {
                "name": "Crypto.com Exchange",
                "description": "Cryptocurrency price data",
                "authentication": "None required for public endpoints",
                "base_url": "https://api.crypto.com/v2/public",
                "rate_limit": "100 requests per second",
                "example": crypto_com
            },
            "newsapi": {
                "name": "NewsAPI",
                "description": "News articles and headlines",
                "authentication": "API key required (free tier available)",
                "base_url": "https://newsapi.org/v2",
                "rate_limit": "100 requests per day (free tier)",
                "signup_url": "https://newsapi.org/register",
                "example": newsapi
            }
        },
        "usage_notes": {
            "polymarket": [
                "Returns array of market objects",
                "Each market has: id, question, outcomePrices, volume, etc.",
                "Use 'active: true' parameter to filter resolved markets"
            ],
            "crypto_com": [
                "Returns nested JSON with result.data array",
                "Price fields: 'a' (ask), 'b' (bid), 'c' (change)",
                "All prices are strings, convert to float for calculations"
            ],
            "newsapi": [
                "Returns articles array with title, description, url, etc.",
                "Use 'q' parameter for keyword search",
                "Free tier limited to 100 requests/day",
                "Articles may be cached for up to 15 minutes"
            ]
        }
    }
    
    # Create docs directory if it doesn't exist
    os.makedirs('docs', exist_ok=True)
    
    # Save documentation
    filepath = 'docs/api_examples.json'
    with open(filepath, 'w') as f:
        json.dump(documentation, f, indent=2)
    
    print("\n" + "="*60)
    print("✅ DOCUMENTATION COMPLETE!")
    print("="*60)
    print(f"\n📄 Saved to: {filepath}")
    print("\nThis file contains:")
    print("  • Sample API responses")
    print("  • Authentication requirements")
    print("  • Rate limits")
    print("  • Usage notes")
    print("\n💡 Use this as reference when building the AI model!")

if __name__ == "__main__":
    main()