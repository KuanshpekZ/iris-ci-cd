"""Скрипт обучения модели.

Запуск из корня проекта:
    python -m src.train
"""
from src.model import save_model, train_and_evaluate


def main():
    model, accuracy = train_and_evaluate()
    path = save_model(model)
    print(f"Точность модели на тестовой выборке: {accuracy:.3f}")
    print(f"Модель сохранена в файл: {path}")


if __name__ == "__main__":
    main()
