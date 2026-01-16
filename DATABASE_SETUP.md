# Database Layer

The database is built with SQLAlchemy ORM and SQLite for lightweight file-based storage.

## Models

Located in `src/models/database.py`:

- **Market**: Prediction markets with yes/no prices, volume, and resolution tracking
- **Trade**: Individual trades with entry/exit prices and P&L calculation  
- **Signal**: AI trading signals with confidence scores and reasoning
- **PriceHistory**: Historical price snapshots for analysis

Each model includes a `to_dict()` method for easy serialization.

## Usage

### Initialize Database

```python
from src.models.database import Database

db = Database()
session = db.get_session()

# Create tables on first run
db.create_tables()
```

### CRUD Operations

All database operations are in `src/models/crud.py`:

```python
from src.models.crud import (
    # Markets
    create_market, get_market, get_all_markets, update_market, delete_market,
    # Trades  
    create_trade, get_trade, get_open_trades, close_trade,
    # Signals
    create_signal, get_unexecuted_signals, update_signal,
    # Price History
    create_price_history, get_price_history,
    # Utilities
    get_market_summary
)

# Create a market
market = create_market(
    session,
    market_id="btc_100k",
    question="Will Bitcoin reach $100k?",
    yes_price=0.65,
    no_price=0.35
)

# Create a trade
trade = create_trade(
    session,
    market_id="btc_100k",
    side="buy",
    outcome="yes",
    entry_price=0.65,
    position_size=100
)

# Close trade with P&L
close_trade(session, trade.id, exit_price=0.75, pnl_usd=1000)
```

## Migrations

Database schema uses Alembic for version control:

```bash
# Apply migrations
python -m alembic upgrade head

# Create migration after model changes
python -m alembic revision --autogenerate -m "describe changes"
```

## Database Location

SQLite database is stored at `data/markets.db`
