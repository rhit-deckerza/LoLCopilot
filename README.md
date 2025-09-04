# LoL Copilot (Realtime Chat + GPT-5 + Live Client + CV-ready)

This is a runnable prototype that:
- Polls the **League of Legends Live Client API** for the current game state.
- Exposes a **local WebSocket** (ws://127.0.0.1:8765) for chat clients (text or UI).
- Connects to **OpenAI GPT‑5** via the **Responses API** with **tool calling**, so the model can pull fresh game state on demand.
- Provides a compact, token‑efficient **game state summarizer**.
- Is designed to be extended with a **CV positions module** (ally positions + enemy last‑seen).

## Run

1) Install deps (ideally in a fresh venv):
```bash
pip install -r requirements.txt
```

2) Set your API key:
```bash
setx OPENAI_API_KEY "sk-..."
# or: export OPENAI_API_KEY=...
```

3) Start the server:
```bash
python app.py
```

4) Connect a client (e.g. simple test):
```bash
python client_example.py
# then type messages; assistant replies stream back
```

## Notes

- Voice support (STT/TTS) can be added by running `voice_ptt.py` alongside this server.
- The model calls tools to fetch the **latest** game snapshot and optional **positions** from your CV module.
- See `cv_bus.py` for how to push ally/enemy positions into the shared cache.



## CV integration (ally/enemy positions)

From your CV process (e.g., PyQt + YOLO), push positions into the cache:

```python
# somewhere in your CV loop
from lol_copilot.state_cache import SharedState
from lol_copilot.cv_bus import push_positions

CACHE = SharedState()  # better: import the CACHE instance from app.py if running in same proc

positions = {
  "allies": [
    {"role":"MID", "x":0.52, "y":0.31, "ts": 834},
    {"role":"JNG", "x":0.44, "y":0.62, "ts": 834},
  ],
  "enemies_last_seen": [
    {"champ":"Zed", "x":0.61, "y":0.48, "ts": 820}
  ]
}
push_positions(CACHE, positions)
```

Make sure x,y are normalized to your minimap coordinate system. The assistant will only use these if it calls the `fetch_positions` tool.
