# NanoMech - Dockerfile
# Created for Gemini Live Agent Challenge 2026

FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY nanomech.py .
COPY .env.example .

# Run
CMD ["python", "nanomech.py"]
