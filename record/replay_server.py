import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import List, Dict, Any

class ReplayState:
    def __init__(self, frames: List[Dict[str, Any]], speed: float = 1.0, loop: bool = False):
        self.frames = frames
        self.speed = speed
        self.loop = loop
        self.idx = 0
        self.lock = threading.RLock()
        self.current = frames[0]["data"] if frames else {}
        self._stop = threading.Event()

    def start(self):
        while not self._stop.is_set() and self.frames:
            with self.lock:
                if self.idx >= len(self.frames):
                    if self.loop:
                        self.idx = 0
                    else:
                        break
                frame = self.frames[self.idx]
            # set immediately for first frame, then sleep based on delta
            if self.idx > 0:
                prev = self.frames[self.idx - 1]
                dt_wall = max(0.0, (frame["t_wall"] - prev["t_wall"]) / max(1e-6, self.speed))
                time.sleep(dt_wall)
            with self.lock:
                self.current = frame.get("data") or {}
                self.idx += 1

    def stop(self):
        self._stop.set()

    def get_current(self) -> Dict[str, Any]:
        with self.lock:
            return self.current or {"gameData": {"gameTime": 0}, "allPlayers": []}

class Handler(BaseHTTPRequestHandler):
    state: ReplayState = None  # injected

    def do_GET(self):
        if self.path.startswith("/liveclientdata/allgamedata"):
            body = json.dumps(self.state.get_current()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # silence logs
        return

def load_frames(jsonl_path: Path) -> List[Dict[str, Any]]:
    frames = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if "data" in obj and obj["data"]:
                    frames.append(obj)
            except Exception:
                pass
    return frames

def main():
    ap = argparse.ArgumentParser(description="Replay a recorded Live Client API JSONL file as a local HTTP server.")
    ap.add_argument("jsonl", help="Path to liveclientdata.jsonl recording")
    ap.add_argument("--host", default="127.0.0.1", help="Host to bind")
    ap.add_argument("--port", type=int, default=2999, help="Port to bind (default 2999 to match Riot)")
    ap.add_argument("--speed", type=float, default=1.0, help="Playback speed multiplier (e.g., 2.0 = 2x)")
    ap.add_argument("--loop", action="store_true", help="Loop playback")
    args = ap.parse_args()

    frames = load_frames(Path(args.jsonl))
    if not frames:
        raise SystemExit("No frames loaded from recording.")

    state = ReplayState(frames, speed=args.speed, loop=args.loop)
    Handler.state = state

    server = HTTPServer((args.host, args.port), Handler)
    t = threading.Thread(target=state.start, daemon=True)
    t.start()

    print(f"[REPLAY] Serving on http://{args.host}:{args.port}/liveclientdata/allgamedata  (speed={args.speed}x, loop={args.loop})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[REPLAY] Stopping...")
    finally:
        state.stop()
        server.server_close()

if __name__ == "__main__":
    main()
