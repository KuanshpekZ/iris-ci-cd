"""Unit-тесты модели. Каждая функция test_* — одна проверка."""
from src.model import (
    SPECIES,
    load_data,
    load_model,
    predict,
    save_model,
    train_and_evaluate,
)


def test_dataset_has_150_samples_and_4_features():
    X, y = load_data()
    assert X.shape == (150, 4)
    assert len(y) == 150


def test_model_accuracy_is_high_enough():
    # Если кто-то "сломает" модель, точность упадёт и тест не пройдёт
    _, accuracy = train_and_evaluate()
    assert accuracy >= 0.9


def test_training_is_reproducible():
    # Два обучения подряд должны дать одинаковый результат
    _, accuracy_1 = train_and_evaluate()
    _, accuracy_2 = train_and_evaluate()
    assert accuracy_1 == accuracy_2


def test_predict_setosa():
    # Типичный цветок вида setosa из датасета
    model, _ = train_and_evaluate()
    result = predict(model, [5.1, 3.5, 1.4, 0.2])
    assert result["species"] == "setosa"
    assert result["class_id"] == 0


def test_predict_virginica():
    model, _ = train_and_evaluate()
    result = predict(model, [6.7, 3.0, 5.8, 2.2])
    assert result["species"] == "virginica"


def test_probabilities_sum_to_one():
    model, _ = train_and_evaluate()
    result = predict(model, [5.9, 3.0, 4.2, 1.5])
    assert set(result["probabilities"]) == set(SPECIES)
    assert abs(sum(result["probabilities"].values()) - 1.0) < 0.01


def test_save_and_load_model(tmp_path):
    # tmp_path — временная папка, которую pytest создаёт для теста
    model, _ = train_and_evaluate()
    path = save_model(model, tmp_path / "model.joblib")
    loaded = load_model(path)
    sample = [6.3, 2.8, 5.1, 1.5]
    assert predict(loaded, sample) == predict(model, sample)
