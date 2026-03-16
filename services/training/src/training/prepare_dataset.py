"""Prepare training dataset from MusicXML input/output pairs."""

import argparse
import json
import logging
from pathlib import Path

from musicxml_tools import parse_score, split_voices, to_intermediate

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert jazz arranger specializing in bossa nova. "
    "Transform the given musical arrangement into bossa nova style. "
    "Return ONLY valid JSON in the same format."
)


def prepare_pair(input_path: Path, output_path: Path) -> dict:
    """Convert one input/output MusicXML pair into a training example.

    Args:
        input_path: Path to the original piano score.
        output_path: Path to the bossa arrangement.

    Returns:
        A training example dict with system/user/assistant messages.
    """
    # Parse and convert both to intermediate representation
    input_score = parse_score(input_path)
    input_parts = split_voices(input_score)
    input_ir = to_intermediate(input_parts)

    output_score = parse_score(output_path)
    output_parts = split_voices(output_score)
    output_ir = to_intermediate(output_parts)

    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Transform this arrangement to bossa nova style. "
                    "Return ONLY the transformed JSON:\n\n"
                    + json.dumps(input_ir, indent=2)
                ),
            },
            {
                "role": "assistant",
                "content": json.dumps(output_ir, indent=2),
            },
        ]
    }


def prepare_dataset(data_dir: Path, output_path: Path) -> None:
    """Prepare the full training dataset from a directory of pairs.

    Expected structure:
        data_dir/
            song1/
                input.musicxml
                output.musicxml
            song2/
                input.musicxml
                output.musicxml

    Args:
        data_dir: Directory containing song pair subdirectories.
        output_path: Path to write the JSONL training file.
    """
    examples = []

    for song_dir in sorted(data_dir.iterdir()):
        if not song_dir.is_dir():
            continue

        input_file = song_dir / "input.musicxml"
        output_file = song_dir / "output.musicxml"

        if not input_file.exists() or not output_file.exists():
            logger.warning("Skipping %s: missing input.musicxml or output.musicxml", song_dir.name)
            continue

        try:
            example = prepare_pair(input_file, output_file)
            examples.append(example)
            logger.info("Prepared: %s", song_dir.name)
        except Exception:
            logger.exception("Failed to prepare %s", song_dir.name)

    # Write JSONL
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for example in examples:
            f.write(json.dumps(example) + "\n")

    logger.info("Wrote %d training examples to %s", len(examples), output_path)


def main():
    parser = argparse.ArgumentParser(description="Prepare training dataset from MusicXML pairs")
    parser.add_argument("--data-dir", type=Path, required=True, help="Directory of song pairs")
    parser.add_argument("--output", type=Path, default=Path("data/training.jsonl"))
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    prepare_dataset(args.data_dir, args.output)


if __name__ == "__main__":
    main()
