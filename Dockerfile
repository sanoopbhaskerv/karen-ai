FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/data && useradd -m karen && chown -R karen:karen /app
USER karen
ENV PORT=8080 MEMORY_PATH=/app/data/memory.txt
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "4", "--timeout", "150", "app:create_app()"]
