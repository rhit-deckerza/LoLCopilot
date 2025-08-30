from ultralytics import YOLO
import torch

if __name__ == '__main__':
   print(torch.cuda.is_available())

   # Load the model.
   model = YOLO('yolov8n.pt')

   # Training.
   results = model.train(
      data='mini_map_detect_v3.yaml',
      imgsz=280,
      epochs=50,
      batch=32,
      name='yolov8n_mini_map_detect_v3_50e',
      device='0'  # Use '0' for the first GPU, or use 'cpu' for CPU training
   )
