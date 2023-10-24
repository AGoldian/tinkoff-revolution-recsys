# Установка базового образа
FROM python:3.11

# Копирование файлов приложения в контейнер
COPY . /app

# Установка зависимостей
RUN pip install -r /app/requirements.txt

# Определение рабочей директории
WORKDIR /app

# Запуск приложения
CMD ["python", "bot_aio.py"]