# Используем официальный Python-образ
FROM python:3.13

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip

RUN pip install --upgrade setuptools
RUN pip install cachetools
RUN pip install djoser

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Собираем статику
RUN python manage.py collectstatic --noinput

# Указываем команду для запуска приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
