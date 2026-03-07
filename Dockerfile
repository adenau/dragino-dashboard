FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/instance

ENV DRAGINO_ENV=prod
ENV DRAGINO_WEB_PORT=5000
ENV FLASK_APP=app.py

EXPOSE 5000

CMD ["sh", "-c", "flask db upgrade && gunicorn -c gunicorn.conf.py --bind 0.0.0.0:${DRAGINO_WEB_PORT:-5000} --workers 2 --threads 4 --timeout 120 app:app"]
