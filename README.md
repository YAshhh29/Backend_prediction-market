# AI Prediction Market Backend

Automated backend for AI-powered prediction market trading on Polymarket. Fetches market data every 15 minutes, analyzes opportunities, and executes trades based on AI signals.

## Features

- **Automated Data Pipeline**: Fetches crypto markets from Polymarket every 15 minutes
- **Database Layer**: SQLAlchemy ORM with SQLite for persistent storage
- **CRUD Operations**: Complete database interface for markets, trades, and signals
- **Pipeline Monitoring**: Real-time health checks and status reporting
- **Error Handling**: Automatic retries, logging, and graceful error recovery
- **API Integration**: Connected to Polymarket, Crypto.com, and NewsAPI

## Quick Start

### 1. Setup

```bash
# Create virtual environment
python -m venv x402

# Activate environment
# Windows:
x402\Scripts\Activate
# Linux/Mac:
source x402/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Data Pipeline

```bash
# Start the pipeline (fetches markets every 15 minutes)
python src/data/data_fetcher.py

# In another terminal, monitor the pipeline
python src/data/monitor.py
```

### 3. Test with Mock Data

```bash
# Test pipeline without hitting the API
python test_pipeline_mock.py
```

## Project Structure

```
src/
├── data/                    # Data pipeline
│   ├── data_fetcher.py     # Main pipeline (355 lines)
│   ├── monitor.py          # Health monitoring (220 lines)
│   ├── explore_polymarket.py
│   ├── test_apis.py
│   └── document_apis.py
├── models/                  # Database layer
│   ├── database.py         # SQLAlchemy models (255 lines)
│   └── crud.py             # CRUD operations (317 lines)
├── api/                    # REST API endpoints (future)
├── ai/                     # AI trading signals (future)
└── utils/
    └── api_client.py       # API utilities

data/
├── raw/                    # Raw API responses
└── markets.db              # SQLite database

logs/
├── data_pipeline.log       # Pipeline activity
└── pipeline_status.json    # Status snapshot

docs/
└── api_examples.json       # Example API responses
```

## Key Files

| File | Purpose | Size |
|------|---------|------|
| [src/data/data_fetcher.py](src/data/data_fetcher.py) | Main data pipeline with scheduling | 355 lines |
| [src/data/monitor.py](src/data/monitor.py) | Pipeline health monitoring | 220 lines |
| [src/models/database.py](src/models/database.py) | SQLAlchemy ORM models | 255 lines |
| [src/models/crud.py](src/models/crud.py) | Database CRUD operations | 317 lines |
| [DATA_PIPELINE.md](DATA_PIPELINE.md) | Detailed pipeline documentation | Full guide |
| [DATABASE_SETUP.md](DATABASE_SETUP.md) | Database setup guide | Configuration |

## Data Pipeline

The pipeline runs automatically every 15 minutes:

1. **Fetch** - Pulls markets from Polymarket API
2. **Filter** - Selects crypto-related markets (Bitcoin, Ethereum, Solana, etc.)
3. **Store** - Updates database with current prices and volumes
4. **Log** - Records all activity for monitoring

### Monitor Status

```bash
python src/data/monitor.py
```

Shows:
- Last update time and data freshness
- Market statistics
- Pipeline performance (success rate)
- Recent errors/warnings
- Overall system status

## Database

Markets are stored in SQLite with fields:

- `market_id` - Unique identifier
- `question` - Market question
- `yes_price`, `no_price` - Current probabilities
- `volume_24h`, `volume` - Trading volumes
- `active`, `resolved` - Status flags
- `created_at`, `updated_at` - Timestamps

### Query Examples

```python
from src.models.crud import *
from src.models.database import get_db

db = get_db()
session = db.get_session()

# Get all crypto markets
markets = get_all_markets(session)

# Get specific market by ID
market = get_market(session, market_id="0x123...")

# Update market prices
update_market(session, market_id="0x123...", yes_price=0.65)

# Create a trade
trade = create_trade(
    session,
    market_id="0x123...",
    side="BUY",
    outcome="YES",
    entry_price=0.60,
    position_size=100
)

# Get open trades
open_trades = get_open_trades(session)
```

See [DATABASE_SETUP.md](DATABASE_SETUP.md) for full database documentation.

## Configuration

### API Timeout

Change timeout for slow connections in [src/data/data_fetcher.py](src/data/data_fetcher.py):

```python
TIMEOUT = 15  # seconds
```

### Schedule Interval

Change fetch frequency in [src/data/data_fetcher.py](src/data/data_fetcher.py):

```python
schedule.every(15).minutes.do(fetch_and_store_markets)  # Default: 15 minutes
```

### Crypto Keywords

Add or modify keywords in [src/data/data_fetcher.py](src/data/data_fetcher.py):

```python
CRYPTO_KEYWORDS = [
    'bitcoin', 'btc', 'ethereum', 'eth', 'solana', 'sol', ...
]
```

## Logging

All pipeline activity is logged to `logs/data_pipeline.log`:

```
2026-01-16 20:50:58 - Starting market data fetch...
2026-01-16 20:51:15 - Successfully fetched 98 markets
2026-01-16 20:51:15 - Filtered 42 crypto markets
2026-01-16 20:51:15 - Successfully stored/updated 42 markets
```

View logs:

```bash
# Windows
Get-Content logs\data_pipeline.log -Tail 20

# Linux/Mac
tail -20 logs/data_pipeline.log
```

## Testing

### Test Pipeline with Mock Data

```bash
python test_pipeline_mock.py
```

Tests database storage without hitting the API.

### Test APIs

```bash
python src/data/test_apis.py
```

Tests connection to Polymarket, Crypto.com, and NewsAPI.

## Troubleshooting

### Pipeline not fetching data

1. Check logs: `Get-Content logs\data_pipeline.log -Tail 50`
2. Verify internet connection
3. Check if Polymarket API is up
4. Run monitor: `python src/data/monitor.py`

### "Connection timeout" errors

Increase timeout in [src/data/data_fetcher.py](src/data/data_fetcher.py):

```python
TIMEOUT = 30  # Was 15
```

### Database errors

Check permissions on `data/` folder and verify SQLite is not locked.

## Next Steps

1. **Run the pipeline**: `python src/data/data_fetcher.py`
2. **Monitor status**: `python src/data/monitor.py` (run periodically)
3. **Build AI module**: Implement trading signal generation in `src/ai/`
4. **Create REST API**: Build FastAPI endpoints in `src/api/`
5. **Execute trades**: Integrate with Polymarket trading

## Dependencies

- **requests** - HTTP API client
- **sqlalchemy** - ORM for database
- **schedule** - Task scheduling
- **fastapi** - Web framework (future)
- **web3** - Blockchain integration (future)

See [requirements.txt](requirements.txt) for full list.

## Documentation

- [DATA_PIPELINE.md](DATA_PIPELINE.md) - Comprehensive pipeline guide
- [DATABASE_SETUP.md](DATABASE_SETUP.md) - Database models and CRUD operations
- [docs/api_examples.json](docs/api_examples.json) - API response examples

## License

Proprietary - YAshhh29

## Support

For issues:
1. Check [DATA_PIPELINE.md](DATA_PIPELINE.md) troubleshooting section
2. Review logs in `logs/data_pipeline.log`
3. Run `python src/data/monitor.py` for status
4. Test with `python test_pipeline_mock.py`
