"""Tests for the voice splitter."""

import music21
import pytest

from musicxml_tools.splitter import split_voices


def _make_piano_score() -> music21.stream.Score:
    """Create a simple 2-measure piano score for testing."""
    score = music21.stream.Score()
    md = music21.metadata.Metadata()
    md.title = "Test Score"
    score.metadata = md

    # Treble staff (right hand)
    treble = music21.stream.Part()
    treble.partName = "Piano Right"

    m1 = music21.stream.Measure(number=1)
    m1.insert(0, music21.meter.TimeSignature("4/4"))
    # Chord with melody on top + harmony below
    m1.insert(0, music21.chord.Chord(["C5", "E4", "G4"], quarterLength=2.0))
    m1.insert(2, music21.chord.Chord(["D5", "F4", "A4"], quarterLength=2.0))
    treble.append(m1)

    m2 = music21.stream.Measure(number=2)
    m2.insert(0, music21.chord.Chord(["E5", "G4", "B4"], quarterLength=4.0))
    treble.append(m2)

    # Bass staff (left hand)
    bass = music21.stream.Part()
    bass.partName = "Piano Left"

    m1b = music21.stream.Measure(number=1)
    m1b.insert(0, music21.meter.TimeSignature("4/4"))
    m1b.insert(0, music21.note.Note("C3", quarterLength=2.0))
    m1b.insert(2, music21.note.Note("D3", quarterLength=2.0))
    bass.append(m1b)

    m2b = music21.stream.Measure(number=2)
    m2b.insert(0, music21.note.Note("E3", quarterLength=4.0))
    bass.append(m2b)

    score.insert(0, treble)
    score.insert(0, bass)

    return score


def test_split_voices_returns_three_parts():
    score = _make_piano_score()
    parts = split_voices(score)

    assert parts.melody is not None
    assert parts.harmony is not None
    assert parts.bass is not None


def test_split_voices_melody_is_top_note():
    score = _make_piano_score()
    parts = split_voices(score)

    melody_notes = list(parts.melody.flatten().getElementsByClass(music21.note.Note))
    # Should get C5, D5, E5 as the top notes
    pitches = [n.nameWithOctave for n in melody_notes]
    assert "C5" in pitches
    assert "D5" in pitches
    assert "E5" in pitches


def test_split_voices_bass_is_bottom_note():
    score = _make_piano_score()
    parts = split_voices(score)

    bass_notes = list(parts.bass.flatten().getElementsByClass(music21.note.Note))
    pitches = [n.nameWithOctave for n in bass_notes]
    assert "C3" in pitches
    assert "D3" in pitches
    assert "E3" in pitches


def test_split_voices_metadata():
    score = _make_piano_score()
    parts = split_voices(score)

    assert parts.metadata["title"] == "Test Score"
    assert parts.metadata["time_signature"] == "4/4"


def test_split_voices_empty_score_raises():
    score = music21.stream.Score()
    with pytest.raises(ValueError, match="no parts"):
        split_voices(score)
