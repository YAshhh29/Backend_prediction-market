# How to Run - AI Prediction Market Backend

Complete guide with every command needed to setup and run the prediction market backend codebase.

---

## 📋 Table of Contents

1. [Initial Setup](#-initial-setup)
2. [Running the Pipeline](#-running-the-pipeline)
3. [Database Management](#-database-management)
4. [Monitoring & Testing](#-monitoring--testing)
5. [All Commands Reference](#-all-commands-reference)

---

## 🚀 Initial Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/intelligent-ears/OmniPredict.git
cd OmniPredict
```

### Step 2: Create Python Virtual Environment

**Windows**:
```bash
python -m venv x402
x402\Scripts\Activate
```

**Linux/Mac**:
```bash
python3 -m venv x402
source x402/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Verify installation**:
```bash
python --version  # Should be 3.7+
pip list | grep -E "sqlalchemy|schedule|requests"
```

### Step 4: Create Environment Variables (Optional)

Create `.env` file in project root:

```
POLYMARKET_API_KEY=your_key_here
CRYPTO_COM_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
```

### Step 5: Initialize Database

**First time only**:
```bash
python -m alembic upgrade head
python test_pipeline_mock.py
```

---

## 📊 Running the Pipeline

### Start Data Pipeline (Fetches every 15 minutes)

**Windows**:
```bash
python src/data/data_fetcher.py
```

**Linux/Mac**:
```bash
python src/data/data_fetcher.py &
```

**Background on Windows (PowerShell)**:
```powershell
Start-Process python -ArgumentList "src/data/data_fetcher.py" -NoNewWindow
```

### Monitor Pipeline Status

Run in another terminal:

```bash
python src/data/monitor.py
```

This shows:
- Last update time
- Data freshness
- Market statistics
- Pipeline performance
- Error logs

### Stop Pipeline

**Windows**:
```bash
taskkill /im python.exe /f
```

**Linux/Mac**:
```bash
pkill -f data_fetcher.py
```

---

## 💾 Database Management

### Initialize Database (First Run)

```bash
# Apply all migrations
python -m alembic upgrade head

# Verify database created
ls data/markets.db  # Linux/Mac
dir data\markets.db  # Windows
```

### Create Market

```python
python -c "
from src.models.database import Database
from src.models.crud import create_market

db = Database()
session = db.get_session()

market = create_market(
    session,
    market_id='btc_100k',
    question='Will Bitcoin reach \$100k?',
    yes_price=0.65,
    no_price=0.35,
    volume_24h=150000
)
print(f'✓ Created market: {market.question}')
session.close()
"
```

### Query All Markets

```python
python -c "
from src.models.database import Database
from src.models.crud import get_all_markets

db = Database()
session = db.get_session()

markets = get_all_markets(session)
print(f'Total markets: {len(markets)}')
for market in markets[:5]:
    print(f'  - {market.question}')
session.close()
"
```

### Create Trade

```python
python -c "
from src.models.database import Database
from src.models.crud import create_trade

db = Database()
session = db.get_session()

trade = create_trade(
    session,
    market_id='btc_100k',
    side='BUY',
    outcome='YES',
    entry_price=0.65,
    position_size=100
)
print(f'✓ Created trade: {trade.side} {trade.position_size} @ {trade.entry_price}')
session.close()
"
```

### Get Open Trades

```python
python -c "
from src.models.database import Database
from src.models.crud import get_open_trades

db = Database()
session = db.get_session()

trades = get_open_trades(session)
print(f'Open trades: {len(trades)}')
for trade in trades:
    print(f'  - {trade.market_id}: {trade.side} {trade.position_size}')
session.close()
"
```

### Close Trade

```python
python -c "
from src.models.database import Database
from src.models.crud import close_trade

db = Database()
session = db.get_session()

close_trade(session, trade_id=1, exit_price=0.75, pnl_usd=1000)
print('✓ Trade closed')
session.close()
"
```

### Create Database Migrations

After modifying models in `src/models/database.py`:

```bash
# Auto-generate migration
python -m alembic revision --autogenerate -m "Add new field"

# View migrations
python -m alembic history

# Apply migration
python -m alembic upgrade head

# Downgrade migration (undo last)
python -m alembic downgrade -1
```

### Reset Database (Delete All Data)

```bash
rm data/markets.db  # Linux/Mac
del data\markets.db  # Windows

python -m alembic upgrade head
```

---

## 🧪 Monitoring & Testing

### Test with Mock Data

```bash
python test_pipeline_mock.py
```

Expected output:
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

Tests:
- Polymarket API connection
- Crypto.com API connection
- NewsAPI connection

### View Pipeline Logs

**Last 50 lines**:
```bash
# Windows
Get-Content logs\data_pipeline.log -Tail 50

# Linux/Mac
tail -50 logs/data_pipeline.log
```

**Follow log in real-time (Linux/Mac)**:
```bash
tail -f logs/data_pipeline.log
```

**Find errors**:
```bash
# Windows
Select-String "ERROR" logs\data_pipeline.log

# Linux/Mac
grep "ERROR" logs/data_pipeline.log
```

### Check Pipeline Status JSON

```bash
# Windows
Get-Content logs\pipeline_status.json

# Linux/Mac
cat logs/pipeline_status.json

# Pretty print (Linux/Mac)
cat logs/pipeline_status.json | python -m json.tool
```

### Run Specific Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_pipeline_mock.py -v

# Specific test
pytest tests/test_pipeline_mock.py::test_function_name -v
```

---

## ⚙️ Configuration Commands

### Change Pipeline Schedule

Edit `src/data/data_fetcher.py` and find this line:

```python
schedule.every(15).minutes.do(fetch_and_store_markets)
```

Change to:
```bash
# 30 minutes
schedule.every(30).minutes.do(fetch_and_store_markets)

# 1 hour
schedule.every(1).hours.do(fetch_and_store_markets)

# 1 day
schedule.every(1).days.do(fetch_and_store_markets)
```

Then restart pipeline:
```bash
python src/data/data_fetcher.py
```

### Change API Timeout

Edit `src/data/data_fetcher.py`:

```python
TIMEOUT = 15  # seconds (change this)
```

### Add Crypto Keywords

Edit `src/data/data_fetcher.py`:

```python
CRYPTO_KEYWORDS = [
    'bitcoin', 'btc', 'ethereum', 'eth', 'solana', 'sol',
    # Add more here
    'polkadot', 'dot', 'cardano', 'ada'
]
```

---

## 🚀 Production Deployment Commands

### Windows - Task Scheduler

**Create scheduled task (runs every 15 minutes)**:
```batch
schtasks /create /tn "PredictionMarketPipeline" /tr "python C:\path\to\src\data\data_fetcher.py" /sc minute /mo 15
```

**Start task**:
```batch
schtasks /run /tn "PredictionMarketPipeline"
```

**Check status**:
```batch
schtasks /query /tn "PredictionMarketPipeline"
```

**Delete task**:
```batch
schtasks /delete /tn "PredictionMarketPipeline" /f
```

### Linux/Mac - Systemd Service

**Create service file**:
```bash
sudo nano /etc/systemd/system/pipeline.service
```

**Paste this content**:
```ini
[Unit]
Description=Prediction Market Data Pipeline
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/python src/data/data_fetcher.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

**Enable and start**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pipeline
sudo systemctl start pipeline
```

**Check status**:
```bash
sudo systemctl status pipeline
```

**View logs**:
```bash
sudo journalctl -u pipeline -f
```

**Stop service**:
```bash
sudo systemctl stop pipeline
```

**Restart service**:
```bash
sudo systemctl restart pipeline
```

### Linux/Mac - Cron Job

**Edit crontab**:
```bash
crontab -e
```

**Add these lines**:
```bash
# Run pipeline at startup
@reboot cd /path/to/project && python src/data/data_fetcher.py &

# Monitor health every 6 hours
0 */6 * * * cd /path/to/project && python src/data/monitor.py >> logs/monitor.log 2>&1

# Run mock test daily at 2 AM
0 2 * * * cd /path/to/project && python test_pipeline_mock.py >> logs/daily_test.log 2>&1
```

**List cron jobs**:
```bash
crontab -l
```

**Remove cron jobs**:
```bash
crontab -r
```

### Docker Deployment

**Build Docker image**:
```bash
docker build -t prediction-market .
```

**Run container**:
```bash
docker run -d --name pipeline \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  prediction-market
```

**Check container logs**:
```bash
docker logs -f pipeline
```

**Stop container**:
```bash
docker stop pipeline
```

**Remove container**:
```bash
docker rm pipeline
```

---

## 🔍 Troubleshooting Commands

### Check Python Version

```bash
python --version
python -c "import sys; print(sys.version)"
```

### Verify Dependencies

```bash
pip list
pip show sqlalchemy
pip show schedule
pip show requests
```

### Check if Polymarket API is Reachable

```bash
python -c "
import requests
try:
    response = requests.get('https://gamma-api.polymarket.com/markets', timeout=5)
    print(f'✓ Polymarket API OK (Status: {response.status_code})')
except Exception as e:
    print(f'✗ Polymarket API Error: {e}')
"
```

### Check Database Size

```bash
# Windows
(Get-Item data\markets.db).Length / 1MB  # in MB

# Linux/Mac
du -h data/markets.db
```

### Clear Database Locks

```bash
# Windows
del data\.markets.db-shm
del data\.markets.db-wal

# Linux/Mac
rm data/.markets.db-shm
rm data/.markets.db-wal
```

### View Database Contents with SQLite

```bash
# Install SQLite (if needed)
# Windows: choco install sqlite
# Mac: brew install sqlite3
# Linux: sudo apt-get install sqlite3

# Connect to database
sqlite3 data/markets.db

# View tables
.tables

# View markets
SELECT market_id, question, yes_price, no_price FROM markets LIMIT 5;

# Count records
SELECT COUNT(*) FROM markets;

# Exit
.quit
```

### Kill Running Python Process

```bash
# Windows
taskkill /im python.exe /f

# Linux/Mac
pkill -f python
pkill -f data_fetcher
```

### Check Network Connectivity

```bash
# Windows
Test-Connection google.com

# Linux/Mac
ping -c 4 google.com
```

---

## 📦 Dependency Management

### Install Specific Package Version

```bash
pip install sqlalchemy==2.0.21
pip install schedule==1.2.0
```

### Upgrade All Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Create requirements.txt from Environment

```bash
pip freeze > requirements.txt
```

### Uninstall Package

```bash
pip uninstall sqlalchemy -y
```

---

## 🔄 Git Commands

### Push to OmniPredict Repository

```bash
git push omnipredict main
```

### Pull Latest Changes

```bash
git pull origin main
```

### Check Status

```bash
git status
```

### View Commit History

```bash
git log --oneline -10
```

### Create New Branch

```bash
git checkout -b feature/new-feature
git push -u origin feature/new-feature
```

---

## 📊 Performance & Monitoring

### Monitor Pipeline Resource Usage (Linux/Mac)

```bash
# Real-time monitoring
top -p $(pgrep -f data_fetcher.py)

# Memory and CPU
ps aux | grep data_fetcher

# Disk usage
du -sh data/
du -sh logs/
```

### Generate Performance Report

```bash
python -c "
import os
from pathlib import Path

db_size = Path('data/markets.db').stat().st_size / (1024*1024)  # MB
log_size = Path('logs/data_pipeline.log').stat().st_size / (1024*1024)  # MB

print(f'Database size: {db_size:.2f} MB')
print(f'Log file size: {log_size:.2f} MB')
print(f'Total size: {(db_size + log_size):.2f} MB')
"
```

---

## ✅ Quick Command Checklist

```bash
# Setup (first time)
python -m venv x402
x402\Scripts\Activate
pip install -r requirements.txt
python -m alembic upgrade head

# Run (daily)
python src/data/data_fetcher.py        # Terminal 1
python src/data/monitor.py             # Terminal 2 (anytime)

# Test
python test_pipeline_mock.py
python src/data/test_apis.py

# Monitor
Get-Content logs\data_pipeline.log -Tail 50

# Configuration
# Edit src/data/data_fetcher.py for schedule, timeout, keywords

# Deployment
# Use systemd (Linux), Task Scheduler (Windows), or Docker
```

---

## 🆘 Getting Help

**Check logs for errors**:
```bash
Get-Content logs\data_pipeline.log -Tail 100 | Select-String "ERROR"
```

**Run diagnostic test**:
```bash
python test_pipeline_mock.py
python src/data/test_apis.py
python src/data/monitor.py
```

**Check database integrity**:
```bash
sqlite3 data/markets.db "SELECT COUNT(*) FROM markets; SELECT COUNT(*) FROM trades;"
```

---

**Last Updated**: January 16, 2026  
**Project**: AI Prediction Market Backend  
**Repository**: OmniPredict
