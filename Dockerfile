FROM python:3.11-slim

WORKDIR /app

# Kutubxonalarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kodni nusxalash
COPY . .

# Serverni ishga tushirish
CMD ["uvicorn", "server.app.main:app", "--host", "0.0.0.0", "--port", "10000"]
