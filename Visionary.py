class Visionary:
    

    def process_yolo_results(self, results):
        red_team_locations = []
        red_team_1350 = []
        red_team_1200 = []
        red_team_900 = []
        blue_team_locations = []
        blue_team_1350 = []
        blue_team_1200 = []
        blue_team_900 = []
        for class_id, (class_name, center_x, center_y, width, height) in results.items():
            if 23 <= class_id <= 358: #champions
                # print(f"File: {filename}, Found {class_name} (ID: {class_id}) at ({center_x}, {center_y}) with dimensions {width}x{height}")

                
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
                # print(f"File: {filename}, Found {class_name} (ID: {class_id}) at ({center_x}, {center_y}) with dimensions {width}x{height}")
                
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

