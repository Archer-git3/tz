# Используем официальный образ Python как базовый
FROM python:3.9-slim

# Установка рабочего каталога в контейнере
WORKDIR /usr/src/app

# Копирование файла зависимостей в рабочий каталог
COPY requirements.txt ./

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование остальных файлов проекта в контейнер
COPY . .

# Команда для запуска приложения
CMD ["python", "./app.py"]
