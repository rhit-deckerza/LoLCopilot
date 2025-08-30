import sys
import numpy as np
import cv2
import win32gui
import win32ui
import win32con
from ctypes import windll
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPixmap, QPainter, QPen, QFont
from ultralytics import YOLO

print("Imports completed successfully")

class YOLOWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.model = YOLO('best.pt')  # or your specific model path
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_yolo)
        self.timer.start(30)  # Run YOLO every 30 ms
        self.canvas = QPixmap(self.rect().size())  # Initialize the canvas
        self.window_name = "League of Legends (TM) Client"  # Replace with the actual window name
        self.box_size = 280
        self.frame_count = 0  # Initialize frame counter
        print("YOLOWindow initialized")

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)  # Set a fixed size for the YOLO window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) 
        self.setAttribute(Qt.WA_TranslucentBackground)  # Make the window background transparent
        self.show()
        print("YOLOWindow UI initialized")

    def capture_win_alt(self, window_name: str):
        windll.user32.SetProcessDPIAware()
        hwnd = win32gui.FindWindow(None, window_name)

        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        w = right - left
        h = bottom - top

        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, w, h)
        save_dc.SelectObject(bitmap)

        result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)

        bmpinfo = bitmap.GetInfo()
        bmpstr = bitmap.GetBitmapBits(True)

        img = np.frombuffer(bmpstr, dtype=np.uint8).reshape((bmpinfo["bmHeight"], bmpinfo["bmWidth"], 4))
        img = np.ascontiguousarray(img)[..., :-1]  # make image C_CONTIGUOUS and drop alpha channel

        if not result:  # result should be 1
            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)
            raise RuntimeError(f"Unable to acquire screenshot! Result: {result}")

        return img

    def run_yolo(self):
        print("Starting YOLOv8 detection...")
        hwnd = win32gui.FindWindow(None, self.window_name)
        if hwnd == 0:
            print(f"Window '{self.window_name}' not found!")
            return

        window_rect = win32gui.GetWindowRect(hwnd)
        width = window_rect[2] - window_rect[0]
        height = window_rect[3] - window_rect[1]

        # Update the position and size of the YOLOWindow to match the target window
        self.setGeometry(window_rect[0], window_rect[1], width, height)

        # Capture the window using the new method
        screen = self.capture_win_alt(self.window_name)
        print("Window captured successfully")

        # Save the image after every 100 frames
        self.frame_count += 1
        if self.frame_count % 100 == 0:
            cv2.imwrite(f'screenshot_{self.frame_count}.png', screen)
            print(f"Saved screenshot_{self.frame_count}.png")

        # Crop the image to 512x512 from the bottom right
        start_y = height - self.box_size
        start_x = width - self.box_size
        cropped_screen = screen[start_y:, start_x:]

        # Run YOLOv8 inference on the captured screen area
        results = self.model(cropped_screen)
        print(f"YOLOv8 inference completed. Detections: {len(results[0])}")

        # Create a transparent canvas
        self.canvas = QPixmap(self.rect().size())  # Update the canvas
        self.canvas.fill(Qt.transparent)

        # Draw on the canvas
        painter = QPainter(self.canvas)
        painter.setOpacity(0.7)  # Increased opacity for better visibility

        # Draw the 512x512 box in the bottom right corner
        painter.setPen(QPen(Qt.green, 2, Qt.SolidLine))
        painter.drawRect(QRect(width - self.box_size, start_y, self.box_size, self.box_size))

        # Draw bounding boxes and labels
        for result in results[0].boxes.data:
            x1, y1, x2, y2, conf, cls = result
            
            # Only display boxes with confidence above 0.5 threshold and class id greater than 24
            if conf > 0.5 and int(cls) >= 24:
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                
                # Adjust coordinates to match the full window (bottom right corner)
                x1 += width - self.box_size
                x2 += width - self.box_size
                y1 += start_y
                y2 += start_y
                
                # Draw bounding box
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                painter.drawRect(x1, y1, x2 - x1, y2 - y1)
                
                # Draw label
                label = f"{results[0].names[int(cls)]}: {conf:.2f}"
                painter.setPen(Qt.white)
                painter.setFont(QFont("Arial", 10))
                painter.drawText(x1, y1 - 10, label)
        painter.end()

        # Trigger a repaint of the window
        self.update()
        print("Annotations drawn on transparent window")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.canvas)
        painter.end()

if __name__ == '__main__':
    print("Starting application")
    app = QApplication(sys.argv)
    yolo_window = YOLOWindow()
    sys.exit(app.exec_())