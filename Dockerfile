FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

RUN python -m pip install --no-cache-dir --upgrade pip

ENTRYPOINT ["python", "-m", "mini_torrent.cli"]
