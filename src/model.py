"""Всё, что связано с моделью машинного обучения.

Модель решает классическую научную задачу: по четырём измерениям цветка
(длина и ширина чашелистика, длина и ширина лепестка) определить,
к какому из трёх видов ириса он относится.
"""
from pathlib import Path

import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Фиксированное "зерно" случайности. Благодаря ему разбиение данных и обучение
# каждый раз дают один и тот же результат — это и есть воспроизводимость.
RANDOM_STATE = 42

# Куда сохраняется обученная модель (папка models/ в корне проекта)
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "iris_model.joblib"

# Порядок признаков, который ожидает модель
FEATURE_NAMES = ["sepal_length", "sepal_width", "petal_length", "petal_width"]

# Названия классов: 0 -> setosa, 1 -> versicolor, 2 -> virginica
SPECIES = ["setosa", "versicolor", "virginica"]


def load_data():
    """Загружает датасет Iris (150 цветков). Он встроен в scikit-learn,
    поэтому интернет не нужен."""
    iris = load_iris()
    return iris.data, iris.target


def build_model():
    """Создаёт модель: нормализация признаков + логистическая регрессия."""
    return Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(max_iter=200, random_state=RANDOM_STATE)),
    ])


def train_and_evaluate():
    """Обучает модель на 80% данных и проверяет точность на оставшихся 20%.

    Возвращает (обученная модель, точность на тестовой выборке).
    """
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    model = build_model()
    model.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, model.predict(X_test))
    return model, accuracy


def save_model(model, path=MODEL_PATH):
    """Сохраняет обученную модель в файл."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    return path


def load_model(path=MODEL_PATH):
    """Загружает модель из файла. Если файла нет — обучает и сохраняет."""
    path = Path(path)
    if not path.exists():
        model, _ = train_and_evaluate()
        save_model(model, path)
        return model
    return joblib.load(path)


def predict(model, features):
    """Предсказывает вид ириса для одного цветка.

    features — список из 4 чисел в порядке FEATURE_NAMES.
    Возвращает словарь: номер класса, название вида и вероятности.
    """
    probabilities = model.predict_proba([features])[0]
    class_id = int(probabilities.argmin())
    return {
        "class_id": class_id,
        "species": SPECIES[class_id],
        "probabilities": {
            name: round(float(p), 4) for name, p in zip(SPECIES, probabilities)
        },
    }
