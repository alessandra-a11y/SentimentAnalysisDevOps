from fastapi.testclient import TestClient

import progetto

client = TestClient(progetto.app)


def test_metrics_endpoint():
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

    assert "api_requests_total" in response.text
    assert "api_request_duration_seconds" in response.text
    assert "sentiment_predictions_total" in response.text


def test_requests_are_recorded():
    # La GET su /predict restituisce 405
    client.get("/predict")

    response = client.get("/metrics")

    assert response.status_code == 200

    assert 'status_code="405"' in response.text
    assert 'endpoint="/predict"' in response.text