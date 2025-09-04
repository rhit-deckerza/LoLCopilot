import os

# ---- OpenAI / Models ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-5")          # or: gpt-5-mini
TTS_MODEL = os.getenv("TTS_MODEL", "gpt-4o-mini-tts")  # speech model name

# ---- Live Client API ----
LIVE_CLIENT_URL = os.getenv("LIVE_CLIENT_URL", "https://127.0.0.1:2999/liveclientdata/allgamedata")
LIVE_CLIENT_VERIFY_SSL = False  # riot uses a self-signed cert locally

# ---- Server ----
WS_HOST = os.getenv("WS_HOST", "127.0.0.1")
WS_PORT = int(os.getenv("WS_PORT", 8765))

# ---- Summarizer / Limits ----
MAX_ITEM_COUNT = 6
