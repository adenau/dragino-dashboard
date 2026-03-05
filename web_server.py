"""Web server for displaying sensor data"""
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import config
from database import SensorDatabase
from collector import SensorDataCollector


app = Flask(__name__)
db = SensorDatabase()
collector = SensorDataCollector(database=db)


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/current')
def api_current():
    """Get the current/latest sensor reading"""
    reading = collector.get_current_temperature(config.DEVICE_ID)
    if reading:
        return jsonify({
            'success': True,
            'data': reading
        })
    return jsonify({
        'success': False,
        'message': 'No data available'
    }), 404


@app.route('/api/latest/<int:limit>')
def api_latest(limit):
    """Get the latest N readings"""
    readings = db.get_latest_readings(device_id=config.DEVICE_ID, limit=min(limit, 1000))
    return jsonify({
        'success': True,
        'count': len(readings),
        'data': readings
    })


@app.route('/api/history/<int:hours>')
def api_history(hours):
    """Get readings from the last N hours"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    readings = db.get_readings_by_timerange(
        start_time.isoformat() + 'Z',
        end_time.isoformat() + 'Z',
        device_id=config.DEVICE_ID
    )
    
    return jsonify({
        'success': True,
        'count': len(readings),
        'data': readings
    })


@app.route('/api/range/<start_date>/<end_date>')
def api_date_range(start_date, end_date):
    """Get readings between two dates (ISO format)"""
    try:
        # Validate and parse dates
        start_dt = datetime.fromisoformat(start_date.replace('Z', ''))
        end_dt = datetime.fromisoformat(end_date.replace('Z', ''))
        
        readings = db.get_readings_by_timerange(
            start_dt.isoformat() + 'Z',
            end_dt.isoformat() + 'Z',
            device_id=config.DEVICE_ID
        )
        
        return jsonify({
            'success': True,
            'count': len(readings),
            'data': readings
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': f'Invalid date format: {e}'
        }), 400


@app.route('/api/statistics')
def api_statistics():
    """Get statistics about the sensor data"""
    stats = db.get_statistics(device_id=config.DEVICE_ID)
    return jsonify({
        'success': True,
        'data': stats
    })


@app.route('/api/collect')
def api_collect():
    """Manually trigger data collection"""
    result = collector.collect_and_store(lookback_hours=24)
    return jsonify({
        'success': True,
        'data': result
    })


if __name__ == '__main__':
    print(f"Starting Dragino Dashboard on http://{config.WEB_HOST}:{config.WEB_PORT}")
    app.run(host=config.WEB_HOST, port=config.WEB_PORT, debug=True)
