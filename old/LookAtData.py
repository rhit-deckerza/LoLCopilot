import pandas as pd
from collections import Counter

# Load the CSV file
file_path = r"C:\Users\zadec\OneDrive\Desktop\LOLData\Data\yolo_results_Aurora Carry vs Kai'Sa - EUW Master Patch 14.14.csv"
df = pd.read_csv(file_path)

# Count the occurrences of each label across the entire DataFrame
label_counts = Counter(df['Label'])
most_common_labels = label_counts.most_common(10)

# Print the 10 most common labels
print("Overall 10 Most Common Labels:")
for label, count in most_common_labels:
    print(f"Label: {label}, Count: {count}")
