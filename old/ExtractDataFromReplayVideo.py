from moviepy.editor import VideoFileClip
from PIL import Image
import cv2
import numpy as np
import os
import csv
import easyocr

def extract_and_crop_frames(video_path, output_folder, crop_coords1=None, crop_coords2=None, crop_coords3=None, crop_coords4=None, perform_ocr=True):
    if perform_ocr:
        interval = 1
    else:
        interval = 10

    # Load the video
    clip = VideoFileClip(video_path)
    
    # Create the output directory if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Initialize the OCR reader if OCR is to be performed
    reader = easyocr.Reader(['en']) if perform_ocr else None

    # Prepare CSV file for OCR results if OCR is to be performed
    csv_file = os.path.join(output_folder, "ocr_results.csv") if perform_ocr else None
    if perform_ocr:
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'CS', 'Kills', 'Deaths', 'Assists', 'Confidence_Timestamp', 'Confidence_CS', 'Confidence_KDA'])
    
    # Iterate through each second of the video
    for t in range(0, int(clip.duration), interval):
        try:
            frame = clip.get_frame(t)
            img = Image.fromarray(frame)
            
            if perform_ocr:
                timestamp = 0
                cs = k = d = a = "0"
                confidence_timestamp = confidence_cs = confidence_kda = 0
                
                # Process each crop region for OCR
                for i, crop_coords in enumerate([crop_coords1, crop_coords2, crop_coords4], 1):
                    if crop_coords:
                        left, top, right, bottom = crop_coords
                        cropped_img = img.crop((left, top, right, bottom))
                        cropped_img = cropped_img.convert('L')
                        
                        img_cropped = np.array(cropped_img)
                        scale_factor = 2
                        upscaled = cv2.resize(img_cropped, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
                        blur = cv2.blur(upscaled, (5, 5))
                        results = reader.readtext(blur, text_threshold=0.3)
                        print(f"OCR Results for region {i}: {results}")

                        if i == 1:  # Timestamp
                            timestamp_str = results[0][1].replace("o", "0").replace("I", "1")
                            splitTimestamp = timestamp_str.split(":" if ":" in timestamp_str else ".")
                            timestamp = int(splitTimestamp[0]) * 60 + int(splitTimestamp[1])
                            confidence_timestamp = results[0][2]
                        elif i == 2:  # CS
                            cs = results[0][1]
                            confidence_cs = results[0][2]
                        elif i == 3:  # KDA
                            kda = results[0][1].split("/")
                            k, d, a = kda
                            confidence_kda = results[0][2]

                # Write to CSV
                with open(csv_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamp, cs, k, d, a, confidence_timestamp, confidence_cs, confidence_kda])

            # Save minimap image regardless of OCR setting
            if crop_coords3:
                left, top, right, bottom = crop_coords3
                minimap_img = img.crop((left, top, right, bottom))
                frame_image = os.path.join(output_folder, f"minimap_{t}.png")
                minimap_img.save(frame_image)
                print(f"Saved {frame_image}")

        except Exception as e:
            print(f"Error processing frame at time {t}: {str(e)}")
            if perform_ocr:
                with open(csv_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([t, 0, 0, 0, 0, 0, 0, 0])

    print("Frame extraction" + (" and OCR text extraction" if perform_ocr else "") + " complete.")

def process_videos_in_folder(input_folder, output_base_folder, crop_coords1=None, crop_coords2=None, crop_coords3=None, crop_coords4=None, perform_ocr=True):
    # Iterate through each video file in the input folder
    for video_file in os.listdir(input_folder):
        if video_file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):  # Add more extensions if needed
            video_path = os.path.join(input_folder, video_file)
            video_name, _ = os.path.splitext(video_file)
            output_folder = os.path.join(output_base_folder, video_name)
            
            print(f"Processing {video_file}...")
            extract_and_crop_frames(video_path, output_folder, crop_coords1, crop_coords2, crop_coords3, crop_coords4, perform_ocr)

# Example usage
input_folder = r"D:\LOLData\Replays"
output_base_folder = r"D:\LOLData\Replays"

# Define crop coordinates (left, top, right, bottom)
crop_coords1 = (930, 70, 1000, 100)    # Timestamp region
crop_coords2 = (1020, 900, 1060, 940)  # CS region
crop_coords3 = (1640, 800, 1920, 1080) # Minimap region
crop_coords4 = (1060, 900, 1150, 940)  # KDA region

# Set perform_ocr to False to only save minimap images without OCR and CSV creation
process_videos_in_folder(input_folder, output_base_folder, crop_coords1=crop_coords1, crop_coords2=crop_coords2, crop_coords3=crop_coords3, crop_coords4=crop_coords4, perform_ocr=True)
