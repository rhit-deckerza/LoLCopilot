import asyncio, json, os, traceback
import websockets
from openai import OpenAI
from config import OPENAI_API_KEY, GPT_MODEL, WS_HOST, WS_PORT
from state_cache import SharedState
from live_client_poller import LiveClientPoller
from system_prompt import SYSTEM_PROMPT
from tools import make_tools_spec, handle_tool_call

# Shared cache populated by the poller and CV
CACHE = SharedState()


async def stream_gpt5(message_text: str):
    r"""Yield assistant chunks using OpenAI Responses streaming with tool-calls handled inline."""
    client = OpenAI(api_key=OPENAI_API_KEY)

    # We'll run the blocking streaming loop in a thread and push deltas into an asyncio.Queue
    queue = asyncio.Queue()

    def run_stream():
        try:
            with client.responses.stream(
                model=GPT_MODEL,
                input=[
                    { "role": "system", "content": SYSTEM_PROMPT },
                    { "role": "user", "content": message_text },
                ],
                tools=make_tools_spec(),
                temperature=0.2,
                verbosity="low",
                reasoning={"effort": "minimal"},
            ) as stream:
                for event in stream:
                    et = getattr(event, "type", "")
                    if et == "response.output_text.delta":
                        queue.put_nowait(event.delta)
                    elif et == "response.function_call":
                        name = event.name
                        args_json = event.arguments or "{}"
                        try:
                            tool_result = handle_tool_call(CACHE, name, args_json)
                        except Exception as e:
                            tool_result = f"ERROR calling tool {name}: {e}"
                        stream.input.append({"role":"tool","content":tool_result,"name":name})
                    elif et == "response.error":
                        queue.put_nowait("\n[error] " + str(event.error))
                # finalize
        except Exception as e:
            queue.put_nowait("\n[stream error] " + str(e))
        finally:
            queue.put_nowait(None)  # sentinel

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, run_stream)

    while True:
        chunk = await queue.get()
        if chunk is None:
            break
        yield chunk

async def handle_client(ws):
    await ws.send(json.dumps({"type":"hello","msg":"LoL Copilot ready"}))
    async for raw in ws:
        try:
            data = json.loads(raw)
            if data.get("type") == "user_text":
                text = data.get("text","").strip()
                if not text:
                    await ws.send(json.dumps({"type":"assistant_text","delta":"(empty)"}))
                    continue
                async for chunk in stream_gpt5(text):
                    await ws.send(json.dumps({"type":"assistant_text","delta":chunk}))
            else:
                await ws.send(json.dumps({"type":"error","msg":"unknown message type"}))
        except Exception as e:
            await ws.send(json.dumps({"type":"error","msg":str(e)}))

async def main():
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")
    # start live client poller in a background thread
    poller = LiveClientPoller(lambda raw, summary: CACHE.set_game(raw, summary))
    poller.start()
    async with websockets.serve(handle_client, WS_HOST, WS_PORT, ping_interval=20):
        print(f"WebSocket server on ws://{WS_HOST}:{WS_PORT}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        import uvloop, platform
        if platform.system() != "Windows":
            uvloop.install()
    except Exception:
        pass
    asyncio.run(main())
