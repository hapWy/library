FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# скрипт должен быть исполняемым
RUN chmod +x /app/start.sh

CMD ["./start.sh"]
