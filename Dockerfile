FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# create_tables.py ni ishga tushirib, keyin serverni boshlash
CMD ["sh", "-c", "python server/app/create_tables.py && uvicorn server.app.main:app --host 0.0.0.0 --port 8000"]
