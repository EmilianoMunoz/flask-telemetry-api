import pytest

from app import create_app


@pytest.fixture()
def client():
    app = create_app("testing")
    return app.test_client()
