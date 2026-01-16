"""
Test script for the data pipeline - uses mock data since Polymarket API is currently unreachable
This allows testing the database storage and monitoring functionality
"""

import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import Market, Database
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_pipeline_with_mock_data():
    """Test the pipeline by inserting mock market data"""
    
    logger.info("=" * 60)
    logger.info("Testing Data Pipeline with Mock Data")
    logger.info("=" * 60)
    
    db = Database()
    session = db.get_session()
    
    # Mock market data (as would come from Polymarket API)
    mock_markets = [
        {
            'market_id': 'mock_btc_100k_1',
            'question': 'Will Bitcoin reach $100,000 by end of 2026?',
            'description': 'Mock market for testing',
            'yes_price': 0.65,
            'no_price': 0.35,
            'volume_24h': 150000.00,
            'volume': 500000.00,
            'active': True,
            'resolved': False,
            'outcome': None
        },
        {
            'market_id': 'mock_eth_5k_1',
            'question': 'Will Ethereum reach $5,000 by mid-2026?',
            'description': 'Mock market for testing',
            'yes_price': 0.58,
            'no_price': 0.42,
            'volume_24h': 120000.00,
            'volume': 400000.00,
            'active': True,
            'resolved': False,
            'outcome': None
        },
        {
            'market_id': 'mock_crypto_bull_1',
            'question': 'Crypto Bull Run in 2026?',
            'description': 'Mock market for testing',
            'yes_price': 0.72,
            'no_price': 0.28,
            'volume_24h': 200000.00,
            'volume': 600000.00,
            'active': True,
            'resolved': False,
            'outcome': None
        }
    ]
    
    try:
        stored_count = 0
        
        for market_data in mock_markets:
            # Check if market exists
            existing = session.query(Market).filter_by(
                market_id=market_data['market_id']
            ).first()
            
            if existing:
                # Update existing
                logger.info(f"Updating market: {market_data['question'][:50]}...")
                existing.yes_price = market_data['yes_price']
                existing.no_price = market_data['no_price']
                existing.volume_24h = market_data['volume_24h']
                existing.volume = market_data['volume']
                existing.updated_at = datetime.utcnow()
            else:
                # Create new
                logger.info(f"Creating market: {market_data['question'][:50]}...")
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
        
        session.commit()
        logger.info(f"✓ Successfully stored/updated {stored_count} markets")
        
        # Verify data was stored
        count = session.query(Market).count()
        logger.info(f"✓ Total markets in database: {count}")
        
        # Show sample
        logger.info("\nSample markets:")
        markets = session.query(Market).order_by(Market.updated_at.desc()).limit(3).all()
        for market in markets:
            logger.info(f"  - {market.question}")
            logger.info(f"    Yes: {market.yes_price}, No: {market.no_price}")
            logger.info(f"    Updated: {market.updated_at}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Pipeline test completed successfully!")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"✗ Error during test: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()


if __name__ == "__main__":
    test_pipeline_with_mock_data()
