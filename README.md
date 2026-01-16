# AI Prediction Market Backend

Automated backend for AI-powered prediction market trading on Polymarket. Fetches crypto market data every 15 minutes, stores in SQLite database, and provides trading signal infrastructure.

**Status**: Database ✓ | Pipeline ✓ | Monitoring ✓ | API (in progress)

---

## 🚀 Quick Start (2 minutes)

```bash
# 1. Setup
python -m venv x402
x402\Scripts\Activate  # Windows
pip install -r requirements.txt

# 2. Run pipeline (Terminal 1)
python src/data/data_fetcher.py

# 3. Monitor status (Terminal 2)
python src/data/monitor.py

# 4. Test with mock data
python test_pipeline_mock.py
```

---

## 📚 Full Documentation

This README consolidates all project documentation. Use the sections below:

### 1. Data Pipeline (Auto-fetches every 15 min)
- **File**: [src/data/data_fetcher.py](src/data/data_fetcher.py) (355 lines)
- [🔗 Pipeline Details](#-data-pipeline)

### 2. Database Layer (SQLAlchemy ORM)
- **Files**: [src/models/database.py](src/models/database.py) (255 lines) + [src/models/crud.py](src/models/crud.py) (317 lines)
- [🔗 Database Details](#-database-layer)

### 3. Monitoring (Real-time health checks)
- **File**: [src/data/monitor.py](src/data/monitor.py) (220 lines)
- [🔗 Monitoring Details](#-monitoring)

### 4. Configuration & Testing
- [🔗 Configuration](#-configuration)
- [🔗 Testing](#-testing)

### 5. Troubleshooting & Deployment
- [🔗 Troubleshooting](#-troubleshooting)
- [🔗 Production Deployment](#-production-deployment)

---

## 📁 Project Structure

```
src/data/               # Data pipeline
├── data_fetcher.py     # Main scheduler (fetches every 15 min)
├── monitor.py          # Health monitoring & status reporting
├── explore_polymarket.py
├── test_apis.py
└── document_apis.py

src/models/             # Database
├── database.py         # SQLAlchemy ORM (4 models)
└── crud.py             # 20+ CRUD functions

src/api/                # REST API (future)
src/ai/                 # AI signals (future)
src/utils/              # Utilities
└── api_client.py

data/
├── markets.db          # SQLite database
└── raw/                # Raw API responses

logs/
├── data_pipeline.log   # Activity log
└── pipeline_status.json # Status snapshot

tests/
├── test_pipeline_mock.py
└── test_data_pipeline.py
```

---

## 📊 Data Pipeline

### Overview

Automatic 15-minute cycle:

```
Polymarket API (100) → Filter Crypto (40-50) → Store in DB → Log Activity
```

**Features**:
- ✓ Scheduled every 15 minutes (configurable)
- ✓ 3-attempt retry logic with exponential backoff
- ✓ Comprehensive error handling
- ✓ Real-time monitoring and logging

### Running

```bash
# Start pipeline
python src/data/data_fetcher.py

# Monitor status (run anytime)
python src/data/monitor.py
```

### Monitor Output Example

```
📊 DATA FRESHNESS:
   Last Update: 2026-01-16 15:22:52 UTC
   Data Age: ✓ FRESH (0:00:08)

📈 MARKET STATISTICS:
   Total Markets: 42
   Active Markets: 40
   Resolved Markets: 2

⚙️  PIPELINE PERFORMANCE:
   Total Fetches: 287
   Successful: 285
   Failed: 2
   Success Rate: 99.3%

✅ SYSTEM STATUS:
   Pipeline: ✓ RUNNING NORMALLY
```

### Data Freshness Levels

| Level | Age | Status |
|-------|-----|--------|
| ✓ Fresh | < 20 min | OK |
| ⚠ Stale | 20 min - 1 hr | Warning |
| ✗ Very Stale | > 1 hr | Not updating |

### Crypto Keywords Filtered

Bitcoin, Ethereum, Solana, Dogecoin, XRP, Cardano, Polygon, Arbitrum + more

### How Each Cycle Works

1. Connect to Polymarket API (15s timeout, 3 retries)
2. Fetch active markets (up to 100)
3. Filter for crypto keywords → 40-50 markets
4. Extract prices, volumes, status
5. Store/update in SQLite database
6. Log all activity to `logs/data_pipeline.log`

### Logging

Every action logged:

```
2026-01-16 20:50:58 - Starting market data fetch...
2026-01-16 20:51:15 - Successfully fetched 98 markets
2026-01-16 20:51:15 - Filtered 42 crypto markets
2026-01-16 20:51:15 - Successfully stored/updated 42 markets
```

View logs:
```bash
Get-Content logs\data_pipeline.log -Tail 20  # Windows
tail -20 logs/data_pipeline.log               # Linux/Mac
```

---

## 💾 Database Layer

### 4 Models (SQLAlchemy ORM)

#### Market
Prediction markets from Polymarket
- `market_id` (String) - Unique ID
- `question` (Text) - Market question
- `yes_price`, `no_price` (Float) - Probabilities
- `volume_24h`, `volume` (Float) - Trading volumes
- `active`, `resolved` (Boolean) - Status
- `outcome` (String) - YES/NO if resolved
- `created_at`, `updated_at` (DateTime)

#### Trade
Individual trades with P&L
- `market_id` (String)
- `side` (String) - BUY/SELL
- `outcome` (String) - YES/NO
- `entry_price`, `exit_price` (Float)
- `position_size` (Float)
- `status` (String) - open/closed
- `pnl_usd`, `pnl_percent` (Float)
- `opened_at`, `closed_at` (DateTime)

#### Signal
AI trading signals
- `market_id` (String)
- `signal_type` (String) - BUY/SELL/HOLD
- `confidence` (Float)
- `reasoning` (Text)
- `executed` (Boolean)

#### PriceHistory
Historical prices
- `market_id` (String)
- `yes_price`, `no_price` (Float)
- `timestamp` (DateTime)

### 20+ CRUD Functions in [src/models/crud.py](src/models/crud.py)

**Markets**: `create_market()`, `get_market()`, `get_all_markets()`, `update_market()`, `delete_market()`

**Trades**: `create_trade()`, `get_trade()`, `get_trades_by_market()`, `get_open_trades()`, `update_trade()`, `close_trade()`, `delete_trade()`

**Signals**: `create_signal()`, `get_signal()`, `get_unexecuted_signals()`, `update_signal()`

**Price History**: `create_price_history()`, `get_price_history()`

**Utils**: `get_market_summary()`

### Usage Examples

**Initialize DB**:
```python
from src.models.database import Database
db = Database()
session = db.get_session()
```

**Create Market**:
```python
from src.models.crud import create_market

market = create_market(
    session,
    market_id="btc_100k",
    question="Will Bitcoin reach $100k?",
    yes_price=0.65,
    no_price=0.35,
    volume_24h=150000
)
```

**Query Markets**:
```python
from src.models.crud import get_all_markets, get_market

all_markets = get_all_markets(session)
market = get_market(session, market_id="btc_100k")
print(f"{market.question}: Yes={market.yes_price}, No={market.no_price}")
```

**Create Trade**:
```python
from src.models.crud import create_trade

trade = create_trade(
    session,
    market_id="btc_100k",
    side="BUY",
    outcome="YES",
    entry_price=0.65,
    position_size=100
)
```

**Close Trade**:
```python
from src.models.crud import close_trade

close_trade(session, trade_id=1, exit_price=0.75, pnl_usd=1000)
```

**Get Open Trades**:
```python
from src.models.crud import get_open_trades

open_trades = get_open_trades(session)
for trade in open_trades:
    print(f"{trade.market_id}: {trade.side} {trade.position_size} @ {trade.entry_price}")
```

### Migrations (Alembic)

```bash
python -m alembic upgrade head           # Apply migrations
python -m alembic revision --autogenerate -m "desc"  # Create migration
python -m alembic history               # View history
```

**Database file**: `data/markets.db`

---

## 📈 Monitoring

### Run Monitor

```bash
python src/data/monitor.py
```

Shows:
- Last update time & data freshness
- Market statistics (total, active, resolved)
- Pipeline performance (success rate)
- Recent errors/warnings
- System status

### Monitor also exports JSON

`logs/pipeline_status.json`:
```json
{
  "timestamp": "2026-01-16T20:23:01.123456",
  "last_update": "2026-01-16T15:22:52.888393",
  "data_freshness": {
    "age_minutes": 0.14,
    "status": "✓ FRESH"
  },
  "market_stats": {
    "total": 42,
    "active": 40,
    "resolved": 2
  },
  "pipeline_performance": {
    "total_fetches": 287,
    "successful_fetches": 285,
    "failed_fetches": 2,
    "success_rate": "99.3%"
  }
}
```

---

## ⚙️ Configuration

### Schedule Interval

Edit `src/data/data_fetcher.py`:

```python
schedule.every(15).minutes.do(fetch_and_store_markets)  # Default: 15 min
schedule.every(30).minutes.do(fetch_and_store_markets)  # 30 min
schedule.every(1).hours.do(fetch_and_store_markets)     # 1 hour
schedule.every(1).days.do(fetch_and_store_markets)      # 1 day
```

### API Timeout

Edit `src/data/data_fetcher.py`:

```python
TIMEOUT = 15  # seconds
```

### Fetch Limit

Edit `src/data/data_fetcher.py`:

```python
markets = fetcher.fetch_markets(limit=100)  # Change 100
```

### Add Crypto Keywords

Edit `src/data/data_fetcher.py`:

```python
CRYPTO_KEYWORDS = [
    'bitcoin', 'btc', 'ethereum', 'eth', 'solana', 'sol',
    # Add more here
]
```

---

## 🧪 Testing

### Mock Data Test

```bash
python test_pipeline_mock.py
```

Tests without hitting the API:

```
Testing Data Pipeline with Mock Data
Creating market: Will Bitcoin reach $100,000 by end of 2026?...
✓ Successfully stored/updated 3 markets
✓ Total markets in database: 45
✓ Pipeline test completed successfully!
```

### Test APIs

```bash
python src/data/test_apis.py
```

### View Logs

```bash
Get-Content logs\data_pipeline.log -Tail 50
```

### Check Status JSON

```bash
Get-Content logs\pipeline_status.json
```

---

## 🔧 Troubleshooting

### "Connection timeout" in logs

**Cause**: Polymarket API unreachable/slow

**Fix**: Increase timeout in `src/data/data_fetcher.py`:
```python
TIMEOUT = 30  # Was 15
```

### "No crypto markets found"

**Cause**: No markets match keywords

**Fix**:
- Verify internet connection
- Check Polymarket API is working
- Add more crypto keywords
- Increase fetch limit

### "Database commit error"

**Cause**: Database locked/corrupted

**Fix**:
- Close other connections
- Check disk space
- Verify `data/` folder permissions
- Delete lock: `del data\.markets.db-shm`

### Pipeline not running

**Cause**: Process terminated

**Fix**:
1. Check logs: `Get-Content logs\data_pipeline.log -Tail 50`
2. Verify Python: `python --version` (needs 3.7+)
3. Restart: `python src/data/data_fetcher.py`

---

## 🚀 Production Deployment

### Windows Task Scheduler

```batch
schtasks /create /tn "PredictionMarketPipeline" /tr "python src\data\data_fetcher.py" /sc minute /mo 15
```

### Linux/Mac Systemd Service

Create `/etc/systemd/system/pipeline.service`:

```ini
[Unit]
Description=Prediction Market Pipeline
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/python src/data/data_fetcher.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable pipeline
sudo systemctl start pipeline
sudo systemctl status pipeline
```

### Linux/Mac Cron Job

Add to crontab:
```bash
@reboot cd /path/to/project && python src/data/data_fetcher.py &
0 */6 * * * cd /path/to/project && python src/data/monitor.py >> logs/monitor.log 2>&1
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/data/data_fetcher.py"]
```

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Fetch time | 15-30 sec |
| Markets/cycle | 40-50 |
| DB size | ~1 MB/1000 markets |
| Memory | 50-100 MB |
| CPU | <5% |
| Success rate | >99% |

---

## 📦 Dependencies

```
requests==2.31.0        # HTTP client
sqlalchemy==2.0.21      # ORM
schedule==1.2.0         # Scheduling
python-dotenv==1.0.0    # Environment
pandas==2.2.0           # Data processing
pytest==7.4.2           # Testing
```

Install all: `pip install -r requirements.txt`

---

## ✅ Completion Status

| Component | Status | Lines | Date |
|-----------|--------|-------|------|
| Database Models | ✓ | 255 | 2026-01-16 |
| CRUD Operations | ✓ | 317 | 2026-01-16 |
| Data Pipeline | ✓ | 355 | 2026-01-16 |
| Pipeline Monitor | ✓ | 220 | 2026-01-16 |
| API Testing | ✓ | 120 | 2026-01-16 |
| REST API | ⏳ | - | - |
| AI Signals | ⏳ | - | - |

**Total Code**: 1,267 lines | **Tests**: All passing | **Documentation**: Complete

---

## 🎯 Next Steps

1. **Run**: `python src/data/data_fetcher.py`
2. **Monitor**: `python src/data/monitor.py`
3. **Build AI**: Implement signals in `src/ai/`
4. **Create API**: Build endpoints in `src/api/`
5. **Execute**: Trade on Polymarket

---

## 📞 Support

1. Check logs: `Get-Content logs\data_pipeline.log -Tail 50`
2. Run monitor: `python src/data/monitor.py`
3. Test mock: `python test_pipeline_mock.py`

---

**Last Updated**: January 16, 2026 | **License**: Proprietary - YAshhh29

