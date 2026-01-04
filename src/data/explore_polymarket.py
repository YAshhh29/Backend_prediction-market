"""
Explore Polymarket API to understand data structure
Save examples for documentation
NO PANDAS NEEDED - uses only standard library!
"""

import requests
import json
from datetime import datetime
import os

def fetch_markets(limit=20):
    """Fetch prediction markets from Polymarket"""
    url = "https://gamma-api.polymarket.com/markets"
    params = {
        "limit": limit,
        "active": True
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching markets: {e}")
        return []

def find_crypto_markets(markets):
    """Filter for crypto-related markets"""
    keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'solana', 'sol', 'dogecoin', 'doge']
    
    crypto_markets = []
    for market in markets:
        question = market.get('question', '').lower()
        if any(keyword in question for keyword in keywords):
            crypto_markets.append(market)
    
    return crypto_markets

def analyze_market(market):
    """Extract key information from a market"""
    # Safely extract outcome prices
    outcome_prices = market.get('outcomePrices', [])
    
    # Convert to list if it's a string (sometimes API returns stringified JSON)
    if isinstance(outcome_prices, str):
        try:
            outcome_prices = json.loads(outcome_prices)
        except:
            outcome_prices = []
    
    # Ensure we have valid prices
    yes_price = 0
    no_price = 0
    
    if outcome_prices and len(outcome_prices) >= 1:
        try:
            yes_price = float(outcome_prices[0])
        except (ValueError, TypeError):
            yes_price = 0
    
    if outcome_prices and len(outcome_prices) >= 2:
        try:
            no_price = float(outcome_prices[1])
        except (ValueError, TypeError):
            no_price = 0
    
    return {
        'id': market.get('id', 'N/A'),
        'question': market.get('question', 'N/A'),
        'volume': market.get('volume', 0),
        'volume_24h': market.get('volume24hr', 0),
        'yes_price': yes_price,
        'no_price': no_price,
        'active': market.get('active', False),
        'end_date': market.get('endDate', 'N/A')
    }

def main():
    print("="*60)
    print("🔍 EXPLORING POLYMARKET API")
    print("="*60)
    
    print("\n📥 Fetching markets from Polymarket...")
    markets = fetch_markets(50)
    
    if not markets:
        print("❌ Failed to fetch markets!")
        return
    
    print(f"✅ Total markets fetched: {len(markets)}")
    
    # Find crypto markets
    print("\n🔎 Filtering for crypto-related markets...")
    crypto = find_crypto_markets(markets)
    print(f"✅ Found {len(crypto)} crypto-related markets")
    
    # Analyze markets
    analyzed = [analyze_market(m) for m in crypto[:10]]
    
    # Save examples
    output = {
        "fetched_at": datetime.now().isoformat(),
        "total_markets": len(markets),
        "crypto_markets_count": len(crypto),
        "analyzed_markets": analyzed
    }
    
    # Create directory if it doesn't exist
    os.makedirs('data/raw', exist_ok=True)
    
    filepath = 'data/raw/polymarket_sample.json'
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Saved to {filepath}")
    
    # Print interesting markets
    print("\n" + "="*60)
    print("📊 TOP CRYPTO MARKETS")
    print("="*60)
    
    for i, market in enumerate(analyzed[:5], 1):
        print(f"\n{i}. {market['question'][:70]}")
        
        # Convert volume to float, handle if it's a string
        try:
            volume = float(market['volume']) if market['volume'] else 0
            print(f"   Volume: ${volume:,.0f}")
        except (ValueError, TypeError):
            print(f"   Volume: {market['volume']}")
        
        # Display prices
        yes_price = market['yes_price']
        no_price = market['no_price']
        
        if yes_price > 0 or no_price > 0:
            print(f"   YES: {yes_price*100:.1f}% | NO: {no_price*100:.1f}%")
            
            # Calculate implied edge
            spread = abs(yes_price - 0.5) * 100
            print(f"   Distance from 50/50: {spread:.1f}%")
        else:
            print(f"   Prices: Not available")
    
    print("\n" + "="*60)
    print("✅ EXPLORATION COMPLETE!")
    print("="*60)
    print(f"\nYou can now review the data in: {filepath}")

if __name__ == "__main__":
    main()