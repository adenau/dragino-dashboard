"""Configuration for the Dragino Temperature Sensor Dashboard."""

import os

from dotenv import load_dotenv


load_dotenv()


def _get_int(name: str, default: int) -> int:
	value = os.getenv(name)
	if value is None:
		return default
	try:
		return int(value)
	except ValueError:
		return default


def _get_bool(name: str, default: bool) -> bool:
	value = os.getenv(name)
	if value is None:
		return default
	return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_choice(name: str, default: str, allowed: set[str]) -> str:
	value = os.getenv(name, default).strip().lower()
	if value not in allowed:
		allowed_values = ", ".join(sorted(allowed))
		raise ValueError(f"Invalid value for {name}: '{value}'. Allowed values: {allowed_values}")
	return value


def _get_database_url() -> str:
	explicit_database_url = os.getenv("DRAGINO_DATABASE_URL")
	if explicit_database_url:
		return explicit_database_url

	if DATABASE_BACKEND == "mysql":
		mysql_host = os.getenv("DRAGINO_MYSQL_HOST", "localhost")
		mysql_port = _get_int("DRAGINO_MYSQL_PORT", 3306)
		mysql_database = os.getenv("DRAGINO_MYSQL_DATABASE", "dragino_dashboard")
		mysql_user = os.getenv("DRAGINO_MYSQL_USER", "dragino")
		mysql_password = os.getenv("DRAGINO_MYSQL_PASSWORD", "")
		return (
			f"mysql+pymysql://{mysql_user}:{mysql_password}"
			f"@{mysql_host}:{mysql_port}/{mysql_database}"
		)

	database_path = os.getenv("DRAGINO_DATABASE_PATH", "sensor_data.db")
	return f"sqlite:///{database_path}"


# API Configuration
API_URL = os.getenv(
	"DRAGINO_API_URL",
	"https://nam1.cloud.thethings.network/api/v3/as/applications/technodabbler-exploration/packages/storage/uplink_message",
)
API_TOKEN = os.getenv("DRAGINO_API_TOKEN", "")
DEVICE_ID = os.getenv("DRAGINO_DEVICE_ID", "temp-sensor-001")

# Database Configuration
APP_ENV = _get_choice("DRAGINO_ENV", "dev", {"dev", "prod"})
DATABASE_BACKEND = _get_choice(
	"DRAGINO_DATABASE_BACKEND",
	"sqlite" if APP_ENV == "dev" else "mysql",
	{"sqlite", "mysql"},
)
DATABASE_PATH = os.getenv("DRAGINO_DATABASE_PATH", "sensor_data.db")
DATABASE_URL = _get_database_url()

# Web Server Configuration
WEB_HOST = os.getenv("DRAGINO_WEB_HOST", "0.0.0.0")
WEB_PORT = _get_int("DRAGINO_WEB_PORT", 5000)

# Data Collection Configuration
COLLECTION_INTERVAL = _get_int("DRAGINO_COLLECTION_INTERVAL", 15 * 60)
LOOKBACK_HOURS = _get_int("DRAGINO_LOOKBACK_HOURS", 192)
ENABLE_BACKGROUND_COLLECTOR = _get_bool("DRAGINO_ENABLE_BACKGROUND_COLLECTOR", True)
