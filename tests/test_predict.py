from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import progetto


client = TestClient(progetto.app)


def test_predict_success(monkeypatch):
    mock_model = MagicMock()

    mock_model.predict.return_value = ["positive"]
    mock_model.predict_proba.return_value = [[0.05, 0.95]]

    monkeypatch.setattr(progetto, "model", mock_model)

    response = client.post(
        "/predict",
        json={"review": "This product is amazing!"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["sentiment"] == "positive"
    assert data["confidence"] == 0.95

    mock_model.predict.assert_called_once_with(
        ["This product is amazing!"]
    )


def test_predict_negative(monkeypatch):
    mock_model = MagicMock()

    mock_model.predict.return_value = ["negative"]
    mock_model.predict_proba.return_value = [[0.90, 0.10]]

    monkeypatch.setattr(progetto, "model", mock_model)

    response = client.post(
        "/predict",
        json={"review": "Terrible product!"}
    )

    assert response.status_code == 200
    assert response.json()["sentiment"] == "negative"
    assert response.json()["confidence"] == 0.90


def test_predict_empty_review():
    response = client.post(
        "/predict",
        json={"review": ""}
    )

    assert response.status_code == 400


def test_predict_missing_review():
    response = client.post(
        "/predict",
        json={}
    )

    assert response.status_code == 422


def test_predict_invalid_type():
    response = client.post(
        "/predict",
        json={"review": 123}
    )

    assert response.status_code == 422


def test_predict_wrong_method():
    response = client.get("/predict")

    assert response.status_code == 405


def test_predict_model_error(monkeypatch):
    mock_model = MagicMock()

    mock_model.predict.side_effect = RuntimeError(
        "Errore simulato del modello"
    )

    monkeypatch.setattr(progetto, "model", mock_model)

    response = client.post(
        "/predict",
        json={"review": "This is a test"}
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Non è possibile identificare il sentiment della recensione"
    )


def test_predict_real_model():
    # In questo test NON utilizziamo mock:
    # viene interrogato il modello pickle originale.

    response = client.post(
        "/predict",
        json={"review": "This product is amazing! I love it."}
    )

    assert response.status_code == 200

    data = response.json()

    assert set(data.keys()) == {"sentiment", "confidence"}
    assert data["sentiment"] in {"positive", "negative", "neutral"}
    assert isinstance(data["confidence"], float)
    assert 0.0 <= data["confidence"] <= 1.0