"""Веб-сервис (REST API), через который модель доступна по сети.

Запуск из корня проекта:
    uvicorn src.api:app --reload
После запуска откройте в браузере http://127.0.0.1:8000/docs
"""
import os
from functools import lru_cache

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.model import load_model, predict

# Версия приложения. Позже Jenkins будет подставлять сюда номер сборки.
APP_VERSION = os.getenv("APP_VERSION", "dev")

app = FastAPI(
    title="Iris Classifier API",
    description="Определяет вид ириса по размерам цветка.",
    version=APP_VERSION,
)


class IrisFeatures(BaseModel):
    """Входные данные: 4 измерения цветка в сантиметрах.
    gt=0 означает "больше нуля", le=20 — "не больше 20"."""
    sepal_length: float = Field(..., gt=0, le=20, examples=[5.1])
    sepal_width: float = Field(..., gt=0, le=20, examples=[3.5])
    petal_length: float = Field(..., gt=0, le=20, examples=[1.4])
    petal_width: float = Field(..., gt=0, le=20, examples=[0.2])


@lru_cache
def get_model():
    """Загружает модель один раз и дальше берёт её из памяти."""
    return load_model()


@app.get("/")
def root():
    return {"message": "Iris Classifier API. Документация: /docs"}


@app.get("/health")
def health():
    """Проверка "жив ли сервис". Её используют Docker, Jenkins и Kubernetes."""
    return {"status": "ok", "version": APP_VERSION}


@app.post("/predict")
def predict_species(features: IrisFeatures):
    """Принимает размеры цветка и возвращает предсказанный вид."""
    values = [
        features.sepal_length,
        features.sepal_width,
        features.petal_length,
        features.petal_width,
    ]
    return predict(get_model(), values)
