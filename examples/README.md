# Examples

Place MusicXML files here for testing and training.

## Structure

```
examples/
  input/     Piano scores (MusicXML) — the raw input
  output/    Bossa arrangements (MusicXML) — the expected output
```

## For Training

Create subdirectories under a `training/` folder with input/output pairs:

```
examples/training/
  song1/
    input.musicxml
    output.musicxml
  song2/
    input.musicxml
    output.musicxml
```

These pairs are used by `services/training/` to prepare fine-tuning datasets.
