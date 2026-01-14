"""QR code scanner using webcam."""

import logging
import cv2
from pyzbar import pyzbar

logger = logging.getLogger(__name__)


class QRScanner:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap = None

    def start(self):
        """Initialize the camera."""
        logger.info(f"Opening camera {self.camera_index}...")
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera {self.camera_index}")
        # Set lower resolution for faster processing
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Log camera info
        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        logger.info(f"Camera opened: {width}x{height}")

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
            logger.warning("Camera not initialized")
            return None

        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to capture frame")
            return None

        # Decode QR codes in the frame
        decoded_objects = pyzbar.decode(frame)

        if decoded_objects:
            logger.debug(f"Found {len(decoded_objects)} objects: {[obj.type for obj in decoded_objects]}")

        for obj in decoded_objects:
            if obj.type == "QRCODE":
                data = obj.data.decode("utf-8")
                logger.info(f"QR code detected: {data}")
                return data

        return None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
