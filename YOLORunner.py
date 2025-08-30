import csv
from datetime import datetime
from moviepy.editor import VideoFileClip
from PIL import Image
import cv2
import numpy as np
import os
import csv
from OCR import OCR
import easyocr
import requests
from pytube import YouTube
from ultralytics import YOLO
import pandas as pd
import matplotlib.pyplot as plt
class YOLORunner:

    def __init__(self):
        self.model = YOLO('best.pt', verbose=False)


    def run_yolo_on_minimap(self, minimap_img):
        # Convert PIL Image to a format suitable for YOLOv8
        minimap_cv = np.array(minimap_img)
        
        # If using OpenCV, convert BGR to RGB
        minimap_cv = cv2.cvtColor(minimap_cv, cv2.COLOR_BGR2RGB)

        # Run inference
        results = self.model(minimap_cv)
        # print("YOLO Results:", results)  # Debug: Check the structure of the results

        # Check if results have the boxes object
        results_new = {}
        for result in results[0].boxes.data:
            x1, y1, x2, y2, conf, cls = result  # Extract box coordinates and class info
            x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))  # Convert to integers
            if (int(cls) >= 24):
                results_new[int(cls)] = (self.model.names[int(cls)], float(conf), x1, y1, x2, y2)
        
        # Convert results_new to a DataFrame
        df_results = pd.DataFrame.from_dict(results_new, orient='index', 
                                            columns=['Label', 'Confidence', 'X1', 'Y1', 'X2', 'Y2'])

        # Reset index to have a cleaner DataFrame
        df_results.reset_index(inplace=True)
        df_results.rename(columns={'index': 'Class ID'}, inplace=True)

        return df_results
    
    
