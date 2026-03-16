# musicxml-tools

Core Python library for MusicXML parsing, voice splitting, and score assembly.

## Purpose

Handles all rule-based music processing:

- Parse MusicXML piano scores
- Split voices from a piano part (top → sax, bottom → bass, middle → harmony)
- Convert between MusicXML and a compact intermediate representation for LLM processing
- Assemble multi-part scores from individual parts
- Validate MusicXML output

## Intermediate Representation

MusicXML is too verbose for LLMs. This library converts to/from a compact format:

```json
{
  "metadata": {"title": "...", "tempo": 120, "time_signature": "4/4", "key": "C"},
  "parts": {
    "melody": [
      {"pitch": "C5", "duration": 1.0, "offset": 0.0},
      {"pitch": "E5", "duration": 0.5, "offset": 1.0}
    ],
    "harmony": [
      {"pitches": ["E4", "G4", "B4"], "duration": 2.0, "offset": 0.0}
    ],
    "bass": [
      {"pitch": "C3", "duration": 1.0, "offset": 0.0}
    ]
  }
}
```

## Usage

```python
from musicxml_tools import parse_score, split_voices, to_intermediate, from_intermediate, assemble_score

# Parse a piano score
score = parse_score("input.musicxml")

# Split into parts
parts = split_voices(score)
# parts.melody  — top treble voice
# parts.harmony — middle voices
# parts.bass    — bottom voice

# Convert to intermediate repr for LLM
ir = to_intermediate(parts)

# ... LLM transforms the IR ...

# Convert back and assemble
transformed_parts = from_intermediate(transformed_ir)
output_score = assemble_score(transformed_parts, drums=drum_part)

# Write output
output_score.write("musicxml", "output.musicxml")
```

## Development

```bash
cd services/musicxml-tools
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```
