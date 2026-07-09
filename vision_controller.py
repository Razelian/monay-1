from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from vision_worker import VisionWorker

class YOLOController(QObject):
    # 1. Define the signals
    frame_ready = pyqtSignal(object)  # Emits the DetectionPayload
    finished = pyqtSignal()           # Signals the thread to shut down safely
    error_occurred = pyqtSignal(str)  # Emits error messages to the UI

    def __init__(self, model_name="yolo11n.pt"):
        super().__init__()
        self.worker = VisionWorker(model_name=model_name)
        self.is_running = True

        try:
            self.worker.load_model()
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()

    @pyqtSlot()
    def run_inference(self):
        """This method will execute in the background thread."""
        try:
            self.worker.open_camera()
            for payload in self.worker.generate_frames():
                if not self.is_running:
                    break
                # Send the data packet across the thread boundary
                self.frame_ready.emit(payload)

        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()

    def stop(self):
        """Updates the flag to break the generator loop cleanly."""
        self.is_running = False
