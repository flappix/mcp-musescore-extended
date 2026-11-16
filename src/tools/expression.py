"""Expression tools for MuseScore MCP: dynamics, hairpins, slurs, slides."""

from typing import Annotated, Dict, List, Union

from fastmcp import FastMCP

from ..client import MuseScoreClient


def setup_expression_tools(mcp: FastMCP, client: MuseScoreClient) -> None:
    """Register the dynamics, line and slide tools.

    Args:
        mcp (FastMCP): The server to register the tools on.
        client (MuseScoreClient): The client the tools send their commands
            through.
    """

    @mcp.tool(
        description=(
            "Add dynamics (pp, p, mp, mf, f, ff, sfz, fp...) at notes or rests: each at a measure and beat "
            "(1-based) of a staff. All are added as one undo step; if one cannot be placed, none is added."
        ),
        tags={"expression"},
    )
    async def add_dynamics(
        dynamics: Annotated[
            List[Dict[str, Union[int, float, str]]],
            'Dynamics as {"measure": int, "beat": number (default 1), "dynamic": str, "staff": int (default 0)}, '
            'e.g. [{"measure": 1, "dynamic": "p"}, {"measure": 5, "beat": 2, "dynamic": "mf"}]',
        ],
    ):
        return await client.request("addDynamics", {"dynamics": dynamics})

    @mcp.tool(
        description=(
            "Add lines over a range of notes of one staff, each from the note at its start to (and including) the "
            "note at its end: crescendo and diminuendo hairpins, slurs, and hammer-ons/pull-offs (guitar; "
            "MuseScore marks each rising pair H and each falling pair P). Each line is its own undo step; adding "
            "stops at the first line that cannot be added."
        ),
        tags={"expression"},
    )
    async def add_lines(
        lines: Annotated[
            List[Dict[str, Union[int, float, str]]],
            'Lines as {"kind": "crescendo" | "diminuendo" | "slur" | "hammer_on_pull_off", "startMeasure": int, '
            '"startBeat": number (default 1), "endMeasure": int, "endBeat": number (default 1), '
            '"staff": int (default 0), "voice": int (1-4, default 1)}; a note (for hairpins also a rest) must '
            "start at both ends in that voice. Hairpins belong to the whole staff; slurs and hammer-ons/pull-offs "
            "to the voice",
        ],
    ):
        return await client.request("addLines", {"lines": lines})

    @mcp.tool(
        description=(
            "Add guitar slides: a straight line from a note to a later note of the same staff. By default the "
            "top notes of the two chords; give pitch/toPitch for others. All are added as one undo step."
        ),
        tags={"expression"},
    )
    async def add_slides(
        slides: Annotated[
            List[Dict[str, Union[int, float]]],
            'Slides as {"measure": int, "beat": number (default 1), "toMeasure": int, "toBeat": number '
            '(default 1), "staff": int (default 0), "voice": int (1-4, default 1), "pitch": int, "toPitch": int '
            "(optional)}",
        ],
    ):
        return await client.request("addSlides", {"slides": slides})
