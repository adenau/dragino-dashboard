"""create sensor_readings table

Revision ID: 20260305_0001
Revises:
Create Date: 2026-03-05 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "20260305_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "sensor_readings" not in inspector.get_table_names():
        op.create_table(
            "sensor_readings",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("device_id", sa.String(length=255), nullable=False),
            sa.Column("received_at", sa.String(length=64), nullable=False),
            sa.Column("temp_sht", sa.Float(), nullable=True),
            sa.Column("temp_ds", sa.Float(), nullable=True),
            sa.Column("humidity", sa.Float(), nullable=True),
            sa.Column("battery_voltage", sa.Float(), nullable=True),
            sa.Column("battery_status", sa.Integer(), nullable=True),
            sa.Column("f_cnt", sa.Integer(), nullable=True),
            sa.Column("rssi", sa.Integer(), nullable=True),
            sa.Column("snr", sa.Float(), nullable=True),
            sa.Column("raw_data", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint(
                "device_id",
                "received_at",
                "f_cnt",
                name="uq_sensor_readings_device_received_fcnt",
            ),
        )

    inspector = inspect(bind)
    index_names = [idx["name"] for idx in inspector.get_indexes("sensor_readings")]

    if "ix_sensor_readings_device_id" not in index_names:
        op.create_index("ix_sensor_readings_device_id", "sensor_readings", ["device_id"], unique=False)

    inspector = inspect(bind)
    index_names = [idx["name"] for idx in inspector.get_indexes("sensor_readings")]

    if "ix_sensor_readings_received_at" not in index_names:
        op.create_index("ix_sensor_readings_received_at", "sensor_readings", ["received_at"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "sensor_readings" in inspector.get_table_names():
        index_names = [idx["name"] for idx in inspector.get_indexes("sensor_readings")]
        if "ix_sensor_readings_device_id" in index_names:
            op.drop_index("ix_sensor_readings_device_id", table_name="sensor_readings")
        if "ix_sensor_readings_received_at" in index_names:
            op.drop_index("ix_sensor_readings_received_at", table_name="sensor_readings")
        op.drop_table("sensor_readings")
