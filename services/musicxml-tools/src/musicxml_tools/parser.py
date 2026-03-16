"""Parse MusicXML files into music21 Score objects."""

from pathlib import Path

import music21


def parse_score(filepath: str | Path) -> music21.stream.Score:
    """Parse a MusicXML file and return a music21 Score.

    Args:
        filepath: Path to a .musicxml or .xml file.

    Returns:
        A music21 Score object.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        music21.converter.ConverterException: If the file can't be parsed.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Score not found: {filepath}")

    score = music21.converter.parse(str(filepath))
    if not isinstance(score, music21.stream.Score):
        # Wrap in a Score if converter returned a Part or other stream
        wrapper = music21.stream.Score()
        wrapper.insert(0, score)
        score = wrapper

    return score
