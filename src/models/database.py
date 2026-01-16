"""
Database models for AI Prediction Market
Using SQLAlchemy ORM with SQLite
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Create base class for models
Base = declarative_base()

# Database Models
class Market(Base):
    """Prediction market from Polymarket"""
    __tablename__ = 'markets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(String(100), unique=True, nullable=False)
    question = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    
    # Prices
    yes_price = Column(Float, nullable=True)
    no_price = Column(Float, nullable=True)
    
    # Volume and liquidity
    volume = Column(Float, default=0)
    volume_24h = Column(Float, default=0)
    liquidity = Column(Float, default=0)
    
    # Status
    active = Column(Boolean, default=True)
    resolved = Column(Boolean, default=False)
    outcome = Column(String(10), nullable=True)
    
    # Timestamps
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Market(id={self.market_id}, question='{self.question[:50]}...')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'market_id': self.market_id,
            'question': self.question,
            'yes_price': self.yes_price,
            'no_price': self.no_price,
            'volume': self.volume,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Trade(Base):
    """Trades executed by the AI"""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(String(100), nullable=False)
    
    # Trade details
    side = Column(String(10), nullable=False)
    outcome = Column(String(10), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    position_size = Column(Float, nullable=False)
    
    # AI decision
    ai_confidence = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    
    # Status
    status = Column(String(20), default='open')
    
    # P&L
    pnl_usd = Column(Float, nullable=True)
    pnl_percent = Column(Float, nullable=True)
    
    # Timestamps
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Trade(id={self.id}, market={self.market_id}, status={self.status})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'market_id': self.market_id,
            'side': self.side,
            'outcome': self.outcome,
            'entry_price': self.entry_price,
            'position_size': self.position_size,
            'status': self.status,
            'pnl_usd': self.pnl_usd,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None
        }


class Signal(Base):
    """AI-generated trading signals"""
    __tablename__ = 'signals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(String(100), nullable=False)
    
    # Signal details
    signal_type = Column(String(10), nullable=False)
    outcome = Column(String(10), nullable=False)
    confidence = Column(Float, nullable=False)
    
    # AI reasoning
    fair_probability = Column(Float, nullable=True)
    market_probability = Column(Float, nullable=True)
    edge = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    
    # Execution
    executed = Column(Boolean, default=False)
    trade_id = Column(Integer, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Signal(id={self.id}, type={self.signal_type}, confidence={self.confidence:.2f})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'market_id': self.market_id,
            'signal_type': self.signal_type,
            'confidence': self.confidence,
            'edge': self.edge,
            'executed': self.executed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PriceHistory(Base):
    """Historical price data for markets"""
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(String(100), nullable=False)
    
    yes_price = Column(Float, nullable=False)
    no_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PriceHistory(market={self.market_id}, yes={self.yes_price:.2f})>"


# Database connection and session management
class Database:
    """Database manager"""
    
    def __init__(self, db_url=None):
        if db_url is None:
            db_path = os.path.join('data', 'markets.db')
            db_url = f'sqlite:///{db_path}'
        
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
        print("✅ Database tables created!")
    
    def drop_tables(self):
        """Drop all tables (use carefully!)"""
        Base.metadata.drop_all(self.engine)
        print("⚠️  All tables dropped!")
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()


def get_db():
    """Get database instance"""
    return Database()


# Test the database
if __name__ == "__main__":
    print("="*60)
    print("🗄️  TESTING DATABASE SETUP")
    print("="*60)
    
    db = Database()
    
    print("\n1. Creating tables...")
    db.create_tables()
    
    print("\n2. Testing Market creation...")
    session = db.get_session()
    
    test_market = Market(
        market_id="test_btc_100k",
        question="Will Bitcoin hit $100k by end of 2024?",
        yes_price=0.45,
        no_price=0.55,
        volume=125000,
        active=True
    )
    
    session.add(test_market)
    session.commit()
    print(f"   ✅ Created: {test_market}")
    
    print("\n3. Testing query...")
    markets = session.query(Market).all()
    print(f"   ✅ Found {len(markets)} market(s)")
    
    for market in markets:
        print(f"      - {market.question}")
    
    print("\n4. Testing Signal creation...")
    test_signal = Signal(
        market_id="test_btc_100k",
        signal_type="buy",
        outcome="yes",
        confidence=0.75,
        fair_probability=0.60,
        market_probability=0.45,
        edge=0.15,
        reasoning="Market underpricing, strong momentum"
    )
    
    session.add(test_signal)
    session.commit()
    print(f"   ✅ Created: {test_signal}")
    
    print("\n" + "="*60)
    print("✅ DATABASE TEST COMPLETE!")
    print("="*60)
    print(f"\nDatabase location: data/markets.db")
    print("All 4 tables created: markets, trades, signals, price_history")
    
    session.close()