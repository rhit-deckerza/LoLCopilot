from __future__ import annotations
import threading
from typing import Optional, Dict, Any

class SharedState:
    """Thread-safe cache for game + CV positions."""
    def __init__(self):
        self._lock = threading.RLock()
        self._game: Optional[dict] = None         # raw API dict (your GameState also ok)
        self._summary: Optional[str] = None       # compact text produced by summarizer
        self._positions: Dict[str, Any] = {}      # { 'allies': [...], 'enemies_last_seen': [...] }

    def set_game(self, raw: dict, summary: str):
        with self._lock:
            self._game = raw
            self._summary = summary

    def get_game(self) -> Optional[dict]:
        with self._lock:
            return self._game

    def get_summary(self) -> Optional[str]:
        with self._lock:
            return self._summary

    def set_positions(self, positions: Dict[str, Any]):
        with self._lock:
            self._positions = positions

    def get_positions(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._positions)
