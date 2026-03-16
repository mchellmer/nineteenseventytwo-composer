FROM python:3.12-slim

WORKDIR /app

# Install musicxml-tools first (build context is services/)
COPY musicxml-tools/ /tmp/musicxml-tools
RUN pip install --no-cache-dir /tmp/musicxml-tools && rm -rf /tmp/musicxml-tools

COPY composer/pyproject.toml composer/version.txt ./
COPY composer/src/ src/

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "composer.app:app", "--host", "0.0.0.0", "--port", "8000"]
