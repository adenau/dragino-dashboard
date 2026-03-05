"""
Main application script for the Dragino Temperature Sensor Dashboard

This script orchestrates the data collection and web server components.
"""
import argparse

import config
from database import SensorDatabase
from collector import SensorDataCollector
from collector_runtime import start_background_collector_thread
from web_server import app


def main():
    parser = argparse.ArgumentParser(
        description='Dragino Temperature Sensor Dashboard'
    )
    parser.add_argument(
        '--collect-only',
        action='store_true',
        help='Only collect data once and exit (no web server)'
    )
    parser.add_argument(
        '--no-background',
        action='store_true',
        help='Disable background data collection'
    )
    parser.add_argument(
        '--initial-fetch',
        action='store_true',
        help='Fetch historical data on startup'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=config.WEB_PORT,
        help=f'Web server port (default: {config.WEB_PORT})'
    )
    
    args = parser.parse_args()
    
    # Initialize database
    print("Initializing database...")
    db = SensorDatabase()
    print(f"Database ready: {config.DATABASE_PATH}")
    
    # Collect-only mode
    if args.collect_only:
        print("\n=== Collection Mode ===")
        collector = SensorDataCollector(database=db)
        result = collector.collect_and_store()
        print(f"\nResults:")
        print(f"  Fetched: {result['fetched']}")
        print(f"  Stored: {result['stored']}")
        print(f"  Duplicates: {result['duplicates']}")
        
        # Show statistics
        stats = db.get_statistics(config.DEVICE_ID)
        print(f"\nDatabase Statistics:")
        print(f"  Total Readings: {stats['total_readings']}")
        print(f"  First Reading: {stats['first_reading']}")
        print(f"  Last Reading: {stats['last_reading']}")
        if stats['avg_temp_sht']:
            print(f"  Avg Temperature: {stats['avg_temp_sht']}°C")
        return
    
    # Initial data fetch
    if args.initial_fetch:
        print("\n=== Initial Data Fetch ===")
        collector = SensorDataCollector(database=db)
        result = collector.collect_and_store()
        print(f"Fetched {result['stored']} readings")
    
    # Start background collector thread
    if not args.no_background:
        start_background_collector_thread(config.COLLECTION_INTERVAL)
    else:
        print("Background collection disabled")
    
    # Start web server
    print(f"\n=== Starting Web Server ===")
    print(f"Dashboard available at: http://localhost:{args.port}")
    print(f"API endpoints:")
    print(f"  - GET /api/current         - Latest reading")
    print(f"  - GET /api/latest/<n>      - Last N readings")
    print(f"  - GET /api/history/<hours> - Readings from last N hours")
    print(f"  - GET /api/statistics      - Database statistics")
    print(f"  - GET /api/collect         - Manually trigger collection")
    print(f"\nPress Ctrl+C to stop\n")
    
    app.run(
        host=config.WEB_HOST,
        port=args.port,
        debug=False,
        threaded=True
    )


if __name__ == '__main__':
    main()
