"""Тесты веб-сервиса. TestClient "притворяется" браузером и шлёт запросы
к API прямо в памяти, без настоящего сервера."""
from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict_returns_species():
    flower = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }
    response = client.post("/predict", json=flower)
    assert response.status_code == 200
    assert response.json()["species"] == "setosa"


def test_predict_rejects_negative_values():
    # Отрицательный размер цветка — ошибка, сервис должен ответить 422
    flower = {
        "sepal_length": -1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }
    response = client.post("/predict", json=flower)
    assert response.status_code == 422


def test_predict_rejects_missing_field():
    response = client.post("/predict", json={"sepal_length": 5.1})
    assert response.status_code == 422
