"""musicxml-tools: MusicXML parsing, voice splitting, and score assembly."""

from musicxml_tools.parser import parse_score
from musicxml_tools.splitter import split_voices
from musicxml_tools.intermediate import to_intermediate, from_intermediate
from musicxml_tools.assembler import assemble_score

__all__ = [
    "parse_score",
    "split_voices",
    "to_intermediate",
    "from_intermediate",
    "assemble_score",
]
