"""Smoke-тест запущенного контейнера: проверяет /health и /predict.

Скрипт выполняется ВНУТРИ контейнера, Jenkins передаёт его так:
    docker exec -i <контейнер> python - < scripts/smoke_test.py
"""
import json
import sys
import urllib.request

BASE_URL = "http://127.0.0.1:8000"


def get(path):
    with urllib.request.urlopen(BASE_URL + path, timeout=5) as response:
        return json.load(response)


def post(path, payload):
    request = urllib.request.Request(
        BASE_URL + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.load(response)


def main():
    health = get("/health")
    print("GET /health ->", health)
    assert health["status"] == "ok", "сервис нездоров"

    flower = {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}
    result = post("/predict", flower)
    print("POST /predict ->", result)
    assert result["species"] == "setosa", "неверное предсказание"

    print("Smoke-тест пройден: контейнер работает корректно")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("Smoke-тест провален:", error)
        sys.exit(1)
