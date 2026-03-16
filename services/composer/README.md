# composer

FastAPI service that orchestrates the bossa arrangement pipeline.

## Purpose

Takes a piano MusicXML as input and outputs a full bossa jazz arrangement with:
- Alto Sax melody
- Piano harmony with bossa voicing
- Bass line in bossa style
- Bossa drum track

## API

### POST /arrange

Upload a MusicXML file and receive an arranged MusicXML back.

```bash
curl -X POST http://localhost:8000/arrange \
  -F "file=@input.musicxml" \
  -o output.musicxml
```

### GET /health

Health check endpoint.

## Configuration

Environment variables:

| Variable | Default | Description |
|---|---|---|
| `LLM_BASE_URL` | `http://llm-server:11434` | Ollama API base URL |
| `LLM_MODEL` | `llama3:8b` | Model to use for transformations |
| `LOG_LEVEL` | `info` | Logging level |

## Development

```bash
cd services/composer
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn composer.app:app --reload
```
