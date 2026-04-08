# Works on both ARM64 (Oracle Cloud) and x86_64 (local dev)
FROM python:3.12-slim

WORKDIR /app

# System dependencies for ML libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Persistent data directory (mount a volume here)
RUN mkdir -p /app/data

# Prevent XGBoost/OpenMP crashes
ENV OMP_NUM_THREADS=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "30"]
