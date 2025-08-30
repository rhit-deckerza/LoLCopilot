import os
from tqdm import tqdm

def process_yolo_labels(directory):
    # Walk through the directory and its subdirectories
    for root, _, files in os.walk(directory):
        # Filter only text files
        txt_files = [file for file in files if file.endswith('.txt')]
        
        # Use tqdm to display a loading bar
        for file in tqdm(txt_files, desc='Processing files', unit='file'):
            file_path = os.path.join(root, file)
            process_file(file_path)

def process_file(file_path):
    new_lines = []
    with open(file_path, 'r') as f:
        for line in f:
            # Split the line into components
            parts = line.strip().split()
            if len(parts) < 5:
                continue  # Skip lines that don't have enough parts

            # Parse the class ID
            class_id = int(parts[0])
            
            # Check if the class ID is within the valid range
            if 24 <= class_id <= 191:
                # Subtract 24 from the class ID
                new_class_id = class_id - 24
                # Append the modified line to the new lines list
                new_lines.append(f"{new_class_id} {' '.join(parts[1:])}\n")

    # Write the filtered and updated labels back to the file
    if new_lines:
        with open(file_path, 'w') as f:
            f.writelines(new_lines)

if __name__ == '__main__':
    directory_path = r'C:\Users\zadec\OneDrive\Desktop\LOLData\Generated_Maps'  # Replace with your directory path
    process_yolo_labels(directory_path)
