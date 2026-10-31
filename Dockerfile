# ---------------------------------------------------------------
# Dockerfile — "рецепт" сборки образа с нашим приложением
# ---------------------------------------------------------------

# 1. Базовый образ: облегчённый Linux (Debian) с уже установленным Python 3.13
FROM python:3.13-slim

# 2. Описание образа (метаданные)
LABEL org.opencontainers.image.title="iris-api" \
      org.opencontainers.image.description="Iris classifier REST API (research CI/CD demo)" \
      org.opencontainers.image.source="https://github.com/KuanshpekZ/iris-ci-cd"

# 3. Настройки Python и pip:
#    - не создавать файлы .pyc
#    - сразу выводить логи (без буферизации)
#    - не хранить кэш pip (образ меньше)
#    - не проверять обновления pip
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 4. Рабочая папка внутри контейнера (все следующие команды выполняются в ней)
WORKDIR /app

# 5. Сначала копируем ТОЛЬКО список библиотек и устанавливаем их.
#    Docker кэширует этот шаг: если requirements.txt не менялся,
#    при следующей сборке библиотеки не будут скачиваться заново.
COPY requirements.txt .
RUN pip install -r requirements.txt

# 6. Теперь копируем код приложения
COPY src/ ./src/

# 7. Обучаем модель прямо во время сборки:
#    готовая модель "запекается" в образ
RUN python -m src.train

# 8. Версия приложения. Её можно передать при сборке:
#    docker build --build-arg APP_VERSION=1.0 ...
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

# 9. Безопасность: запускаем приложение не от администратора (root),
#    а от обычного пользователя appuser
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# 10. Сообщаем, что приложение слушает порт 8000
EXPOSE 8000

# 11. Проверка здоровья: каждые 30 секунд Docker обращается к /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

# 12. Команда, которая выполняется при запуске контейнера
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]