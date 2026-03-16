"""FastAPI application for the bossa arrangement service."""

import logging
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse

from composer.pipeline import arrange

app = FastAPI(
    title="nineteenseventytwo-composer",
    description="AI-powered bossa jazz arrangement service",
    version="0.1.0",
)

log_level = os.environ.get("LOG_LEVEL", "info").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger(__name__)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/arrange")
async def arrange_endpoint(file: UploadFile = File(...)):
    """Accept a MusicXML piano score and return a bossa arrangement.

    The input should be a .musicxml or .xml file containing a piano score.
    Returns a MusicXML file with the full bossa arrangement.
    """
    # Write uploaded file to temp location
    with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False) as tmp_in:
        content = await file.read()
        tmp_in.write(content)
        input_path = Path(tmp_in.name)

    try:
        output_path = input_path.with_name("arranged_" + input_path.name)
        await arrange(input_path, output_path)

        return FileResponse(
            path=str(output_path),
            media_type="application/xml",
            filename="arrangement.musicxml",
        )
    finally:
        # Clean up input file (output cleaned up by FileResponse or caller)
        input_path.unlink(missing_ok=True)
