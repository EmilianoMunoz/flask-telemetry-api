import os


class BaseConfig:
    DEBUG = False
    TESTING = False
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    SERVICE_NAME = os.getenv("SERVICE_NAME", "flask-telemetry-api")
    SERVICE_NAMESPACE = os.getenv("SERVICE_NAMESPACE", "portfolio")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    TESTING = True
    LOG_LEVEL = "WARNING"


CONFIGURATIONS = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(name: str) -> type[BaseConfig]:
    """Devuelve una configuración conocida o la de desarrollo por defecto."""
    return CONFIGURATIONS.get(name.lower(), DevelopmentConfig)


__all__ = [
    "BaseConfig",
    "DevelopmentConfig",
    "ProductionConfig",
    "TestingConfig",
    "get_config",
]
