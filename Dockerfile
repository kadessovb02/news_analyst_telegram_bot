FROM python:3.10

# Устанавливаем рабочую директорию в контейнере
WORKDIR /code/

# Копируем файлы проекта в текущую директорию (в контейнере)
COPY requirements.txt .

# Устанавливаем необходимые пакеты с помощью pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/

CMD ["python", "./main.py"]
