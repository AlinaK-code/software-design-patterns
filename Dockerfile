FROM python:3.11-slim

WORKDIR /app 

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# это для скрипта суперпользователя
# COPY ./entrypoint.sh /entrypoint.sh
# RUN chmod +x /entrypoint.sh

EXPOSE 8000 

# при старте контейнера запускаю файлик баш
# ENTRYPOINT ["/entrypoint.sh"]