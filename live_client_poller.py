from __future__ import annotations
import threading, time, requests
from typing import Optional, Callable, Dict, Any
from config import LIVE_CLIENT_URL, LIVE_CLIENT_VERIFY_SSL
from summarizer import summarize_allgamedata

class LiveClientPoller(threading.Thread):
    """Polls Riot's Live Client API and updates a shared cache via callback."""
    def __init__(self, on_update: Callable[[dict, str], None], interval_sec: float = 1.0):
        super().__init__(daemon=True)
        self.on_update = on_update
        self.interval = interval_sec
        self._stop = threading.Event()

    def run(self):
        while not self._stop.is_set():
            try:
                r = requests.get(LIVE_CLIENT_URL, verify=LIVE_CLIENT_VERIFY_SSL, timeout=0.8)
                r.raise_for_status()
                data = r.json()
                summary = summarize_allgamedata(data)
                self.on_update(data, summary)
            except Exception as e:
                # No game / champ select / etc.
                self.on_update({}, "NO_GAME")
            time.sleep(self.interval)

    def stop(self):
        self._stop.set()
