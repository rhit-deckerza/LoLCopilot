import os
import cv2
import matplotlib.pyplot as plt
import yaml

# Load class names from the YAML configuration file
config_path = r'C:\Users\zadec\OneDrive\Desktop\CS Projects\LeaugeAIReal\mini_map_detect_v3.yaml'  # Update this path to your YAML config
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

# Get the image and label directories
train_image_dir = config['train']
train_label_dir = os.path.join(train_image_dir[:-7], 'labels')  # Directly reference the 'labels' directory

# Initialize a dictionary to hold examples for each label ID
label_examples = {}

# Loop through each label file in the labels directory
for label_file in os.listdir(train_label_dir):
    if label_file.endswith('.txt'):
        label_path = os.path.join(train_label_dir, label_file)
        image_name = label_file.replace('.txt', '.png')  # Assuming png format
        image_path = os.path.join(train_image_dir, image_name)
        
        if os.path.exists(image_path):
            with open(label_path, 'r') as f:
                for line in f:
                    line = line.strip()  # Remove leading/trailing whitespace
                    if line:  # Only process non-empty lines
                        # print("here:", line, label_path)
                        label_id = int(line.split()[0])  # Get the label ID
                        if label_id not in label_examples:
                            label_examples[label_id] = (image_path, line)

# Prepare to plot images
num_labels = len(label_examples)
print(f'Number of labels found: {num_labels}')

# Calculate grid size
grid_size = int(num_labels**0.5) + (num_labels % 2 > 0)  # Square root to create a grid
fig, axs = plt.subplots(grid_size, grid_size, figsize=(15, 15))

# Flatten the axes array for easy indexing
axs = axs.flatten()

for ax, (label_id, (img_path, bbox_info)) in zip(axs, label_examples.items()):
    # Read the image
    img = cv2.imread(img_path)

    # Get bounding box coordinates
    _, center_x, center_y, width, height = map(float, bbox_info.split())
    h, w, _ = img.shape
    x1 = int((center_x - width / 2) * w)
    y1 = int((center_y - height / 2) * h)
    x2 = int((center_x + width / 2) * w)
    y2 = int((center_y + height / 2) * h)

    # Crop the image to the bounding box
    cropped_img = img[y1:y2, x1:x2]

    # Display the cropped image
    ax.imshow(cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB))
    ax.set_title(config["names"][label_id])  # Only display the label name
    ax.axis('off')

# Hide any remaining empty subplots
for i in range(len(label_examples), len(axs)):
    axs[i].axis('off')

plt.tight_layout()
plt.show()
