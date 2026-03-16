"""LLM client for bossa transformations via Ollama API."""

import json
import logging
import os

import httpx

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://llm-server:11434"
DEFAULT_MODEL = "llama3:8b"

BOSSA_SYSTEM_PROMPT = """\
You are an expert jazz arranger specializing in bossa nova. You receive a JSON \
representation of a musical arrangement with melody, harmony, and bass parts.

Your task is to transform each part to bossa nova style:

**Bass**: Convert to bossa bass pattern. Use root-fifth movement with syncopation. \
Typical pattern: root on beat 1, fifth on the and-of-2, with occasional chromatic \
approach notes. Keep it simple and grooving.

**Harmony**: Apply bossa voicings. Use rootless voicings (drop the root since bass \
has it). Add 9ths, 7ths, and 13ths where appropriate. Keep voicings in the middle \
register. Use the classic bossa comping rhythm (syncopated, anticipating beats).

**Melody**: Keep the original melody mostly intact but add bossa phrasing. This means \
slight rhythmic displacement (anticipations), occasional grace notes, and breath marks. \
The melody should feel relaxed and behind the beat.

IMPORTANT: Return ONLY valid JSON in the exact same format as the input. \
Do not add any text before or after the JSON. Preserve the metadata section unchanged.\
"""


class LLMClient:
    """Client for communicating with the Ollama LLM server."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
    ):
        self.base_url = base_url or os.environ.get("LLM_BASE_URL", DEFAULT_BASE_URL)
        self.model = model or os.environ.get("LLM_MODEL", DEFAULT_MODEL)

    async def transform_to_bossa(self, ir: dict) -> dict:
        """Send intermediate representation to LLM for bossa transformation.

        Args:
            ir: Intermediate representation dict from musicxml_tools.

        Returns:
            Transformed intermediate representation dict.
        """
        prompt = (
            "Transform this arrangement to bossa nova style. "
            "Return ONLY the transformed JSON:\n\n"
            + json.dumps(ir, indent=2)
        )

        try:
            response = await self._chat(prompt)
            transformed = json.loads(response)

            # Validate structure
            if "parts" not in transformed or "metadata" not in transformed:
                logger.warning("LLM response missing required keys, using original")
                return ir

            return transformed

        except (httpx.HTTPError, json.JSONDecodeError) as e:
            logger.error("LLM transformation failed: %s", e)
            logger.info("Falling back to original arrangement (no bossa transformation)")
            return ir

    async def _chat(self, prompt: str) -> str:
        """Send a chat request to Ollama.

        Args:
            prompt: The user prompt.

        Returns:
            The model's response text.
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": BOSSA_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 4096,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
