import asyncio, json, websockets, sys

async def run():
    uri = "ws://127.0.0.1:8765"
    async with websockets.connect(uri) as ws:
        hello = await ws.recv()
        print("<<", hello)
        print("Type a message and press Enter (Ctrl+C to exit).")
        while True:
            user = input("> ")
            await ws.send(json.dumps({"type":"user_text","text":user}))
            # stream reply until a short idle gap (crude)
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                if data.get("type") == "assistant_text":
                    sys.stdout.write(data.get("delta",""))
                    sys.stdout.flush()
                    # stop on newline heuristics
                    if data.get("delta","").endswith("\n"):
                        break
                else:
                    print("\n<<", data)
                    break

if __name__ == "__main__":
    asyncio.run(run())
