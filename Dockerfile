FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
ENV PYTHONUNBUFFERED=1

CMD gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT app.main:app
