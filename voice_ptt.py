"""Optional push-to-talk client using local mic (simple; not Realtime/WebRTC).
- Press Enter to record 4s, release to send.
- Plays TTS response audio locally.
"""
import io, os, sys, time
import sounddevice as sd
import soundfile as sf
import numpy as np
from openai import OpenAI
from config import OPENAI_API_KEY, GPT_MODEL, TTS_MODEL
from system_prompt import SYSTEM_PROMPT

RATE = 16000
CH = 1

def record(seconds=4):
    audio = sd.rec(int(seconds*RATE), samplerate=RATE, channels=CH, dtype="float32")
    sd.wait()
    with io.BytesIO() as buf:
        sf.write(buf, audio, RATE, format="WAV", subtype="PCM_16")
        return buf.getvalue()

def transcribe(client, wav_bytes):
    r = client.audio.transcriptions.create(model="whisper-1", file=("speech.wav", wav_bytes, "audio/wav"))
    return r.text

def speak(client, text):
    speech = client.audio.speech.create(model=TTS_MODEL, voice="verse", input=text, format="wav")
    wav_bytes = speech.read()
    data, sr = sf.read(io.BytesIO(wav_bytes), dtype="float32")
    sd.play(data, sr); sd.wait()

def ask(client, text):
    resp = client.responses.create(model=GPT_MODEL,
        input=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":text}],
        temperature=0.2, verbosity="low", reasoning={"effort":"minimal"})
    return resp.output_text

def main():
    if not OPENAI_API_KEY: raise RuntimeError("OPENAI_API_KEY not set")
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("Push-to-talk: press Enter to speak for 4s… (Ctrl+C to quit)")
    while True:
        input()
        wav = record(4)
        text = transcribe(client, wav).strip()
        if not text: continue
        print("You:", text)
        reply = ask(client, text)
        print("GPT-5:", reply)
        speak(client, reply)

if __name__ == "__main__":
    main()
