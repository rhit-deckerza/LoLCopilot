import argparse
import datetime as dt
import json
import threading
import time
from pathlib import Path

import cv2
import mss
import numpy as np
import requests

DEFAULT_URL = "https://127.0.0.1:2999/liveclientdata/allgamedata"

def iso_now():
    return dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def record_api(url, out_jsonl, interval=1.0, stop_event=None):
    """
    Poll the Live Client API and write JSONL lines:
    {"t_wall": float, "t_game": float, "data": {...}}
    """
    sess = requests.Session()
    while not (stop_event and stop_event.is_set()):
        t0 = time.monotonic()
        try:
            r = sess.get(url, verify=False, timeout=0.8)
            r.raise_for_status()
            data = r.json()
            t_game = float(data.get("gameData", {}).get("gameTime", 0.0))
            out = {"t_wall": t0, "t_game": t_game, "data": data}
            out_jsonl.write(json.dumps(out) + "\n")
            out_jsonl.flush()
            print(f"[API] t_wall={t0:.3f} t_game={t_game:.1f}")
        except Exception as e:
            # write a marker so playback keeps timing
            out = {"t_wall": t0, "t_game": None, "error": str(e)}
            out_jsonl.write(json.dumps(out) + "\n")
            out_jsonl.flush()
            print(f"[API] error: {e}")
        # sleep remainder
        dt_sleep = interval - (time.monotonic() - t0)
        if dt_sleep > 0:
            time.sleep(dt_sleep)

def record_screen(out_video_path, fps=30, monitor_index=1, region=None):
    """
    Screen record using MSS + OpenCV VideoWriter.
    - monitor_index: 1-based index of the monitor in mss().monitors
    - region: (left, top, width, height) or None for full chosen monitor
    """
    with mss.mss() as sct:
        monitors = sct.monitors
        if monitor_index < 1 or monitor_index >= len(monitors)+1:
            monitor_index = 1
        mon = monitors[monitor_index if monitor_index < len(monitors) else 1]
        if region:
            left, top, width, height = region
        else:
            left, top, width, height = mon["left"], mon["top"], mon["width"], mon["height"]

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        vw = cv2.VideoWriter(str(out_video_path), fourcc, fps, (width, height))

        frame_interval = 1.0 / float(fps)
        print(f"[SCR] Recording {width}x{height} @ {fps}fps to {out_video_path}")
        try:
            while True:
                t0 = time.monotonic()
                img = sct.grab({"left": left, "top": top, "width": width, "height": height})
                frame = np.array(img)  # BGRA
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                vw.write(frame)
                # sleep for fps pacing
                dt_sleep = frame_interval - (time.monotonic() - t0)
                if dt_sleep > 0:
                    time.sleep(dt_sleep)
        except KeyboardInterrupt:
            pass
        finally:
            vw.release()
            print("[SCR] Stopped")

def main():
    ap = argparse.ArgumentParser(description="Record LoL Live Client API + screen video")
    ap.add_argument("--url", default=DEFAULT_URL, help="Live Client API URL")
    ap.add_argument("--outdir", default="recordings", help="Output directory")
    ap.add_argument("--interval", type=float, default=1.0, help="API poll interval seconds")
    ap.add_argument("--fps", type=int, default=30, help="Screen recording FPS")
    ap.add_argument("--monitor", type=int, default=1, help="MSS monitor index (1=primary)")
    ap.add_argument("--region", type=str, default="", help="Optional region 'left,top,width,height'")
    args = ap.parse_args()

    ts = iso_now()
    outdir = Path(args.outdir) / f"session_{ts}"
    outdir.mkdir(parents=True, exist_ok=True)

    jsonl_path = outdir / "liveclientdata.jsonl"
    video_path = outdir / "screen.mp4"

    region = None
    if args.region:
        parts = [int(x.strip()) for x in args.region.split(",")]
        if len(parts) == 4:
            region = tuple(parts)

    stop_event = threading.Event()
    with open(jsonl_path, "w", encoding="utf-8") as jf:
        api_thread = threading.Thread(target=record_api, args=(args.url, jf, args.interval, stop_event), daemon=True)
        api_thread.start()
        try:
            record_screen(video_path, fps=args.fps, monitor_index=args.monitor, region=region)
        except KeyboardInterrupt:
            print("[MAIN] Ctrl+C received, stopping...")
        finally:
            stop_event.set()
            api_thread.join(timeout=2.0)

    print(f"[DONE] Saved API to {jsonl_path}")
    print(f"[DONE] Saved video to {video_path}")

if __name__ == "__main__":
    main()
