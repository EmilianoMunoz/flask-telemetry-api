import logging
import os

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from flask import Flask
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = logging.getLogger(__name__)


def configure_telemetry(app: Flask) -> bool:
    """Instrumenta Flask y exporta trazas cuando Azure Monitor está configurado."""
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not connection_string:
        logger.info("Telemetría remota desactivada: falta la cadena de Azure Monitor")
        return False

    try:
        resource = Resource.create(
            {
                "service.name": app.config["SERVICE_NAME"],
                "service.namespace": app.config["SERVICE_NAMESPACE"],
                "service.instance.id": os.getenv("HOSTNAME", "local"),
            }
        )
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(
            BatchSpanProcessor(
                AzureMonitorTraceExporter(connection_string=connection_string)
            )
        )
        trace.set_tracer_provider(provider)
        FlaskInstrumentor().instrument_app(app)
        logger.info("Trazas OpenTelemetry habilitadas para Azure Monitor")
        return True
    except Exception:
        logger.exception("No fue posible inicializar la telemetría")
        return False
