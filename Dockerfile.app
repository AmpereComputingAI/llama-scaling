# syntax=docker/dockerfile:1
FROM python:3.10-slim

WORKDIR /workspace

COPY requirements-app.txt .

RUN pip install -r requirements-app.txt

COPY app.py .
COPY static ./static

CMD ["python", "app.py"]
