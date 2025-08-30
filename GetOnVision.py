import os
import cv2
import numpy as np

CONVERSION_RATE = 0.04
import numpy as np
import cv2
def is_line_unobstructed(image, circle1, circle2, output_image):
    # Extract circle parameters
    center1, radius1 = circle1
    center2, radius2 = circle2

    # Convert normalized coordinates to pixel coordinates
    
    
    # Create a mask from the image's alpha channel
    if image.shape[2] == 4:  # Check if the image has an alpha channel
        mask = image[:, :, 3]
        # print(mask)
        # Save the mask as a debug image
        # cv2.imwrite('mask_debug.png', mask)
    else:
        mask = np.ones(image.shape[:2], dtype=np.uint8) * 255  # If no alpha, assume fully opaque
        # Save the mask as a debug image
        # cv2.imwrite('mask_debug.png', mask)

    # Draw the circles on the output image
    cv2.circle(output_image, center1, radius1, (255, 255, 255), 1)  # Draw circle1 in green
    cv2.circle(output_image, center2, radius2, (255, 255, 255), 1)  # Draw circle2 in red
    
    # Check points on circle1
    for angle in np.linspace(0, 2 * np.pi, 100):
        point1 = (int(center1[0] + radius1 * np.cos(angle)), int(center1[1] + radius1 * np.sin(angle)))
        
        # Check points on circle2
        for angle2 in np.linspace(0, 2 * np.pi, 100):
            point2 = (int(center2[0] + radius2 * np.cos(angle2)), int(center2[1] + radius2 * np.sin(angle2)))
            
            # Create a line from point1 to point2
            line_mask = np.zeros_like(mask)
            cv2.line(line_mask, point1, point2, 255, 1)
            
            # Check for obstruction
            if np.all(mask[line_mask == 255] < 255):
                # Draw the line on the output image only if it's unobstructed
                cv2.line(output_image, point1, point2, (255, 0, 0), 1)  # Draw line in blue
                return True, output_image  # Unobstructed line found
            # else:
                # print("obstructed")
    
    return False, output_image  # All lines obstructed

def is_on_vision(image, location, opposite_team_1350, opposite_team_1200, opposite_team_900, output_image):
    # Adjust this value based on your desired pixel threshold
    height, width = image.shape[:2]
    location = (int(location[0] * width), int(location[1] * height))
    
    # Draw circle for the main location
    cv2.circle(output_image, location, 10, (0, 255, 0), 2)  # Green circle for main location
    
    for loc in opposite_team_1350:
        loc = (int(loc[0] * width), int(loc[1] * height))
        
        threshold = int(1350 * CONVERSION_RATE)
        cv2.circle(output_image, loc, threshold, (255, 0, 0), 2)  # Blue circle for 1350 threshold
        
        if abs(location[0] - loc[0]) <= threshold and abs(location[1] - loc[1]) <= threshold:
            print(loc)
            print(location)
            print("1")
            line_is_unobstructed, output_image = is_line_unobstructed(image, (location, 10), (loc, 10), output_image)
            if line_is_unobstructed:
                return True, output_image
    
    for loc in opposite_team_1200:
        loc = (int(loc[0] * width), int(loc[1] * height))
        threshold = int(1200 * CONVERSION_RATE)
        cv2.circle(output_image, loc, threshold, (0, 255, 255), 2)  # Yellow circle for 1200 threshold
        
        if abs(location[0] - loc[0]) <= threshold and abs(location[1] - loc[1]) <= threshold:
            print("2")
            line_is_unobstructed, output_image = is_line_unobstructed(image, (location, 10), (loc, 5), output_image)
            if line_is_unobstructed:
                return True, output_image
    
    for loc in opposite_team_900:
        loc = (int(loc[0] * width), int(loc[1] * height))
        threshold = int(900 * CONVERSION_RATE)
        cv2.circle(output_image, loc, threshold, (0, 0, 255), 2)  # Red circle for 900 threshold
        
        if abs(location[0] - loc[0]) <= threshold and abs(location[1] - loc[1]) <= threshold:
            print("3")
            line_is_unobstructed, output_image = is_line_unobstructed(image, (location, 10), (loc, 1), output_image)
            if line_is_unobstructed:
                return True, output_image
    
    return False, output_image


        

