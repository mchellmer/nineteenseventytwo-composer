"""Assemble individual parts into a complete MusicXML score."""

from pathlib import Path

import music21

from musicxml_tools.splitter import SplitParts


def assemble_score(
    parts: SplitParts,
    drums: music21.stream.Part | None = None,
    title: str | None = None,
) -> music21.stream.Score:
    """Assemble individual parts into a complete score.

    Args:
        parts: SplitParts with melody, harmony, and bass.
        drums: Optional drum part to include.
        title: Optional title override (defaults to metadata title).

    Returns:
        A music21 Score with all parts.
    """
    score = music21.stream.Score()

    # Set metadata
    md = music21.metadata.Metadata()
    md.title = title or parts.metadata.get("title", "Bossa Arrangement")
    score.metadata = md

    # Set tempo
    tempo_val = parts.metadata.get("tempo", 120)
    score.insert(0, music21.tempo.MetronomeMark(number=tempo_val))

    # Add parts in score order
    _set_instrument(parts.melody, music21.instrument.AltoSaxophone())
    score.insert(0, parts.melody)

    _set_instrument(parts.harmony, music21.instrument.Piano())
    score.insert(0, parts.harmony)

    _set_instrument(parts.bass, music21.instrument.ElectricBass())
    score.insert(0, parts.bass)

    if drums is not None:
        drums.partName = "Drums"
        score.insert(0, drums)

    return score


def write_score(score: music21.stream.Score, filepath: str | Path, fmt: str = "musicxml") -> None:
    """Write a score to a file.

    Args:
        score: The score to write.
        filepath: Output file path.
        fmt: Output format (default: musicxml).
    """
    score.write(fmt, fp=str(filepath))


def _set_instrument(part: music21.stream.Part, instrument: music21.instrument.Instrument) -> None:
    """Set the instrument for a part."""
    # Remove any existing instruments
    for inst in part.getElementsByClass(music21.instrument.Instrument):
        part.remove(inst)
    part.insert(0, instrument)
