<img width="955" height="939" alt="image" src="https://github.com/user-attachments/assets/c26d1b00-9136-4939-9340-9915cf90ddc2" /># Iris Classifier — CI/CD для исследовательского Python-проекта

Учебный проект: модель машинного обучения, которая определяет вид ириса
(setosa, versicolor, virginica) по четырём измерениям цветка, и REST API
для обращения к ней.

## Структура

```
iris-ci-cd/
├── src/
│   ├── model.py      # загрузка данных, обучение, сохранение, предсказание
│   ├── train.py      # скрипт обучения модели
│   └── api.py        # веб-сервис на FastAPI
├── tests/
│   ├── test_model.py # тесты модели
│   └── test_api.py   # тесты API
├── requirements.txt      # библиотеки приложения
└── requirements-dev.txt  # библиотеки для разработки и тестов
```

## Локальный запуск (Windows, PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

python -m src.train        # обучить модель
pytest                     # запустить тесты
flake8                     # проверить стиль кода
uvicorn src.api:app --reload   # запустить API
```

Документация API: http://127.0.0.1:8000/docs

## Эндпоинты

| Метод | Путь       | Описание                          |
|-------|------------|-----------------------------------|
| GET   | `/`        | Приветствие                       |
| GET   | `/health`  | Проверка состояния сервиса        |
| POST  | `/predict` | Предсказание вида ириса           |

Пример запроса к `/predict`:

```json
{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}
```
Автор: Куаншпек Жансая

   ## CI/CD

   Каждый коммит автоматически проверяется в Jenkins: линтер, unit-тесты,
   сборка Docker-образа и smoke-тест контейнера.
