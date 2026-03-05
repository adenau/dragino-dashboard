# Dragino Temperature Sensor Dashboard

A Python application that collects, stores, and displays temperature data from a Dragino LoRaWAN temperature sensor via The Things Network.

## Features

- 📡 **Data Collection**: Fetches sensor data from The Things Network API
- 💾 **SQLAlchemy Storage**: Uses SQLite in development and MySQL in production
- 📊 **Web Dashboard**: Beautiful real-time dashboard with charts and statistics
- 🔄 **Auto-refresh**: Background data collection every hour (matches sensor reporting interval)
- 📈 **Visualization**: Interactive charts showing temperature and humidity trends

## Installation

1. Clone this repository
2. Create and activate a virtual environment:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

```bash
cp .env.example .env
# Then edit .env with your real TTN API token and app details
```

## Usage

### Run the full application (web server + data collection):

```bash
# Make sure virtual environment is activated first
python main.py
```

Then open your browser to `http://localhost:5000`

### Options:

```bash
# Collect data once without starting web server
python main.py --collect-only

# Start with initial historical data fetch
python main.py --initial-fetch

# Disable background data collection
python main.py --no-background

# Use a different port
python main.py --port 8080
```

### Test individual components:

```bash
# Test data collector
python collector.py

# Test web server only
python web_server.py
```

## Docker

Build image locally:

```bash
docker build -t dragino-dashboard:local .
```

Run container (SQLite example):

```bash
docker run --rm -p 5000:5000 --env-file .env dragino-dashboard:local
```

Use Docker Compose (MySQL sample):

```bash
docker compose up -d --build
```

Container startup runs `alembic upgrade head` before starting Gunicorn.

## Configuration

Configuration is loaded from environment variables (and automatically from a local `.env` file).

Copy `.env.example` to `.env` and customize:

- `DRAGINO_API_URL` - TTN Storage Integration endpoint
- `DRAGINO_API_TOKEN` - TTN API token
- `DRAGINO_DEVICE_ID` - Device ID to display
- `DRAGINO_ENV` - `dev` or `prod`
- `DRAGINO_DATABASE_BACKEND` - `sqlite` or `mysql`
- `DRAGINO_DATABASE_PATH` - SQLite database file path (when backend is `sqlite`)
- `DRAGINO_MYSQL_HOST` / `DRAGINO_MYSQL_PORT` / `DRAGINO_MYSQL_DATABASE` / `DRAGINO_MYSQL_USER` / `DRAGINO_MYSQL_PASSWORD` - MySQL connection settings (when backend is `mysql`)
- `DRAGINO_DATABASE_URL` - Optional explicit SQLAlchemy URL override for either backend
- `DRAGINO_WEB_HOST` / `DRAGINO_WEB_PORT` - Web server binding
- `DRAGINO_COLLECTION_INTERVAL` - Background collection interval in seconds
- `DRAGINO_LOOKBACK_HOURS` - API lookback window in hours
- `DRAGINO_ENABLE_BACKGROUND_COLLECTOR` - Enable/disable collector loop (`true`/`false`)

Database behavior:

- Select environment with `DRAGINO_ENV` (`dev` or `prod`).
- Select DB type with `DRAGINO_DATABASE_BACKEND` (`sqlite` or `mysql`).
- For `sqlite`, the app uses `DRAGINO_DATABASE_PATH`.
- For `mysql`, the app builds `mysql+pymysql://...` from `DRAGINO_MYSQL_*`.
- If `DRAGINO_DATABASE_URL` is set, it takes precedence in all environments.

## Database Schema

The database stores:
- Device ID
- Timestamp (received_at)
- Temperature readings (SHT sensor and DS sensor)
- Humidity
- Battery voltage and status
- Signal quality (RSSI, SNR)
- Frame counter
- Raw JSON data

## API Endpoints

- `GET /` - Web dashboard
- `GET /api/current` - Latest sensor reading
- `GET /api/latest/<n>` - Last N readings
- `GET /api/history/<hours>` - Readings from last N hours
- `GET /api/statistics` - Database statistics
- `GET /api/collect` - Manually trigger data collection

## Database Backend

The data layer uses SQLAlchemy. Backend selection:

1. Set `DRAGINO_ENV` to `dev` or `prod`
2. Set `DRAGINO_DATABASE_BACKEND` to `sqlite` or `mysql`
3. Optional override: set `DRAGINO_DATABASE_URL` directly

## Migrations

Schema migrations are managed with Alembic.

```bash
# Apply latest migrations
alembic upgrade head
```

In Docker, migrations are automatically applied on container startup.

## Project Structure

```
dragino_dashboard/
├── main.py              # Main application entry point
├── collector.py         # Data collection from API
├── database.py          # Database operations
├── web_server.py        # Flask web server
├── config.py            # Environment-backed configuration
├── .env.example         # Example environment settings
├── Dockerfile           # Container build definition
├── docker-compose.yml   # Sample app + MySQL compose stack
├── requirements.txt     # Python dependencies
├── templates/
│   └── index.html      # Dashboard HTML
└── sensor_data.db      # SQLite database (created on first run)
```

## License

MIT
