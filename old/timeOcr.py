import time
from moviepy.editor import VideoFileClip
import pandas as pd
from OCR import OCR
# Your OCR class code goes here (as defined earlier)

# Define a function to time the execution of extract_and_crop_frame
def time_function_execution():
    # Load a sample video (replace with your actual video path)
    clip = VideoFileClip(r"C:\Users\zadec\Downloads\3195394-uhd_3840_2160_25fps.mp4")

    # Create an instance of the OCR class
    ocr = OCR()

    # Choose a time point (t) in the video to test
    t = 10  # Change to any time in the video you want to analyze (in seconds)

    # Time the function
    start_time = time.time()
    
    # Call the method you want to time
    df = ocr.extract_and_crop_frame(clip, t)

    # Calculate the time taken
    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Execution time for extracting and cropping the frame: {execution_time:.4f} seconds")

    # Optionally, save the DataFrame to a CSV or do further processing
    # df.to_csv('output.csv', index=False)

# Run the timing function
time_function_execution()
