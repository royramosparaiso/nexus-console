FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl docker.io \
    && rm -rf /var/lib/apt/lists/*

# nexus-core is expected to be checked out into ./vendor/nexus-core by CI.
# Local `docker compose build` can do the same:
#   git -C vendor/nexus-core pull || git clone https://github.com/royramosparaiso/nexus-core vendor/nexus-core
COPY vendor/nexus-core /nexus-core
RUN pip install --no-cache-dir -e /nexus-core/python

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -e .

COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./

EXPOSE 7000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7000"]
