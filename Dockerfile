FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y \
    tesseract-ocr tesseract-ocr-por tesseract-ocr-eng \
    libjpeg-dev libpng-dev libtiff-dev libfreetype6-dev \
    libglib2.0-0 libgomp1 wget curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml ./
COPY uv.lock* ./
RUN pip install uv
RUN uv pip install --system --requirement pyproject.toml
COPY src/ ./src/
COPY main.py ./main.py
COPY README.md ./
RUN mkdir -p /tmp/uploads

ENV TESSERACT_PATH=/usr/bin/tesseract \
    MONGODB_URL=mongodb://mongodb:27017 \
    DATABASE_NAME=curriculum_analyzer \
    HOST=0.0.0.0 \
    PORT=8000 \
    PYTHONPATH=/app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1
CMD ["python", "main.py"]