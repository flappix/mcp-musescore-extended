"""Playback tools for MuseScore MCP: loop, play/stop, speed, mixer, voices."""

import math
from typing import Annotated, Any, Dict, Optional

from fastmcp import FastMCP

from ..client import MuseScoreClient


def setup_playback_tools(mcp: FastMCP, client: MuseScoreClient) -> None:
    """Register the playback tools.

    Args:
        mcp (FastMCP): The server to register the tools on.
        client (MuseScoreClient): The client the tools send their commands
            through.
    """

    @mcp.tool(
        description=(
            "Loop playback over whole measures and switch the loop on (it is not a toggle). Start playback "
            "with play; it then repeats the range until stop."
        ),
        tags={"playback"},
    )
    async def set_loop(
        start_measure: Annotated[int, "First measure of the loop (1-based)"],
        end_measure: Annotated[int, "Last measure of the loop (inclusive)"],
    ):
        return await client.request(
            "setLoop",
            {"startMeasure": start_measure, "endMeasure": end_measure},
        )

    @mcp.tool(description="Switch loop playback off.", tags={"playback"})
    async def clear_loop():
        return await client.request("setLoop", {"off": True})

    @mcp.tool(
        description=(
            "Start playback (does nothing when it is already playing). With a loop on, it plays the loop from "
            "its start, over and over."
        ),
        tags={"playback"},
    )
    async def play():
        return await client.request("play")

    @mcp.tool(description="Stop playback.", tags={"playback"})
    async def stop():
        return await client.request("stop")

    @mcp.tool(
        description=(
            "Play back at a percentage of the score's tempo (e.g. 75 to practise slower), like the speed "
            "control in MuseScore's playback toolbar. The tempo markings in the score do not change."
        ),
        tags={"playback"},
    )
    async def set_playback_speed(
        percent: Annotated[
            float,
            "Percentage of the written tempo, 10 to 300 (100: as written)",
        ],
    ):
        return await client.request("setPlaybackSpeed", {"percent": percent})

    @mcp.tool(
        description=(
            "Set the mixer channel of a staff's instrument: mute, solo and/or volume. MuseScore's mixer has "
            "one channel per instrument, so this applies to all staves of that instrument (e.g. both piano "
            "staves). Leave out what should not change."
        ),
        tags={"playback"},
    )
    async def set_staff_mix(
        staff: Annotated[int, "Staff (0-based) whose instrument to set"],
        mute: Annotated[Optional[bool], "Mute or unmute"] = None,
        solo: Annotated[Optional[bool], "Solo or unsolo"] = None,
        volume_db: Annotated[
            Optional[float],
            "Volume in dB, -60 to 12 (0 is the default level, -6 about half as loud)",
        ] = None,
    ):
        params: Dict[str, Any] = {"staff": staff}
        if mute is not None:
            params["mute"] = mute
        if solo is not None:
            params["solo"] = solo
        if volume_db is not None:
            params["volumeDb"] = volume_db
        return await client.request("setStaffMix", params)

    @mcp.tool(
        description=(
            "Switch the playback of one voice (1-4) of a staff on or off, e.g. to hear only the melody (voice "
            "1) or only the bass (voice 2) of a guitar part. It is a staff property, saved with the score "
            "(undoable)."
        ),
        tags={"playback"},
    )
    async def set_voice_playback(
        staff: Annotated[int, "Staff (0-based)"],
        voice: Annotated[int, "Voice 1 to 4"],
        play: Annotated[bool, "True to hear the voice, False to silence it"],
    ):
        return await client.request(
            "setVoicePlayback", {"staff": staff, "voice": voice, "play": play}
        )

    @mcp.tool(
        description=(
            "Switch the metronome (the click during playback) on or off, and/or set its volume, as a "
            "percentage of its normal level or in dB. Leave out what should not change."
        ),
        tags={"playback"},
    )
    async def set_metronome(
        on: Annotated[Optional[bool], "True to switch it on, False off"] = None,
        volume_percent: Annotated[
            Optional[float],
            "Volume as a percentage of the normal level (amplitude: 50 is about -6 dB), 1 to 400",
        ] = None,
        volume_db: Annotated[
            Optional[float],
            "Volume in dB, -60 to 12, instead of volume_percent",
        ] = None,
    ):
        params: Dict[str, Any] = {}
        if on is not None:
            params["on"] = on
        if volume_percent is not None:
            if not 1 <= volume_percent <= 400:
                return {"error": "volume_percent must be between 1 and 400"}
            params["volumeDb"] = 20 * math.log10(volume_percent / 100)
        elif volume_db is not None:
            params["volumeDb"] = volume_db
        return await client.request("setMetronome", params)
