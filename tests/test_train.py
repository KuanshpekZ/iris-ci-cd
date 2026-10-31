"""Тест скрипта обучения src/train.py."""
from src import model, train


def test_train_script_saves_model(tmp_path, monkeypatch, capsys):
    target = tmp_path / "model.joblib"
    # Подменяем путь сохранения, чтобы тест не трогал настоящую папку models/
    monkeypatch.setattr(train, "save_model", lambda m: model.save_model(m, target))

    train.main()

    assert target.exists()
    assert "Точность модели" in capsys.readouterr().out
