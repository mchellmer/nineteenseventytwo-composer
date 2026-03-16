FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml version.txt ./
COPY src/ src/

RUN pip install --no-cache-dir .

COPY . .

ENTRYPOINT ["python", "-m", "musicxml_tools"]
