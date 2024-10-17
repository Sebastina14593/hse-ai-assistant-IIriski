# Используем официальный образ Python в качестве базового
FROM python:3.11-slim

# Устанавливаем рабочую директорию
RUN mkdir code
WORKDIR code

ADD . /code/
ADD .env.docker /code/.env

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Указываем команду для запуска API сервера
CMD ["python", "main.py"]