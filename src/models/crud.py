"""
CRUD operations for database models
"""

from sqlalchemy.orm import Session
from datetime import datetime
from .database import Market, Trade, Signal, PriceHistory


# ========== MARKET CRUD ==========

def create_market(
    db: Session,
    market_id: str,
    question: str,
    yes_price: float = None,
    no_price: float = None,
    volume: float = 0,
    description: str = None,
    active: bool = True
) -> Market:
    """Create a new market"""
    market = Market(
        market_id=market_id,
        question=question,
        yes_price=yes_price,
        no_price=no_price,
        volume=volume,
        description=description,
        active=active
    )
    db.add(market)
    db.commit()
    db.refresh(market)
    return market


def get_market(db: Session, market_id: str) -> Market:
    """Get a market by ID"""
    return db.query(Market).filter(Market.market_id == market_id).first()


def get_all_markets(db: Session, active_only: bool = False, limit: int = 100) -> list[Market]:
    """Get all markets with optional filtering"""
    query = db.query(Market)
    if active_only:
        query = query.filter(Market.active == True)
    return query.limit(limit).all()


def update_market(
    db: Session,
    market_id: str,
    yes_price: float = None,
    no_price: float = None,
    volume: float = None,
    active: bool = None,
    resolved: bool = None,
    outcome: str = None
) -> Market:
    """Update a market"""
    market = get_market(db, market_id)
    if not market:
        return None
    
    if yes_price is not None:
        market.yes_price = yes_price
    if no_price is not None:
        market.no_price = no_price
    if volume is not None:
        market.volume = volume
    if active is not None:
        market.active = active
    if resolved is not None:
        market.resolved = resolved
    if outcome is not None:
        market.outcome = outcome
    
    market.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(market)
    return market


def delete_market(db: Session, market_id: str) -> bool:
    """Delete a market"""
    market = get_market(db, market_id)
    if not market:
        return False
    
    db.delete(market)
    db.commit()
    return True


# ========== TRADE CRUD ==========

def create_trade(
    db: Session,
    market_id: str,
    side: str,
    outcome: str,
    entry_price: float,
    position_size: float,
    ai_confidence: float = None,
    reasoning: str = None,
    status: str = 'open'
) -> Trade:
    """Create a new trade"""
    trade = Trade(
        market_id=market_id,
        side=side,
        outcome=outcome,
        entry_price=entry_price,
        position_size=position_size,
        ai_confidence=ai_confidence,
        reasoning=reasoning,
        status=status
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade


def get_trade(db: Session, trade_id: int) -> Trade:
    """Get a trade by ID"""
    return db.query(Trade).filter(Trade.id == trade_id).first()


def get_trades_by_market(db: Session, market_id: str) -> list[Trade]:
    """Get all trades for a market"""
    return db.query(Trade).filter(Trade.market_id == market_id).all()


def get_open_trades(db: Session, market_id: str = None) -> list[Trade]:
    """Get all open trades, optionally filtered by market"""
    query = db.query(Trade).filter(Trade.status == 'open')
    if market_id:
        query = query.filter(Trade.market_id == market_id)
    return query.all()


def update_trade(
    db: Session,
    trade_id: int,
    exit_price: float = None,
    status: str = None,
    pnl_usd: float = None,
    pnl_percent: float = None,
    closed_at: datetime = None
) -> Trade:
    """Update a trade"""
    trade = get_trade(db, trade_id)
    if not trade:
        return None
    
    if exit_price is not None:
        trade.exit_price = exit_price
    if status is not None:
        trade.status = status
    if pnl_usd is not None:
        trade.pnl_usd = pnl_usd
    if pnl_percent is not None:
        trade.pnl_percent = pnl_percent
    if closed_at is not None:
        trade.closed_at = closed_at
    
    db.commit()
    db.refresh(trade)
    return trade


def close_trade(
    db: Session,
    trade_id: int,
    exit_price: float,
    pnl_usd: float = None,
    pnl_percent: float = None
) -> Trade:
    """Close a trade with exit price and P&L"""
    return update_trade(
        db,
        trade_id,
        exit_price=exit_price,
        status='closed',
        pnl_usd=pnl_usd,
        pnl_percent=pnl_percent,
        closed_at=datetime.utcnow()
    )


def delete_trade(db: Session, trade_id: int) -> bool:
    """Delete a trade"""
    trade = get_trade(db, trade_id)
    if not trade:
        return False
    
    db.delete(trade)
    db.commit()
    return True


# ========== SIGNAL CRUD ==========

def create_signal(
    db: Session,
    market_id: str,
    signal_type: str,
    outcome: str,
    confidence: float,
    fair_probability: float = None,
    market_probability: float = None,
    edge: float = None,
    reasoning: str = None
) -> Signal:
    """Create a new signal"""
    signal = Signal(
        market_id=market_id,
        signal_type=signal_type,
        outcome=outcome,
        confidence=confidence,
        fair_probability=fair_probability,
        market_probability=market_probability,
        edge=edge,
        reasoning=reasoning
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal


def get_signal(db: Session, signal_id: int) -> Signal:
    """Get a signal by ID"""
    return db.query(Signal).filter(Signal.id == signal_id).first()


def get_unexecuted_signals(db: Session, market_id: str = None) -> list[Signal]:
    """Get all unexecuted signals"""
    query = db.query(Signal).filter(Signal.executed == False)
    if market_id:
        query = query.filter(Signal.market_id == market_id)
    return query.all()


def update_signal(
    db: Session,
    signal_id: int,
    executed: bool = None,
    trade_id: int = None
) -> Signal:
    """Update a signal (mark as executed)"""
    signal = get_signal(db, signal_id)
    if not signal:
        return None
    
    if executed is not None:
        signal.executed = executed
    if trade_id is not None:
        signal.trade_id = trade_id
    
    db.commit()
    db.refresh(signal)
    return signal


# ========== PRICE HISTORY CRUD ==========

def create_price_history(
    db: Session,
    market_id: str,
    yes_price: float,
    no_price: float,
    volume: float = None
) -> PriceHistory:
    """Record price history for a market"""
    history = PriceHistory(
        market_id=market_id,
        yes_price=yes_price,
        no_price=no_price,
        volume=volume
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def get_price_history(db: Session, market_id: str, limit: int = 100) -> list[PriceHistory]:
    """Get price history for a market"""
    return db.query(PriceHistory).filter(
        PriceHistory.market_id == market_id
    ).order_by(PriceHistory.timestamp.desc()).limit(limit).all()


# ========== BATCH OPERATIONS ==========

def get_market_summary(db: Session, market_id: str) -> dict:
    """Get comprehensive market summary with related data"""
    market = get_market(db, market_id)
    if not market:
        return None
    
    trades = get_trades_by_market(db, market_id)
    signals = db.query(Signal).filter(Signal.market_id == market_id).all()
    
    return {
        'market': market.to_dict(),
        'trade_count': len(trades),
        'open_trades': len([t for t in trades if t.status == 'open']),
        'closed_trades': len([t for t in trades if t.status == 'closed']),
        'total_pnl': sum(t.pnl_usd for t in trades if t.pnl_usd),
        'signal_count': len(signals),
        'unexecuted_signals': len([s for s in signals if not s.executed])
    }
