import csv
from datetime import datetime
from moviepy.editor import VideoFileClip
from PIL import Image

import os
import csv
import time
from tqdm import tqdm
from OCR import OCR
from YOLORunner import YOLORunner

from pytube import YouTube
import yt_dlp
# Function to download a single video from a given URL if it contains "jungle" in the title
import matplotlib.pyplot as plt
import pandas as pd
# Example usage
import os
import time

from moviepy.editor import VideoFileClip
from PIL import Image
import pandas as pd
import os
from tqdm import tqdm
import gc
from datetime import datetime
class Master:
    def __init__(self, file_path):
        self.file_path = file_path
        self.video_data = self.read_video_data(file_path)
        self.output_folder = "C:/Users/zadec/Desktop/LOLData/Data"
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        self.yolo = YOLORunner()
        self.ocr = OCR()

    

    def delete_video(self, file_path):
        try:
            # Check if the file exists
            if os.path.isfile(file_path):
                os.remove(file_path)  # Delete the file
                print(f"Deleted video: {file_path}")
            else:
                print(f"File not found: {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")

    
    def read_video_data(self, file_path):
        video_data = []
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) >= 2:  # Ensure there are at least two columns
                    url, date_str = row[0].strip(), row[1].strip()
                    
                    # Check if the row indicates that the URL has been processed
                    if len(row) > 2 and row[2].strip().lower() == "processed":
                        continue  # Skip this URL
                    
                    try:
                        date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                        video_data.append((url, date))
                    except ValueError:
                        print(f"Skipping invalid date format: {date_str}")
        
        return video_data
    def mark_url_as_processed(self, url_to_process):
        updated_data = []
        url_found = False
        
        # Read the current data from the CSV file
        with open(self.file_path, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) >= 2:  # Ensure there are at least two columns
                    url, date_str = row[0].strip(), row[1].strip()
                    # Check if this is the URL we want to mark as processed
                    if url == url_to_process:
                        # Update the row to signal it's processed
                        updated_data.append([url, date_str, "processed"])
                        url_found = True
                    else:
                        updated_data.append(row)

        # Write the updated data back to the CSV file
        with open(self.file_path, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(updated_data)

        if url_found:
            print(f"Marked URL as processed: {url_to_process}")
        else:
            print(f"URL not found: {url_to_process}")

    def download_single_video(self, video_url):
        try:
            
            self.output_folder += '/'

            ydl_opts = {
                'format': 'bestvideo.3',
                'quiet': False,
                'outtmpl': f'{self.output_folder}%(title)s.%(ext)s',  # Set output path
                'merge_output_format': 'mp4'
            }
            
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                filename = ydl.prepare_filename(info)
                #print(f'Downloading: {info["title"]}')
                ydl.download([video_url])
                #print(f'Downloaded: {info["title"]}')
                return filename, info["title"]
                
        except Exception as e:
            #print(f'Error downloading {video_url}: {e}')
            return None
    
    def split_vod(self, video_path, title):
        with VideoFileClip(video_path) as clip:
            all_yolo_results = []
            all_ocr_results = []
            for t in tqdm(range(90, int(clip.duration), 1), desc="Processing Frames"):
                frame_start_time = time.time()  # Start timing for each frame

                # Extract OCR results for the current timestamp
                ocr_start_time = time.time()
                ocr_results = self.ocr.extract_and_crop_frame(clip, t)
                ocr_end_time = time.time()
                # print(f"\n OCR processing time at {t} seconds: {ocr_end_time - ocr_start_time:.2f} seconds")
                
                frame = clip.get_frame(t)
                img = Image.fromarray(frame)
                
                # Crop the minimap image
                minimap_img = img.crop((1640, 800, 1920, 1080))
                
                # Run YOLO on the minimap
                yolo_start_time = time.time()
                yolo_df = self.yolo.run_yolo_on_minimap(minimap_img)
                yolo_end_time = time.time()
                # print(f"\n YOLO processing time at {t} seconds: {yolo_end_time - yolo_start_time:.2f} seconds")

                # Create duplicate columns for YOLO results
                yolo_df['Timestamp'] = t
                ocr_results['Timestamp'] = t

                # Append current yolo_df and ocr_results to the lists
                all_ocr_results.append(ocr_results)
                all_yolo_results.append(yolo_df)

                frame_end_time = time.time()
                print(f"\n Total processing time for frame at {t} seconds: {frame_end_time - frame_start_time:.2f} seconds")
                

            # After the loop, concatenate all results into a single DataFrame
            final_yolo_results_df = pd.concat(all_yolo_results, ignore_index=True)
            final_ocr_results_df = pd.concat(all_ocr_results, ignore_index=True)
            # Save the combined DataFr
            # ame to a CSV file
            final_yolo_results_df.to_csv(os.path.join(self.output_folder, "yolo_results_" + title + ".csv"), index=False)
            final_ocr_results_df.to_csv(os.path.join(self.output_folder, "ocr_results_" + title + ".csv"), index=False)


            
    def run(self):
        for url, date in self.video_data:
            start_time = time.time()
            #print(f"Starting download for URL: {url} at {datetime.now()}")

            path, title = self.download_single_video(url)
            #print(f"Downloaded video: {title} in {time.time() - start_time:.2f} seconds.")

            self.split_vod(path, title)
            #print(f"Processed video: {title} in {time.time() - start_time:.2f} seconds."
            # time.sleep(5)  # Wait before deleting the video

            self.delete_video(path)
            #print(f"Deleted video: {title} in {time.time() - start_time:.2f} seconds.")

            self.mark_url_as_processed(url)
            #print(f"Marked URL as processed: {url} in {time.time() - start_time:.2f} seconds.")
            #print("-" * 40)  # Separator for clarity
            

