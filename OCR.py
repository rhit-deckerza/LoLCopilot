from concurrent.futures import ThreadPoolExecutor
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import easyocr

class OCR:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=True) 
    
    def scale_coords(self, x1, y1, x2, y2, width, height):
        """Scales coordinates based on video frame size."""
        scale_x = width / 1280
        scale_y = height / 780
        return (
            int(x1 * scale_x),
            int(y1 * scale_y),
            int(x2 * scale_x),
            int(y2 * scale_y)
        )

    def preprocess_frame(self, frame):
        """Preprocess the entire frame before cropping."""
        # Grayscale conversion
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Upscaling
        upscaled_frame = cv2.resize(gray_frame, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        # Apply blur
        blurred_frame = cv2.blur(upscaled_frame, (5, 5))
        return blurred_frame

    def process_crop(self, crop_coords, frame, index):
        """Process a single crop region for OCR."""
        left, top, right, bottom = crop_coords
        cropped_img = frame[top:bottom, left:right]
        results = self.reader.readtext(cropped_img, text_threshold=0.3)
        
        if results:
            text = results[0][1]
            confidence = results[0][2]
        else:
            text = 0
            confidence = 0
        
        return (text, confidence)

    def extract_and_crop_frame(self, clip, t):
        """Extract and crop regions from video frame and perform OCR."""
        frame = clip.get_frame(t)
        height, width = frame.shape[:2]

        # CS and KDA coordinates (5x2 grid)
        cs_coords = [(680 + col * -90, 575 + row * 31 + 50, 700 + col * -90, 590 + row * 31 + 50)
                     for row in range(5) for col in range(2)]
        kda_coords = [(705 + col * -165, 575 + row * 31 + 50, 750 + col * -165, 590 + row * 31 + 50)
                      for row in range(5) for col in range(2)]

        # Scale coordinates based on frame size
        all_coords = [self.scale_coords(*coords, width, height) for coords in cs_coords + kda_coords]

        # Preprocess the entire frame before extracting crops
        preprocessed_frame = self.preprocess_frame(frame)

        # Set up a thread pool for concurrent processing of crops
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda idx: self.process_crop(all_coords[idx], preprocessed_frame, idx), range(len(all_coords))))

        # Prepare data for DataFrame
        cs_values, confidence_cs_list, k_values, d_values, a_values, confidence_kda_list = [], [], [], [], [], []
        
        for i, (text, confidence) in enumerate(results):
            if 1 <= i <= 10:  # CS
                cs_values.append(text)
                confidence_cs_list.append(confidence)
            elif 11 <= i <= 20:  # KDA
                if text != 0:
                    kda = text.split("/")
                    k_values.append(kda[0] if len(kda) > 0 else 0)
                    d_values.append(kda[1] if len(kda) > 1 else 0)
                    a_values.append(kda[2] if len(kda) > 2 else 0)
                else:
                    k_values.append(0)
                    d_values.append(0)
                    a_values.append(0)
                confidence_kda_list.append(confidence)

        # Organize results into a DataFrame
        max_length = max(len(cs_values), len(k_values), len(d_values), len(a_values))
        data = {
            'CS Values': cs_values + [None] * (max_length - len(cs_values)),
            'CS Confidences': confidence_cs_list + [None] * (max_length - len(confidence_cs_list)),
            'K Values': k_values + [None] * (max_length - len(k_values)),
            'D Values': d_values + [None] * (max_length - len(d_values)),
            'A Values': a_values + [None] * (max_length - len(a_values)),
            'KDA Confidences': confidence_kda_list + [None] * (max_length - len(confidence_kda_list)),
        }

        df = pd.DataFrame(data)
        return df
