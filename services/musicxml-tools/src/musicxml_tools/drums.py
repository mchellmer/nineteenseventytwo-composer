"""Bossa nova drum pattern generator."""

import music21


# Standard bossa nova drum pattern (2-bar pattern in 4/4)
# Using General MIDI percussion:
#   42 = Closed Hi-Hat
#   46 = Open Hi-Hat
#   38 = Snare (cross-stick/rim click)
#   36 = Bass Drum


def generate_bossa_drums(
    num_measures: int,
    time_signature: str = "4/4",
) -> music21.stream.Part:
    """Generate a bossa nova drum pattern.

    The standard bossa pattern is a 2-bar cycle:
    - Hi-hat: steady eighth notes
    - Cross-stick: beats 2 and 4 (rim click feel)
    - Bass drum: syncopated bossa pattern

    Args:
        num_measures: Number of measures to generate.
        time_signature: Time signature string (default: 4/4).

    Returns:
        A music21 Part with unpitched percussion.
    """
    part = music21.stream.Part()
    part.partName = "Drums"

    ts_parts = time_signature.split("/")
    ts = music21.meter.TimeSignature(time_signature)
    beats_per_measure = int(ts_parts[0])

    for i in range(num_measures):
        measure = music21.stream.Measure(number=i + 1)
        if i == 0:
            measure.insert(0, ts)

        # Which bar of the 2-bar cycle (0 or 1)
        cycle_bar = i % 2

        # Hi-hat: eighth notes throughout
        for eighth in range(beats_per_measure * 2):
            offset = eighth * 0.5
            hh = music21.note.Unpitched()
            hh.displayName = "Closed Hi-Hat"
            hh.storedInstrument = music21.instrument.HiHatCymbal()
            hh.quarterLength = 0.5
            measure.insert(offset, hh)

        # Cross-stick on beats 2 and 4
        for beat in [1.0, 3.0]:
            rim = music21.note.Unpitched()
            rim.displayName = "Side Stick"
            rim.storedInstrument = music21.instrument.SnareDrum()
            rim.quarterLength = 1.0
            measure.insert(beat, rim)

        # Bass drum: bossa pattern
        # Bar 1: beat 1, and-of-2, beat 4
        # Bar 2: and-of-1, beat 3, and-of-4
        if cycle_bar == 0:
            bd_offsets = [0.0, 1.5, 3.0]
        else:
            bd_offsets = [0.5, 2.0, 3.5]

        for offset in bd_offsets:
            bd = music21.note.Unpitched()
            bd.displayName = "Bass Drum"
            bd.storedInstrument = music21.instrument.BassDrum()
            bd.quarterLength = 0.5
            measure.insert(offset, bd)

        part.append(measure)

    return part
