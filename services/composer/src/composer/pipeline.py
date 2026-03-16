"""Arrangement pipeline: split → transform → assemble."""

import logging
from pathlib import Path

from musicxml_tools import parse_score, split_voices, to_intermediate, from_intermediate, assemble_score
from musicxml_tools.assembler import write_score
from musicxml_tools.drums import generate_bossa_drums

from composer.llm_client import LLMClient

logger = logging.getLogger(__name__)


async def arrange(input_path: Path, output_path: Path) -> None:
    """Run the full bossa arrangement pipeline.

    Steps:
    1. Parse input MusicXML
    2. Split voices (melody, harmony, bass)
    3. Convert to intermediate representation
    4. Send to LLM for bossa transformation
    5. Convert back from intermediate representation
    6. Generate bossa drum track
    7. Assemble and write output MusicXML
    """
    logger.info("Parsing input score: %s", input_path)
    score = parse_score(input_path)

    logger.info("Splitting voices")
    parts = split_voices(score)

    logger.info("Converting to intermediate representation")
    ir = to_intermediate(parts)

    logger.info("Requesting LLM bossa transformation")
    client = LLMClient()
    transformed_ir = await client.transform_to_bossa(ir)

    logger.info("Converting back from intermediate representation")
    transformed_parts = from_intermediate(transformed_ir)

    logger.info("Generating bossa drum track")
    # Count measures from the melody part
    num_measures = len(list(transformed_parts.melody.getElementsByClass("Measure")))
    if num_measures == 0:
        # Estimate from note offsets
        all_notes = list(transformed_parts.melody.flatten().notesAndRests)
        if all_notes:
            max_offset = max(n.offset + n.quarterLength for n in all_notes)
            ts = ir["metadata"].get("time_signature", "4/4")
            beats = int(ts.split("/")[0])
            num_measures = max(1, int(max_offset / beats) + 1)
        else:
            num_measures = 4

    drums = generate_bossa_drums(
        num_measures=num_measures,
        time_signature=ir["metadata"].get("time_signature", "4/4"),
    )

    logger.info("Assembling output score")
    output_score = assemble_score(transformed_parts, drums=drums)

    logger.info("Writing output: %s", output_path)
    write_score(output_score, output_path)
