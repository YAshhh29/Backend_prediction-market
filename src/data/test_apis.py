"""
Test all API connections on Day 1
Run this to verify everything works!
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_polymarket():
    """Test Polymarket API"""
    print("\n🔵 Testing Polymarket API...")
    try:
        url = "https://gamma-api.polymarket.com/markets"
        params = {"limit": 5}  # Just get 5 markets
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        markets = response.json()
        print(f"✅ Success! Found {len(markets)} markets")
        
        # Show first market
        if markets:
            first = markets[0]
            print(f"   Example: {first.get('question', 'N/A')[:60]}...")
            print(f"   Odds: {first.get('outcomePrices', ['N/A'])[0]}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_crypto_com():
    """Test Crypto.com API with retry logic"""
    print("\n🟠 Testing Crypto.com API...")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            url = "https://api.crypto.com/v2/public/get-ticker"
            params = {"instrument_name": "BTC_USD"}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            price = data['result']['data'][0]['a']
            change = data['result']['data'][0]['c']
            
            if attempt > 0:
                print(f"   (Succeeded on attempt {attempt + 1}/{max_retries})")
            
            print(f"✅ Success! BTC Price: ${float(price):,.2f}")
            print(f"   24h Change: {float(change):+.2f}%")
            
            return True
            
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < max_retries - 1:
                print(f"   ⚠️  Connection error, retrying... ({attempt + 1}/{max_retries})")
                continue
            else:
                print(f"❌ Failed after {max_retries} attempts")
                print(f"   This is normal - Crypto.com API occasionally blocks connections")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    return False

def test_news_api():
    """Test NewsAPI"""
    print("\n🟢 Testing NewsAPI...")
    
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key or api_key == "your_newsapi_key_here":
        print("❌ Error: NEWS_API_KEY not set in .env file!")
        print("   Get your key at: https://newsapi.org/register")
        return False
    
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "Bitcoin",
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": 3,
            "apiKey": api_key
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get('articles', [])
        
        print(f"✅ Success! Found {len(articles)} articles")
        if articles:
            print(f"   Latest: {articles[0]['title'][:60]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all API tests"""
    print("="*60)
    print("🚀 API CONNECTION TEST")
    print("="*60)
    
    results = {
        "Polymarket": test_polymarket(),
        "Crypto.com": test_crypto_com(),
        "NewsAPI": test_news_api()
    }
    
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    
    for api, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{api:15} {status}")
    
    all_working = all(results.values())
    
    print("\n" + "="*60)
    if all_working:
        print("🎉 ALL APIS WORKING! You're ready to code!")
    else:
        print("⚠️  Some APIs failed. Check errors above.")
    print("="*60)

if __name__ == "__main__":
    main()