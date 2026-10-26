FROM python:3.12-slim
WORKDIR /app
COPY requirements-hosted.txt .
RUN pip install --no-cache-dir -r requirements-hosted.txt
COPY home_agent ./home_agent
COPY web ./web
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser
ENV PYTHONUNBUFFERED=1
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 8 --timeout 230 'home_agent.hosted:create_app()'"]
