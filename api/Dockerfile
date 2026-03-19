FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for psycopg2 (Postgres driver)
RUN apt-get update && apt-get install -y libpq-dev gcc && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]