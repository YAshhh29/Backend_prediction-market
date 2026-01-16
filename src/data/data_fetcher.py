"""
Data Pipeline - Fetches market data from Polymarket every 15 minutes
Stores crypto-related markets in the database
Includes error handling, logging, and retry logic
"""

import requests
import json
import logging
from datetime import datetime
import schedule
import time
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.database import Market, Database
from src.models.crud import create_market, update_market, get_market

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'data_pipeline.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PolymarketFetcher:
    """Handles fetching data from Polymarket API"""
    
    BASE_URL = "https://gamma-api.polymarket.com/markets"
    TIMEOUT = 15
    MAX_RETRIES = 3
    
    CRYPTO_KEYWORDS = [
        'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 
        'solana', 'sol', 'dogecoin', 'doge', 'xrp', 'ripple',
        'cardano', 'ada', 'polygon', 'matic', 'arbitrum'
    ]
    
    def __init__(self):
        self.db = Database()
        
    def fetch_markets(self, limit=100):
        """Fetch markets from Polymarket with retry logic"""
        for attempt in range(self.MAX_RETRIES):
            try:
                params = {
                    "limit": limit,
                    "active": True
                }
                
                logger.info(f"Fetching markets from Polymarket (attempt {attempt + 1}/{self.MAX_RETRIES})")
                response = requests.get(self.BASE_URL, params=params, timeout=self.TIMEOUT)
                response.raise_for_status()
                
                markets = response.json()
                logger.info(f"Successfully fetched {len(markets)} markets from Polymarket")
                return markets
                
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error on attempt {attempt + 1}: {str(e)}")
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch markets after {self.MAX_RETRIES} attempts")
                    return []
                    
            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout on attempt {attempt + 1}: {str(e)}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error("Failed to fetch markets: timeout after retries")
                    return []
                    
            except Exception as e:
                logger.error(f"Unexpected error fetching markets: {str(e)}")
                return []
        
        return []
    
    def filter_crypto_markets(self, markets):
        """Filter for crypto-related markets"""
        crypto_markets = []
        
        for market in markets:
            question = market.get('question', '').lower()
            
            # Check if any crypto keyword is in the question
            if any(keyword in question for keyword in self.CRYPTO_KEYWORDS):
                crypto_markets.append(market)
        
        logger.info(f"Filtered {len(crypto_markets)} crypto markets from {len(markets)} total markets")
        return crypto_markets
    
    def extract_market_data(self, market):
        """Extract relevant data from Polymarket market object"""
        try:
            # Parse outcome prices
            outcome_prices = market.get('outcomePrices', [])
            if isinstance(outcome_prices, str):
                try:
                    outcome_prices = json.loads(outcome_prices)
                except:
                    outcome_prices = []
            
            yes_price = float(outcome_prices[0]) if outcome_prices and len(outcome_prices) > 0 else None
            no_price = float(outcome_prices[1]) if outcome_prices and len(outcome_prices) > 1 else None
            
            # Parse volumes
            volume_24h = float(market.get('volume24h', 0)) if market.get('volume24h') else 0
            volume = float(market.get('volume', 0)) if market.get('volume') else 0
            
            return {
                'market_id': market.get('id'),
                'question': market.get('question', 'Unknown'),
                'description': market.get('description'),
                'yes_price': yes_price,
                'no_price': no_price,
                'volume_24h': volume_24h,
                'volume': volume,
                'active': market.get('active', True),
                'resolved': market.get('resolved', False),
                'outcome': market.get('outcome'),
                'end_date': market.get('endDate')
            }
        except Exception as e:
            logger.error(f"Error extracting data from market {market.get('id')}: {str(e)}")
            return None
    
    def store_markets(self, crypto_markets):
        """Store or update markets in database"""
        if not crypto_markets:
            logger.warning("No crypto markets to store")
            return 0
        
        session = self.db.get_session()
        stored_count = 0
        
        try:
            for market_data in crypto_markets:
                if not market_data:
                    continue
                
                try:
                    # Check if market already exists
                    existing = session.query(Market).filter_by(
                        market_id=market_data['market_id']
                    ).first()
                    
                    if existing:
                        # Update existing market
                        existing.yes_price = market_data['yes_price']
                        existing.no_price = market_data['no_price']
                        existing.volume_24h = market_data['volume_24h']
                        existing.volume = market_data['volume']
                        existing.active = market_data['active']
                        existing.resolved = market_data['resolved']
                        existing.outcome = market_data['outcome']
                        existing.updated_at = datetime.utcnow()
                    else:
                        # Create new market
                        new_market = Market(
                            market_id=market_data['market_id'],
                            question=market_data['question'],
                            description=market_data['description'],
                            yes_price=market_data['yes_price'],
                            no_price=market_data['no_price'],
                            volume_24h=market_data['volume_24h'],
                            volume=market_data['volume'],
                            active=market_data['active'],
                            resolved=market_data['resolved'],
                            outcome=market_data['outcome']
                        )
                        session.add(new_market)
                    
                    stored_count += 1
                    
                except Exception as e:
                    logger.error(f"Error storing market {market_data.get('market_id')}: {str(e)}")
                    continue
            
            session.commit()
            logger.info(f"Successfully stored/updated {stored_count} markets")
            return stored_count
            
        except Exception as e:
            logger.error(f"Database commit error: {str(e)}")
            session.rollback()
            return 0
        finally:
            session.close()


def fetch_and_store_markets():
    """Main function to fetch and store market data"""
    logger.info("=" * 60)
    logger.info("Starting market data fetch...")
    
    try:
        fetcher = PolymarketFetcher()
        
        # Fetch from Polymarket
        markets = fetcher.fetch_markets(limit=100)
        
        if not markets:
            logger.warning("No markets fetched from Polymarket")
            return False
        
        # Filter crypto markets
        crypto_markets = fetcher.filter_crypto_markets(markets)
        
        if not crypto_markets:
            logger.warning("No crypto markets found")
            return False
        
        # Extract and store data
        market_data_list = []
        for market in crypto_markets:
            market_data = fetcher.extract_market_data(market)
            if market_data:
                market_data_list.append(market_data)
        
        # Store in database
        stored = fetcher.store_markets(market_data_list)
        
        logger.info(f"Data fetch completed successfully: {stored} markets stored")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"Fatal error in fetch_and_store_markets: {str(e)}")
        logger.info("=" * 60)
        return False


def schedule_pipeline():
    """Schedule the data pipeline to run every 15 minutes"""
    
    logger.info("Initializing data pipeline scheduler...")
    
    # Schedule the job
    schedule.every(15).minutes.do(fetch_and_store_markets)
    
    logger.info("Pipeline scheduled to run every 15 minutes")
    logger.info("Starting scheduler loop...")
    
    # Run the scheduler
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute if a job needs to run
    except KeyboardInterrupt:
        logger.info("Pipeline scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}")


if __name__ == "__main__":
    # Run the scheduler
    schedule_pipeline()
