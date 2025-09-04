"""Simple pub/sub for CV positions so other threads can push updates.

Expected shape for positions:

positions = {
  'allies': [ {'role':'MID','x':0.52,'y':0.31,'ts':834}, ... ],
  'enemies_last_seen': [ {'champ':'Zed','x':0.61,'y':0.48,'ts':820}, ... ]
}
* x,y are normalized [0,1] on a consistent top-left origin minimap projection.
* 'ts' is game time seconds when seen.
"""
from __future__ import annotations
from typing import Dict, Any
from state_cache import SharedState

def push_positions(cache: SharedState, positions: Dict[str, Any]) -> None:
    cache.set_positions(positions)
