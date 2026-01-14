"""QR code scanner using webcam."""

import cv2
from pyzbar import pyzbar


class QRScanner:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap = None

    def start(self):
        """Initialize the camera."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera {self.camera_index}")
        # Set lower resolution for faster processing
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def stop(self):
        """Release the camera."""
        if self.cap:
            self.cap.release()
            self.cap = None

    def scan(self) -> str | None:
        """
        Capture a frame and scan for QR codes.
        Returns the decoded data if found, None otherwise.
        """
        if not self.cap:
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        # Decode QR codes in the frame
        decoded_objects = pyzbar.decode(frame)

        for obj in decoded_objects:
            if obj.type == "QRCODE":
                return obj.data.decode("utf-8")

        return None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
