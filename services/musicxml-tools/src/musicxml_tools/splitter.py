"""Split a piano score into separate voice parts (melody, harmony, bass)."""

from dataclasses import dataclass

import music21


@dataclass
class SplitParts:
    """Result of splitting a piano score into voices."""

    melody: music21.stream.Part
    harmony: music21.stream.Part
    bass: music21.stream.Part
    metadata: dict


def split_voices(score: music21.stream.Score) -> SplitParts:
    """Split a piano score into melody (top), harmony (middle), and bass (bottom).

    Strategy:
    - If the score has separate treble/bass staves, use them as starting points.
    - In the treble staff: highest voice → melody, remaining → harmony.
    - In the bass staff: lowest voice → bass, remaining → added to harmony.

    Args:
        score: A music21 Score, typically a piano score with treble and bass clefs.

    Returns:
        SplitParts with melody, harmony, and bass as separate Part objects.
    """
    metadata = _extract_metadata(score)
    parts = list(score.parts)

    if len(parts) == 0:
        raise ValueError("Score has no parts")

    if len(parts) == 1:
        # Single staff — split by pitch register
        return _split_single_staff(parts[0], metadata)

    # Typical piano: parts[0] = treble (right hand), parts[1] = bass (left hand)
    treble_part = parts[0]
    bass_part = parts[1]

    melody = _extract_top_voice(treble_part, "Alto Sax")
    harmony = _extract_inner_voices(treble_part, bass_part, "Piano")
    bass = _extract_bottom_voice(bass_part, "Bass")

    return SplitParts(melody=melody, harmony=harmony, bass=bass, metadata=metadata)


def _extract_metadata(score: music21.stream.Score) -> dict:
    """Extract score metadata (title, tempo, key, time signature)."""
    md = score.metadata
    meta = {
        "title": md.title if md and md.title else "Untitled",
    }

    # Get tempo
    tempos = score.flatten().getElementsByClass(music21.tempo.MetronomeMark)
    if tempos:
        meta["tempo"] = tempos[0].number
    else:
        meta["tempo"] = 120  # default

    # Get key signature
    keys = score.flatten().getElementsByClass(music21.key.KeySignature)
    if keys:
        meta["key"] = str(keys[0])
    else:
        meta["key"] = "C major"

    # Get time signature
    time_sigs = score.flatten().getElementsByClass(music21.meter.TimeSignature)
    if time_sigs:
        meta["time_signature"] = time_sigs[0].ratioString
    else:
        meta["time_signature"] = "4/4"

    return meta


def _extract_top_voice(part: music21.stream.Part, name: str) -> music21.stream.Part:
    """Extract the highest notes from a part to form the melody line."""
    new_part = music21.stream.Part()
    new_part.partName = name

    for measure in part.getElementsByClass(music21.stream.Measure):
        new_measure = music21.stream.Measure(number=measure.number)

        # Copy time signatures, key signatures, clefs
        for elem in measure.getElementsByClass(
            (music21.meter.TimeSignature, music21.key.KeySignature, music21.clef.Clef)
        ):
            new_measure.insert(elem.offset, elem)

        # Group notes by offset to find the highest at each beat
        notes_by_offset: dict[float, list[music21.note.Note]] = {}
        for elem in measure.notesAndRests:
            offset = elem.offset
            if isinstance(elem, music21.note.Note):
                notes_by_offset.setdefault(offset, []).append(elem)
            elif isinstance(elem, music21.chord.Chord):
                # Take the highest note from chords
                top = elem.sortAscending()[-1]
                n = music21.note.Note(top.pitch, quarterLength=elem.quarterLength)
                notes_by_offset.setdefault(offset, []).append(n)
            elif isinstance(elem, music21.note.Rest):
                notes_by_offset.setdefault(offset, []).append(elem)

        for offset in sorted(notes_by_offset.keys()):
            notes = notes_by_offset[offset]
            actual_notes = [n for n in notes if isinstance(n, music21.note.Note)]
            if actual_notes:
                highest = max(actual_notes, key=lambda n: n.pitch.midi)
                new_measure.insert(offset, music21.note.Note(
                    highest.pitch, quarterLength=highest.quarterLength
                ))
            else:
                # Only rests at this offset
                new_measure.insert(offset, notes[0])

        new_part.append(new_measure)

    return new_part


def _extract_bottom_voice(part: music21.stream.Part, name: str) -> music21.stream.Part:
    """Extract the lowest notes from a part to form the bass line."""
    new_part = music21.stream.Part()
    new_part.partName = name

    for measure in part.getElementsByClass(music21.stream.Measure):
        new_measure = music21.stream.Measure(number=measure.number)

        for elem in measure.getElementsByClass(
            (music21.meter.TimeSignature, music21.key.KeySignature, music21.clef.Clef)
        ):
            new_measure.insert(elem.offset, elem)

        notes_by_offset: dict[float, list[music21.note.Note]] = {}
        for elem in measure.notesAndRests:
            offset = elem.offset
            if isinstance(elem, music21.note.Note):
                notes_by_offset.setdefault(offset, []).append(elem)
            elif isinstance(elem, music21.chord.Chord):
                bottom = elem.sortAscending()[0]
                n = music21.note.Note(bottom.pitch, quarterLength=elem.quarterLength)
                notes_by_offset.setdefault(offset, []).append(n)
            elif isinstance(elem, music21.note.Rest):
                notes_by_offset.setdefault(offset, []).append(elem)

        for offset in sorted(notes_by_offset.keys()):
            notes = notes_by_offset[offset]
            actual_notes = [n for n in notes if isinstance(n, music21.note.Note)]
            if actual_notes:
                lowest = min(actual_notes, key=lambda n: n.pitch.midi)
                new_measure.insert(offset, music21.note.Note(
                    lowest.pitch, quarterLength=lowest.quarterLength
                ))
            else:
                new_measure.insert(offset, notes[0])

        new_part.append(new_measure)

    return new_part


