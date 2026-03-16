"""Tests for bossa drum generation."""

import music21

from musicxml_tools.drums import generate_bossa_drums


def test_generate_correct_number_of_measures():
    drums = generate_bossa_drums(8)
    measures = list(drums.getElementsByClass(music21.stream.Measure))
    assert len(measures) == 8


def test_generate_has_time_signature():
    drums = generate_bossa_drums(4)
    ts = list(drums.flatten().getElementsByClass(music21.meter.TimeSignature))
    assert len(ts) >= 1
    assert ts[0].ratioString == "4/4"
