import os
import platform
import time
from datetime import UTC, datetime

import psutil
import psycopg2
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


def utc_timestamp() -> str:
    return datetime.now(UTC).isoformat()


def database_config() -> tuple[dict[str, str | None], list[str]]:
    config = {
        "host": os.getenv("AZURE_POSTGRESQL_HOST"),
        "dbname": os.getenv("AZURE_POSTGRESQL_DB"),
        "user": os.getenv("AZURE_POSTGRESQL_USER"),
        "password": os.getenv("AZURE_POSTGRESQL_PASSWORD"),
        "port": os.getenv("AZURE_POSTGRESQL_PORT", "5432"),
    }
    missing = [key for key, value in config.items() if not value]
    return config, missing


def check_database() -> dict:
    """Ejecuta una consulta de solo lectura y no expone datos de conexión."""
    config, missing = database_config()
    if missing:
        return {
            "status": "unhealthy",
            "reason": "database_not_configured",
            "missing_variables": missing,
        }

    started_at = time.perf_counter()
    try:
        with psycopg2.connect(**config, connect_timeout=3) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        return {
            "status": "healthy",
            "latency_ms": round((time.perf_counter() - started_at) * 1000, 2),
        }
    except psycopg2.Error:
        return {"status": "unhealthy", "reason": "database_unreachable"}


def system_metrics() -> dict:
    process = psutil.Process()
    memory = psutil.virtual_memory()
    return {
        "process_cpu_percent": process.cpu_percent(interval=None),
        "process_memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
        "system_cpu_percent": psutil.cpu_percent(interval=None),
        "system_memory_percent": memory.percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "cpu_count": psutil.cpu_count(),
        "platform": platform.system(),
        "uptime_seconds": round(time.time() - process.create_time(), 2),
    }


@health_bp.get("/live")
def liveness():
    """Indica si el proceso HTTP está disponible."""
    return jsonify({"status": "healthy", "timestamp": utc_timestamp()})


@health_bp.get("/ready")
def readiness():
    """Indica si la aplicación puede atender tráfico con sus dependencias."""
    database = check_database()
    status = "healthy" if database["status"] == "healthy" else "unhealthy"
    return (
        jsonify(
            {
                "status": status,
                "timestamp": utc_timestamp(),
                "checks": {"database": database},
            }
        ),
        200 if status == "healthy" else 503,
    )


@health_bp.get("/system")
def system():
    """Expone métricas operativas básicas del contenedor."""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": utc_timestamp(),
            "metrics": system_metrics(),
        }
    )
