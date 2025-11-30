#!/bin/sh
echo "Waiting for Postgres..."
until pg_isready -h db -p 5432 -U postgres; do
  sleep 2
done

echo "Running migrations..."
alembic revision --autogenerate -m "check"
alembic upgrade head

echo "Starting FastAPI..."
uvicorn main:app --host 0.0.0.0 --port 8000
