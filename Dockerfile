FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Botni backgroundda, serverni foregroundda ishga tushirish
CMD ["sh", "-c", "python server/bot/telegram_bot.py & uvicorn server.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