def _extract_inner_voices(
    treble: music21.stream.Part,
    bass: music21.stream.Part,
    name: str,
) -> music21.stream.Part:
    """Extract inner voices (everything except top treble and bottom bass)."""
    new_part = music21.stream.Part()
    new_part.partName = name

    for measure in treble.getElementsByClass(music21.stream.Measure):
        new_measure = music21.stream.Measure(number=measure.number)

        for elem in measure.getElementsByClass(
            (music21.meter.TimeSignature, music21.key.KeySignature, music21.clef.Clef)
        ):
            new_measure.insert(elem.offset, elem)

        for elem in measure.notesAndRests:
            if isinstance(elem, music21.chord.Chord) and len(elem.pitches) > 1:
                # Remove the top note (that went to melody), keep the rest
                remaining = elem.sortAscending().pitches[:-1]
                if len(remaining) == 1:
                    n = music21.note.Note(remaining[0], quarterLength=elem.quarterLength)
                    new_measure.insert(elem.offset, n)
                elif len(remaining) > 1:
                    c = music21.chord.Chord(remaining, quarterLength=elem.quarterLength)
                    new_measure.insert(elem.offset, c)

        new_part.append(new_measure)

    # Also grab inner voices from bass staff (everything except bottom note)
    for measure in bass.getElementsByClass(music21.stream.Measure):
        measure_num = measure.number
        # Find or create the corresponding measure in new_part
        existing = None
        for m in new_part.getElementsByClass(music21.stream.Measure):
            if m.number == measure_num:
                existing = m
                break

        if existing is None:
            existing = music21.stream.Measure(number=measure_num)
            new_part.append(existing)

        for elem in measure.notesAndRests:
            if isinstance(elem, music21.chord.Chord) and len(elem.pitches) > 1:
                remaining = elem.sortAscending().pitches[1:]  # remove bottom
                if len(remaining) == 1:
                    n = music21.note.Note(remaining[0], quarterLength=elem.quarterLength)
                    existing.insert(elem.offset, n)
                elif len(remaining) > 1:
                    c = music21.chord.Chord(remaining, quarterLength=elem.quarterLength)
                    existing.insert(elem.offset, c)

    return new_part


def _split_single_staff(part: music21.stream.Part, metadata: dict) -> SplitParts:
    """Split a single-staff score by pitch register."""
    melody = music21.stream.Part()
    melody.partName = "Alto Sax"
    harmony = music21.stream.Part()
    harmony.partName = "Piano"
    bass = music21.stream.Part()
    bass.partName = "Bass"

    # Use C4 (middle C, MIDI 60) as the split point
    mid_split = 60

    for measure in part.getElementsByClass(music21.stream.Measure):
        mel_m = music21.stream.Measure(number=measure.number)
        har_m = music21.stream.Measure(number=measure.number)
        bas_m = music21.stream.Measure(number=measure.number)

        for elem in measure.notesAndRests:
            if isinstance(elem, music21.note.Note):
                if elem.pitch.midi >= mid_split + 12:
                    mel_m.insert(elem.offset, elem)
                elif elem.pitch.midi >= mid_split:
                    har_m.insert(elem.offset, elem)
                else:
                    bas_m.insert(elem.offset, elem)
            elif isinstance(elem, music21.chord.Chord):
                high = [p for p in elem.pitches if p.midi >= mid_split + 12]
                mid = [p for p in elem.pitches if mid_split <= p.midi < mid_split + 12]
                low = [p for p in elem.pitches if p.midi < mid_split]

                if high:
                    mel_m.insert(elem.offset, music21.note.Note(
                        max(high, key=lambda p: p.midi), quarterLength=elem.quarterLength
                    ))
                if mid:
                    if len(mid) == 1:
                        har_m.insert(elem.offset, music21.note.Note(
                            mid[0], quarterLength=elem.quarterLength
                        ))
                    else:
                        har_m.insert(elem.offset, music21.chord.Chord(
                            mid, quarterLength=elem.quarterLength
                        ))
                if low:
                    bas_m.insert(elem.offset, music21.note.Note(
                        min(low, key=lambda p: p.midi), quarterLength=elem.quarterLength
                    ))
            elif isinstance(elem, music21.note.Rest):
                mel_m.insert(elem.offset, elem)
                bas_m.insert(elem.offset, music21.note.Rest(quarterLength=elem.quarterLength))

        melody.append(mel_m)
        harmony.append(har_m)
        bass.append(bas_m)

    return SplitParts(melody=melody, harmony=harmony, bass=bass, metadata=metadata)
