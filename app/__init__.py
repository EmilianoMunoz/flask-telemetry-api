import logging
import os

from dotenv import load_dotenv
from flask import Flask

from app.config import get_config
from app.observability import configure_telemetry
from app.resources.health import health_bp
from app.resources.home import home_bp


def create_app(config_name: str | None = None) -> Flask:
    """Crea la aplicación y aplica la configuración del entorno."""
    load_dotenv()

    app = Flask(__name__)
    environment = config_name or os.getenv("FLASK_CONTEXT", "development")
    app.config.from_object(get_config(environment))

    logging.basicConfig(
        level=app.config["LOG_LEVEL"],
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    app.register_blueprint(home_bp)
    app.register_blueprint(health_bp, url_prefix="/health")

    app.extensions["telemetry_enabled"] = configure_telemetry(app)
    logging.getLogger(__name__).info(
        "Aplicación iniciada en modo %s; telemetría=%s",
        environment,
        app.extensions["telemetry_enabled"],
    )

    return app


__all__ = ["create_app"]
