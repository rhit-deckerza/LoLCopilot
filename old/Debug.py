import os
import csv
import time
from datetime import datetime

import yt_dlp
from moviepy.editor import VideoFileClip
from PIL import Image
import pandas as pd
from tqdm import tqdm

# Assuming you already have these classes implemented similarly:
from OCR import OCR
from YOLORunner import YOLORunner


def debug_single_video(video_url,
                       debug_base_folder=r"C:/Users/zadec/Desktop/LOLData/Debug",
                       start_second=90,
                       step=1):
    """
    Downloads a single video from `video_url`, processes each second from `start_second` to the end,
    and saves all artifacts (frames, minimap images, CSV results) into a debug folder.

    :param video_url: URL of the YouTube video to download and process.
    :param debug_base_folder: Base folder where debug subfolders are created.
    :param start_second: The second at which to start processing frames.
    :param step: Number of seconds to step between each processed frame.
    """

    # 1. Download the video
    ydl_opts = {
        'format': 'bestvideo.3',  # or the format you prefer
        'quiet': False,           # Set to True if you want less console output
        'outtmpl': os.path.join(debug_base_folder, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4'
    }

    downloaded_file_path = None
    video_title = None

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            downloaded_file_path = ydl.prepare_filename(info)
            video_title = info.get("title", "unknown_title")
            print(f"Downloaded file path: {downloaded_file_path}")
            print(f"Video Title: {video_title}")
    except Exception as e:
        print(f"Error downloading video: {e}")
        return

    # 2. Create debug folder for this video
    #    We add a suffix "_debug" to the video title, but sanitize it if needed.
    safe_title = "".join(c for c in video_title if c.isalnum() or c in " _-()[]")
    debug_folder = os.path.join(debug_base_folder, f"{safe_title}_debug")
    os.makedirs(debug_folder, exist_ok=True)

    # 3. Initialize your OCR and YOLO classes
    ocr = OCR()
    yolo = YOLORunner()

    # 4. Open the video with MoviePy
    all_ocr_results = []
    all_yolo_results = []

    try:
        with VideoFileClip(downloaded_file_path) as clip:
            total_duration = int(clip.duration)
            print(f"Video Duration: {total_duration}s")

            # Process frames from `start_second` to the end, stepping by `step` seconds
            for t in tqdm(range(start_second, total_duration, step), desc="Processing Frames"):
                frame_start_time = time.time()

                # Grab the frame at time t
                frame = clip.get_frame(t)
                frame_img = Image.fromarray(frame)

                # 4A. Save the full frame for debug (the same frame used for OCR)
                frame_save_path = os.path.join(debug_folder, f"frame_{t}.jpg")
                frame_img.save(frame_save_path, "JPEG")

                # 4B. OCR
                # Call your OCR method
                ocr_results = ocr.extract_and_crop_frame(clip, t)
                # Add a 'Timestamp' column to OCR results
                ocr_results['Timestamp'] = t
                # For debug, also save the OCR results as a small CSV at each step
                ocr_step_csv_path = os.path.join(debug_folder, f"ocr_{t}.csv")
                ocr_results.to_csv(ocr_step_csv_path, index=False)
                all_ocr_results.append(ocr_results)

                # 4C. YOLO on minimap
                # Crop the minimap portion from the frame
                # Adjust these coordinates to match your actual minimap location
                minimap_img = frame_img.crop((1640, 800, 1920, 1080))

                # For debug, save the minimap image
                minimap_save_path = os.path.join(debug_folder, f"minimap_{t}.jpg")
                minimap_img.save(minimap_save_path, "JPEG")

                # Run YOLO on the cropped minimap
                yolo_df = yolo.run_yolo_on_minimap(minimap_img)
                # Add a 'Timestamp' column
                yolo_df['Timestamp'] = t
                # For debug, also save the YOLO results as a small CSV at each step
                yolo_step_csv_path = os.path.join(debug_folder, f"yolo_{t}.csv")
                yolo_df.to_csv(yolo_step_csv_path, index=False)
                all_yolo_results.append(yolo_df)

                frame_end_time = time.time()
                print(f"Frame {t} processed. Time taken: {frame_end_time - frame_start_time:.2f}s")

        # 5. After all frames processed, concatenate and save final CSV
        final_ocr_results_df = pd.concat(all_ocr_results, ignore_index=True)
        final_yolo_results_df = pd.concat(all_yolo_results, ignore_index=True)

        final_ocr_results_csv_path = os.path.join(debug_folder, f"final_ocr_results_{safe_title}.csv")
        final_yolo_results_csv_path = os.path.join(debug_folder, f"final_yolo_results_{safe_title}.csv")

        final_ocr_results_df.to_csv(final_ocr_results_csv_path, index=False)
        final_yolo_results_df.to_csv(final_yolo_results_csv_path, index=False)

        print("\nDebug processing complete!")
        print(f"Final OCR results saved to: {final_ocr_results_csv_path}")
        print(f"Final YOLO results saved to: {final_yolo_results_csv_path}")
        print(f"All frame/minimap images and per-frame CSVs are in: {debug_folder}")

    except Exception as e:
        print(f"Error while processing the video: {e}")
    # No deletion of the video for debugging - so you have everything to inspect.

# ------------------- USAGE EXAMPLE -------------------
if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=EXAMPLE"  # Replace with your actual video URL
    debug_single_video(test_url)
