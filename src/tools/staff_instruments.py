"""Staff and instrument tools for MuseScore MCP."""

from typing import Annotated, List, Optional

from fastmcp import FastMCP

from ..client import MuseScoreClient


def setup_staff_instruments_tools(
    mcp: FastMCP, client: MuseScoreClient
) -> None:
    """Register the staff and instrument tools.

    Args:
        mcp (FastMCP): The server to register the tools on.
        client (MuseScoreClient): The client the tools send their commands
            through.
    """

    @mcp.tool(
        description=(
            "Create a new score and open it in place of the current one, like File > New. MuseScore "
            "first closes the current score and asks the user to save it when it has unsaved changes. "
            "The measures are filled with rests; write into them with the note tools."
        ),
        tags={"staff", "score"},
    )
    async def new_score(
        instruments: Annotated[
            List[str],
            'Instrument ids from top to bottom, e.g. ["violin", "guitar-nylon"]. Others: "piano", '
            '"flute", "viola", "cello", "voice", "guitar-steel", "electric-bass", "drumset"',
        ],
        title: Annotated[str, "Title shown at the top"] = "",
        composer: Annotated[str, "Composer shown below the title"] = "",
        key_fifths: Annotated[
            int,
            "Key signature in concert pitch: sharps (1 to 7) or flats (-1 to -7); 0 for C major / A minor. "
            "A minor key uses its relative major's signature (E minor: 1)",
        ] = 0,
        time_numerator: Annotated[int, "Time signature numerator"] = 4,
        time_denominator: Annotated[int, "Time signature denominator"] = 4,
        tempo_bpm: Annotated[
            Optional[int],
            "Tempo in quarter notes per minute; None for no marking",
        ] = None,
        measures: Annotated[int, "Number of measures"] = 16,
        pickup_numerator: Annotated[
            Optional[int],
            "Length of a pickup measure in beats of pickup_denominator; None for no pickup",
        ] = None,
        pickup_denominator: Annotated[
            int, "Note value of the pickup's beats"
        ] = 4,
    ):
        params = {
            "instruments": instruments,
            "title": title,
            "composer": composer,
            "keyFifths": key_fifths,
            "timesigNumerator": time_numerator,
            "timesigDenominator": time_denominator,
            "measures": measures,
        }
        if tempo_bpm:
            params["tempoBpm"] = tempo_bpm
        if pickup_numerator:
            params["pickupNumerator"] = pickup_numerator
            params["pickupDenominator"] = pickup_denominator
        return await client.request("newScore", params)

    @mcp.tool(
        description="Add a new staff/instrument to the score.",
        tags={"staff"},
    )
    async def add_instrument(
        instrument_id: Annotated[str, "ID of the instrument to add"],
    ):
        return await client.send_command(
            "addInstrument", {"instrumentId": instrument_id}
        )

    @mcp.tool(
        description="Mute or unmute a staff.",
        tags={"staff"},
    )
    async def set_staff_mute(
        staff: Annotated[int, "Staff number (0-based)"],
        mute: Annotated[bool, "True to mute, False to unmute"],
    ):
        return await client.send_command(
            "setStaffMute", {"staff": staff, "mute": mute}
        )

    @mcp.tool(
        description="Change the sound of an instrument on a staff.",
        tags={"staff"},
    )
    async def set_instrument_sound(
        staff: Annotated[int, "Staff number (0-based)"],
        instrument_id: Annotated[str, "ID of the new instrument sound"],
    ):
        return await client.send_command(
            "setInstrumentSound",
            {"staff": staff, "instrumentId": instrument_id},
        )
