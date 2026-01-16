"""
Reusable API client functions
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

class APIClient:
    """Wrapper for all external APIs"""
    
    def __init__(self):
        self.polymarket_base = "https://gamma-api.polymarket.com"
        self.crypto_com_base = "https://api.crypto.com/v2/public"
        self.news_api_key = os.getenv("NEWS_API_KEY")
    
    def get_polymarket_markets(self, limit=20, active=True):
        """Fetch markets from Polymarket"""
        url = f"{self.polymarket_base}/markets"
        params = {"limit": limit}
        if active:
            params["active"] = True
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def get_market_by_id(self, market_id):
        """Get specific market details"""
        url = f"{self.polymarket_base}/markets/{market_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def get_crypto_price(self, symbol="BTC"):
        """Get crypto price from Crypto.com"""
        url = f"{self.crypto_com_base}/get-ticker"
        params = {"instrument_name": f"{symbol}_USD"}
        
        # Retry logic for network issues
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()['result']['data'][0]
                return {
                    'symbol': symbol,
                    'price': float(data['a']),
                    'change_24h': float(data['c']),
                    'high_24h': float(data['h']),
                    'low_24h': float(data['l']),
                    'volume_24h': float(data['v'])
                }
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt < max_retries - 1:
                    print(f"   ⚠️  Connection error, retrying... ({attempt + 1}/{max_retries})")
                    continue
                else:
                    print(f"   ❌ Failed after {max_retries} attempts: {e}")
                    return None
    
    def get_news_sentiment(self, keyword, max_articles=10):
        """Fetch news articles for sentiment analysis"""
        if not self.news_api_key:
            raise ValueError("NEWS_API_KEY not set in .env file!")
        
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": keyword,
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": max_articles,
            "apiKey": self.news_api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()['articles']

# Usage example
if __name__ == "__main__":
    client = APIClient()
    
    print("="*60)
    print("Testing API Client Class")
    print("="*60)
    
    # Test Polymarket
    print("\n1. Testing Polymarket...")
    markets = client.get_polymarket_markets(limit=5)
    print(f"   ✅ Got {len(markets)} markets")
    if markets:
        print(f"   First market: {markets[0].get('question', 'N/A')[:50]}...")
    
    # Test Crypto.com
    print("\n2. Testing Crypto.com...")
    btc = client.get_crypto_price("BTC")
    if btc:
        print(f"   ✅ BTC: ${btc['price']:,.2f} ({btc['change_24h']:+.2f}%)")
    else:
        print(f"   ⚠️  BTC: Could not fetch price (API issue)")
    
    eth = client.get_crypto_price("ETH")
    if eth:
        print(f"   ✅ ETH: ${eth['price']:,.2f} ({eth['change_24h']:+.2f}%)")
    else:
        print(f"   ⚠️  ETH: Could not fetch price (API issue)")
    
    # Test NewsAPI
    print("\n3. Testing NewsAPI...")
    try:
        articles = client.get_news_sentiment("Bitcoin", max_articles=3)
        print(f"   ✅ Got {len(articles)} news articles")
        if articles:
            print(f"   Latest: {articles[0]['title'][:50]}...")
    except ValueError as e:
        print(f"   ⚠️  {e}")
    
    print("\n" + "="*60)
    print("✅ API Client Ready to Use!")
    print("="*60)