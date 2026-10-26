FROM mcr.microsoft.com/playwright/python:v1.64.1-noble
WORKDIR /app
COPY requirements-browser.txt .
RUN pip install --no-cache-dir -r requirements-browser.txt
COPY home_agent ./home_agent
USER pwuser
ENV PYTHONUNBUFFERED=1
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 1 --timeout 110 'home_agent.browser_worker:create_worker()'"]
