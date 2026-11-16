"""Time signature and tempo tools for MuseScore MCP."""

from typing import Annotated, Dict, List, Literal, Optional, Union

from fastmcp import FastMCP

from ..client import MuseScoreClient


def setup_time_tempo_tools(mcp: FastMCP, client: MuseScoreClient) -> None:
    """Register the time signature and tempo tools.

    Args:
        mcp (FastMCP): The server to register the tools on.
        client (MuseScoreClient): The client the tools send their commands
            through.
    """

    @mcp.tool(
        description=(
            "Set the time signature from the start of the given measure (or of the measure at the cursor) "
            "on all staves, until the next time signature."
        ),
        tags={"time"},
    )
    async def set_time_signature(
        numerator: Annotated[
            int, "Top number of time signature (beats per measure)"
        ] = 4,
        denominator: Annotated[
            int,
            "Bottom number of time signature (note value that gets the beat)",
        ] = 4,
        measure: Annotated[
            Optional[int],
            "Measure number (1-based) where it starts. Defaults to the measure at the cursor.",
        ] = None,
    ):
        params = {"numerator": numerator, "denominator": denominator}
        if measure is not None:
            params["measure"] = measure
        return await client.send_command("setTimeSignature", params)

    @mcp.tool(
        description=(
            "Set the key signature from the start of a measure, on all staves until the next key "
            "signature. The key is given in concert pitch; transposing instruments get their own "
            "written key. A minor key has the key signature of its relative major (E minor: 1 sharp)."
        ),
        tags={"time"},
    )
    async def set_key_signature(
        fifths: Annotated[
            int,
            "Sharps (1 to 7) or flats (-1 to -7) of the key signature; 0 for C major / A minor",
        ],
        measure: Annotated[
            int, "Measure number (1-based) where the key starts"
        ] = 1,
    ):
        return await client.request(
            "setKeySignature", {"fifths": fifths, "measure": measure}
        )

    @mcp.tool(
        description=(
            "Set the tempo with a tempo marking (in quarter-note beats per minute) "
            "at the current cursor position, or at the start of the given measure."
        ),
        tags={"time"},
    )
    async def set_tempo(
        bpm: Annotated[
            float, "Tempo in quarter-note beats per minute (e.g. 120)"
        ],
        measure: Annotated[
            Optional[int],
            "Measure number (1-based) to place the tempo at. Defaults to the cursor position.",
        ] = None,
    ):
        params = {"bpm": bpm}
        if measure is not None:
            params["measure"] = measure
        return await client.send_command("setTempo", params)

    @mcp.tool(
        description=(
            "Add chord symbols (e.g. Am, F#dim, G7, Bb/D) above a staff, on the beats where notes or rests "
            "start. A chord symbol that is already on that beat is replaced. All are added as one undo step; "
            "if one cannot be placed, none is added."
        ),
        tags={"time"},
    )
    async def add_chord_symbols(
        chords: Annotated[
            List[Dict[str, Union[int, float, str]]],
            'Chords as {"measure": int (1-based), "beat": number (1-based, default 1), "text": str}, '
            'e.g. [{"measure": 1, "text": "Am"}, {"measure": 1, "beat": 3, "text": "E7"}]',
        ],
        staff: Annotated[
            int, "Staff (0-based) the chord symbols belong to"
        ] = 0,
    ):
        return await client.request(
            "addChordSymbols", {"chords": chords, "staff": staff}
        )

    @mcp.tool(
        description=(
            "Transpose the whole score, or a range of measures, to another key, like Tools > Transpose > "
            "To key: notes, key signatures and chord symbols. The key is given in concert pitch as the key "
            "signature; a minor key uses its relative major's signature (C minor: -3). One undo step."
        ),
        tags={"time"},
    )
    async def transpose_to_key(
        key_fifths: Annotated[
            int,
            "Target key signature: sharps (1 to 7) or flats (-1 to -7); 0 for C major / A minor",
        ],
        direction: Annotated[
            Literal["up", "down", "closest"], "Which way to move the notes"
        ] = "closest",
        start_measure: Annotated[
            Optional[int],
            "First measure (1-based) to transpose; None for the whole score",
        ] = None,
        end_measure: Annotated[
            Optional[int], "Last measure (1-based, inclusive)"
        ] = None,
        transpose_chord_symbols: Annotated[
            bool, "Whether chord symbols are transposed too"
        ] = True,
    ):
        params: Dict[str, Union[int, str, bool]] = {
            "keyFifths": key_fifths,
            "direction": direction,
            "transposeChordSymbols": transpose_chord_symbols,
        }
        if start_measure is not None:
            params["startMeasure"] = start_measure
            params["endMeasure"] = (
                end_measure if end_measure is not None else start_measure
            )
        return await client.request("transposeToKey", params)
