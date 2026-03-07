"""Database models and data-access helpers for sensor data."""
from contextlib import nullcontext
from datetime import datetime
from typing import Dict, List, Optional

from flask import has_app_context
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, desc, func, select
from sqlalchemy.exc import IntegrityError


db = SQLAlchemy()


class SensorReading(db.Model):
    __tablename__ = "sensor_readings"
    __table_args__ = (
        db.UniqueConstraint(
            "device_id",
            "received_at",
            "f_cnt",
            name="uq_sensor_readings_device_received_fcnt",
        ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(255), nullable=False, index=True)
    received_at = db.Column(db.String(64), nullable=False, index=True)
    temp_sht = db.Column(db.Float, nullable=True)
    temp_ds = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    battery_voltage = db.Column(db.Float, nullable=True)
    battery_status = db.Column(db.Integer, nullable=True)
    f_cnt = db.Column(db.Integer, nullable=True)
    rssi = db.Column(db.Integer, nullable=True)
    snr = db.Column(db.Float, nullable=True)
    raw_data = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> Dict:
        created_at = (
            self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        )
        return {
            "id": self.id,
            "device_id": self.device_id,
            "received_at": self.received_at,
            "temp_sht": self.temp_sht,
            "temp_ds": self.temp_ds,
            "humidity": self.humidity,
            "battery_voltage": self.battery_voltage,
            "battery_status": self.battery_status,
            "f_cnt": self.f_cnt,
            "rssi": self.rssi,
            "snr": self.snr,
            "raw_data": self.raw_data,
            "created_at": created_at,
        }


class SensorDatabase:
    """Handles all database operations for sensor data."""

    def __init__(self, app=None):
        self.app = app

    def _context(self):
        if has_app_context():
            return nullcontext()
        if self.app is None:
            raise RuntimeError("SensorDatabase requires a Flask app context or app instance.")
        return self.app.app_context()

    def init_database(self) -> None:
        """Initialize the database and create tables if they don't exist."""
        with self._context():
            db.create_all()

    def insert_reading(self, reading_data: Dict) -> bool:
        """Insert a sensor reading. Returns True if inserted, False if duplicate."""
        with self._context():
            try:
                reading = SensorReading(
                    device_id=reading_data.get("device_id"),
                    received_at=reading_data.get("received_at"),
                    temp_sht=reading_data.get("temp_sht"),
                    temp_ds=reading_data.get("temp_ds"),
                    humidity=reading_data.get("humidity"),
                    battery_voltage=reading_data.get("battery_voltage"),
                    battery_status=reading_data.get("battery_status"),
                    f_cnt=reading_data.get("f_cnt"),
                    rssi=reading_data.get("rssi"),
                    snr=reading_data.get("snr"),
                    raw_data=reading_data.get("raw_data", ""),
                )
                db.session.add(reading)
                db.session.commit()
                return True
            except IntegrityError:
                db.session.rollback()
                return False

    def get_latest_readings(self, device_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get the latest sensor readings."""
        with self._context():
            query = select(SensorReading)
            if device_id:
                query = query.where(SensorReading.device_id == device_id)

            query = query.order_by(desc(SensorReading.received_at)).limit(limit)
            rows = db.session.execute(query).scalars().all()
            return [row.to_dict() for row in rows]

    def get_readings_by_timerange(
        self,
        start_time: str,
        end_time: str,
        device_id: Optional[str] = None,
    ) -> List[Dict]:
        """Get sensor readings within a time range."""
        with self._context():
            filters = [SensorReading.received_at.between(start_time, end_time)]
            if device_id:
                filters.append(SensorReading.device_id == device_id)

            query = (
                select(SensorReading)
                .where(and_(*filters))
                .order_by(SensorReading.received_at.asc())
            )
            rows = db.session.execute(query).scalars().all()
            return [row.to_dict() for row in rows]

    def get_statistics(self, device_id: Optional[str] = None) -> Dict:
        """Get statistics about stored sensor data."""
        with self._context():
            query = select(
                func.count(SensorReading.id),
                func.min(SensorReading.received_at),
                func.max(SensorReading.received_at),
                func.avg(SensorReading.temp_sht),
                func.min(SensorReading.temp_sht),
                func.max(SensorReading.temp_sht),
                func.avg(SensorReading.humidity),
                func.avg(SensorReading.battery_voltage),
            )

            if device_id:
                query = query.where(SensorReading.device_id == device_id)

            row = db.session.execute(query).one()
            return {
                "total_readings": row[0],
                "first_reading": row[1],
                "last_reading": row[2],
                "avg_temp_sht": round(row[3], 2) if row[3] else None,
                "min_temp_sht": round(row[4], 2) if row[4] else None,
                "max_temp_sht": round(row[5], 2) if row[5] else None,
                "avg_humidity": round(row[6], 2) if row[6] else None,
                "avg_battery": round(row[7], 3) if row[7] else None,
            }
