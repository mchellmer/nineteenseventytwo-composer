"""Tests for the arrangement pipeline (with mocked LLM)."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import music21
import pytest

from composer.pipeline import arrange


def _create_test_musicxml(path: Path) -> None:
    """Create a minimal piano MusicXML for testing."""
    score = music21.stream.Score()
    md = music21.metadata.Metadata()
    md.title = "Test"
    score.metadata = md

    treble = music21.stream.Part()
    m = music21.stream.Measure(number=1)
    m.insert(0, music21.meter.TimeSignature("4/4"))
    m.insert(0, music21.chord.Chord(["C5", "E4"], quarterLength=4.0))
    treble.append(m)

    bass_part = music21.stream.Part()
    mb = music21.stream.Measure(number=1)
    mb.insert(0, music21.meter.TimeSignature("4/4"))
    mb.insert(0, music21.note.Note("C3", quarterLength=4.0))
    bass_part.append(mb)

    score.insert(0, treble)
    score.insert(0, bass_part)
    score.write("musicxml", fp=str(path))


@pytest.mark.asyncio
async def test_arrange_produces_output(tmp_path):
    """Test that the pipeline produces an output file (with LLM returning passthrough)."""
    input_path = tmp_path / "input.musicxml"
    output_path = tmp_path / "output.musicxml"
    _create_test_musicxml(input_path)

    # Mock LLM to return the input unchanged (passthrough)
    with patch("composer.pipeline.LLMClient") as mock_cls:
        instance = mock_cls.return_value
        instance.transform_to_bossa = AsyncMock(side_effect=lambda ir: ir)

        await arrange(input_path, output_path)

    assert output_path.exists()
    # Verify it's valid MusicXML
    result = music21.converter.parse(str(output_path))
    assert result is not None
