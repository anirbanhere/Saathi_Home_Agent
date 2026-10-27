FROM python:3.12-slim
WORKDIR /app
COPY requirements-saathi.txt requirements-saathi.lock.txt ./
RUN pip install --no-cache-dir -r requirements-saathi.txt
COPY saathi ./saathi
COPY saathi_web ./saathi_web
COPY config ./config
COPY alembic-saathi.ini ./
RUN useradd --create-home saathi && mkdir data && chown saathi:saathi data
USER saathi
# Use only the compose profile's loopback-published port. No public ingress.
CMD ["uvicorn", "saathi.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8781"]
