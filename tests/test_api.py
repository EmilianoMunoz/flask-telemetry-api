def test_index_describes_service(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json()["status"] == "available"
    assert response.get_json()["documentation"]["liveness"] == "/health/live"


def test_liveness_is_independent_from_database(client):
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_readiness_fails_without_database_configuration(client, monkeypatch):
    variables = (
        "AZURE_POSTGRESQL_HOST",
        "AZURE_POSTGRESQL_DB",
        "AZURE_POSTGRESQL_USER",
        "AZURE_POSTGRESQL_PASSWORD",
    )
    for variable in variables:
        monkeypatch.delenv(variable, raising=False)

    response = client.get("/health/ready")

    assert response.status_code == 503
    payload = response.get_json()
    assert payload["status"] == "unhealthy"
    assert payload["checks"]["database"]["reason"] == "database_not_configured"


def test_system_endpoint_returns_operational_metrics(client):
    response = client.get("/health/system")

    assert response.status_code == 200
    metrics = response.get_json()["metrics"]
    assert "process_memory_mb" in metrics
    assert "system_cpu_percent" in metrics
