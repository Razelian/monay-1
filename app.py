import sys
import cv2
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QMainWindow, QLabel, QLCDNumber, QVBoxLayout, QWidget, QApplication
from PyQt6.QtCore import QThread
from vision_controller import YOLOController

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_threading()

    def init_ui(self):
        print("Initializing dashboard...")
        # Basic UI Setup (Placeholder for your actual design)
        self.video_label = QLabel("Camera Feed Initializing...")
        self.count_lcd = QLCDNumber()

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.count_lcd)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def setup_threading(self):
        # 1. Instantiate the raw thread and the worker object
        self.inference_thread = QThread()
        self.yolo_controller = YOLOController(model_name="yolo11n.pt")

        # 2. MOVE THE WORKER TO THE THREAD
        self.yolo_controller.moveToThread(self.inference_thread)

        # 3. Wire up the Signals and Slots
        # When the thread starts, trigger the run_inference method
        self.inference_thread.started.connect(self.yolo_controller.run_inference)

        # When the controller has a frame, send it to the UI update method
        self.yolo_controller.frame_ready.connect(self.update_dashboard)

        # Cleanup wiring: When controller is finished, quit the thread
        self.yolo_controller.finished.connect(self.inference_thread.quit)
        # Ensure the controller object is deleted to prevent memory leaks
        self.yolo_controller.finished.connect(self.yolo_controller.deleteLater)
        # Delete the thread object once it has fully quit
        self.inference_thread.finished.connect(self.inference_thread.deleteLater)

        # 4. Start the engine
        self.inference_thread.start()

    def update_dashboard(self, payload):
        """Executes safely on the Main UI Thread."""
        self.count_lcd.display(payload.human_count)
        # Extract the raw NumPy array from the DTO
        bgr_frame = payload.frame
        height, width, channels = bgr_frame.shape
        bytes_per_line = channels * width

        # Step 1: Convert BGR Matrix to RGB Matrix
        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)

        # Step 2: Construct QImage pointing to the raw frame bytes
        qt_image = QImage(
            rgb_frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888
        )

        # Step 3: Convert to a hardware-accelerated QPixmap
        pixmap = QPixmap.fromImage(qt_image)

        # Step 4: Draw it on the UI Label
        self.video_label.setPixmap(pixmap)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec())
