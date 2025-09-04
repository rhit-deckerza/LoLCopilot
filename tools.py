from __future__ import annotations
from typing import Any, Dict
from pydantic import BaseModel, Field
from state_cache import SharedState

# Tool schemas (Pydantic) for clarity and validation if you wire into other frameworks
class FetchStateArgs(BaseModel):
    pass

class FetchPositionsArgs(BaseModel):
    pass

def make_tools_spec():
    """Returns the JSON schema list for OpenAI Responses tools."""
    return [
        {
            "type": "function",
            "name": "fetch_state",
            "description": "Get the latest compact LoL game state snapshot.",
            "parameters": {"type":"object","properties":{},"additionalProperties":False}
        },
        {
            "type": "function",
            "name": "fetch_positions",
            "description": "Get ally positions and enemies' last seen from CV module, if available.",
            "parameters": {"type":"object","properties":{},"additionalProperties":False}
        }
    ]

def handle_tool_call(cache: SharedState, name: str, arguments_json: str) -> str:
    """Return string content for the tool result."""
    if name == "fetch_state":
        summary = cache.get_summary() or "NO_GAME"
        return summary
    if name == "fetch_positions":
        pos = cache.get_positions()
        return "NONE" if not pos else str(pos)
    return "UNSUPPORTED_TOOL"
