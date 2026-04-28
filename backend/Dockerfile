FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    libsndfile1-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download MIT KEMAR HRTF dataset (large pinna, SOFA format)
RUN mkdir -p data/hrtf && \
    python -c "\
import urllib.request, ssl, os; \
ctx = ssl.create_default_context(); \
ctx.check_hostname = False; \
ctx.verify_mode = ssl.CERT_NONE; \
urllib.request.urlretrieve( \
    'https://sofacoustics.org/data/database/mit/MIT_KEMAR_large_pinna.sofa', \
    'data/hrtf/MIT_KEMAR.sofa', \
)" || echo "HRTF download skipped — mount manually"

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