# Example usage
# image = cv2.imread('image.png')
# circle1 = (center1, radius1)
# circle2 = (center2, radius2)
# target_color = np.array([0, 0, 255])  # Example: red color in BGR
# unobstructed = is_line_unobstructed(image, circle1, circle2, target_color)


# Load the class names from the text file
class_names = {}
with open(r"D:\LOLData\champion_ids.txt", 'r') as file:
    for line in file:
        name, id_str = line.strip().split(': ')
        class_names[int(id_str)] = name

# Path to the directory containing annotation files
annotations_dir = "D:\LOLData\ExampleAnnotationPair"

# Lists to store locations based on champion name endings
red_team_locations = []
red_team_1350 = []
red_team_1200 = []
red_team_900 = []
blue_team_locations = []
blue_team_1350 = []
blue_team_1200 = []
blue_team_900 = []

# Iterate through all text files in the annotations directory
for filename in os.listdir(annotations_dir):
    if filename.endswith('.txt'):
        file_path = os.path.join(annotations_dir, filename)
        
        with open(file_path, 'r') as annotation_file:
            annotations = annotation_file.readlines()

        for annotation in annotations:
            parts = annotation.strip().split()
            if len(parts) == 5:  # Ensure the annotation has the correct number of parts
                class_id = int(parts[0])
                # Extract object information
                center_x, center_y, width, height = map(float, parts[1:])
                
                # Get the class name from the dictionary
                class_name = class_names.get(class_id, "Unknown")
                if 23 <= class_id <= 358: #champions
                    print(f"File: {filename}, Found {class_name} (ID: {class_id}) at ({center_x}, {center_y}) with dimensions {width}x{height}")

                    
                    # Check the ending of the champion name and add to appropriate list
                    if class_name.endswith('R'):
                        red_team_locations.append((class_name, (center_x, center_y)))
                        red_team_1350.append((center_x, center_y))
                    elif class_name.endswith('B'):
                        blue_team_locations.append((class_name, (center_x, center_y)))
                        blue_team_1350.append((center_x, center_y))
                    
                    # Print the object's information including the class name
                if 21 == class_id: #towers
                    # Extract object informatio
                    print(f"File: {filename}, Found {class_name} (ID: {class_id}) at ({center_x}, {center_y}) with dimensions {width}x{height}")
                    
                    # Check if the object is in the bottom left half of the image
                    if center_y > 0.5 and center_x < 0.5:
                        blue_team_1350.append((center_x, center_y))
                    else:
                        red_team_1350.append((center_x, center_y))
                if 3 == class_id: #supers
                    blue_team_1350.append((center_x, center_y))
                if 18 == class_id:
                    red_team_1350.append((center_x, center_y))
                if 2 == class_id: #minon
                    blue_team_1200.append((center_x, center_y))
                if 17 == class_id:
                    red_team_1200.append((center_x, center_y))
                if 4 == class_id:
                    blue_team_900.append((center_x, center_y))
                if 19 == class_id:
                    red_team_900.append((center_x, center_y))


image_path = "D:\LOLData\MapMask.png"
image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
output_image_path = "D:\LOLData\ExampleAnnotationPair\map_1.png"
output_image_path2 = "D:\LOLData\log"
output_image = cv2.imread(output_image_path, cv2.IMREAD_UNCHANGED)

coutn = 0
for champion_location in red_team_locations:
    print(champion_location[0])
    veritas, output_image = is_on_vision(image, champion_location[1], blue_team_1350, blue_team_1200, blue_team_900, output_image)
    print(veritas)
    cv2.imwrite(output_image_path2 + str(coutn) + ".png", output_image)
    coutn += 1
    

# Print the results
print("Red Team Locations:", red_team_locations)
print("Blue Team Locations:", blue_team_locations)

# Note: Make sure to replace 'path/to/annotations/directory' with the actual path to your annotations directory
