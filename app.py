"""Flask application factory and WSGI entrypoint."""
from datetime import datetime, timedelta

from flask import Flask, jsonify, render_template
from flask_migrate import Migrate

import config
from collector import SensorDataCollector
from database import SensorDatabase, db


migrate = Migrate()


def create_app() -> Flask:
	"""Create and configure the Flask app instance."""
	app = Flask(__name__, template_folder="templates")
	app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URL
	app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

	db.init_app(app)
	migrate.init_app(app, db, directory="alembic")

	sensor_database = SensorDatabase(app=app)
	collector = SensorDataCollector(database=sensor_database)

	@app.route("/")
	def index():
		"""Main dashboard page."""
		return render_template("index.html")

	@app.route("/api/current")
	def api_current():
		"""Get the current/latest sensor reading."""
		reading = collector.get_current_temperature(config.DEVICE_ID)
		if reading:
			return jsonify({
				"success": True,
				"data": reading,
			})
		return jsonify({
			"success": False,
			"message": "No data available",
		}), 404

	@app.route("/api/latest/<int:limit>")
	def api_latest(limit):
		"""Get the latest N readings."""
		readings = sensor_database.get_latest_readings(device_id=config.DEVICE_ID, limit=min(limit, 1000))
		return jsonify({
			"success": True,
			"count": len(readings),
			"data": readings,
		})

	@app.route("/api/history/<int:hours>")
	def api_history(hours):
		"""Get readings from the last N hours."""
		end_time = datetime.utcnow()
		start_time = end_time - timedelta(hours=hours)

		readings = sensor_database.get_readings_by_timerange(
			start_time.isoformat() + "Z",
			end_time.isoformat() + "Z",
			device_id=config.DEVICE_ID,
		)

		return jsonify({
			"success": True,
			"count": len(readings),
			"data": readings,
		})

	@app.route("/api/range/<start_date>/<end_date>")
	def api_date_range(start_date, end_date):
		"""Get readings between two dates (ISO format)."""
		try:
			start_dt = datetime.fromisoformat(start_date.replace("Z", ""))
			end_dt = datetime.fromisoformat(end_date.replace("Z", ""))

			readings = sensor_database.get_readings_by_timerange(
				start_dt.isoformat() + "Z",
				end_dt.isoformat() + "Z",
				device_id=config.DEVICE_ID,
			)

			return jsonify({
				"success": True,
				"count": len(readings),
				"data": readings,
			})
		except ValueError as error:
			return jsonify({
				"success": False,
				"message": f"Invalid date format: {error}",
			}), 400

	@app.route("/api/statistics")
	def api_statistics():
		"""Get statistics about the sensor data."""
		stats = sensor_database.get_statistics(device_id=config.DEVICE_ID)
		return jsonify({
			"success": True,
			"data": stats,
		})

	@app.route("/api/collect")
	def api_collect():
		"""Manually trigger data collection."""
		result = collector.collect_and_store(lookback_hours=24)
		return jsonify({
			"success": True,
			"data": result,
		})

	return app


app = create_app()


if __name__ == "__main__":
	app.run(host=config.WEB_HOST, port=config.WEB_PORT, debug=True)
