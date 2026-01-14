#!/usr/bin/env python3
"""Test QR scanning - captures frames and tries to decode them."""

import cv2
from pyzbar import pyzbar
import time

print("Opening camera...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open camera")
    exit(1)

width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(f"Camera opened: {width}x{height}")

print("\nScanning for QR codes... (Ctrl+C to stop)")
print("Hold a QR code in front of the camera.\n")

frame_count = 0
last_status = time.time()

try:
    while True:
        ret, frame = cap.read()
        frame_count += 1

        if not ret:
            print(f"Frame {frame_count}: capture failed")
            continue

        # Try to decode
        decoded = pyzbar.decode(frame)

        if decoded:
            for obj in decoded:
                print(f"Frame {frame_count}: FOUND {obj.type} = {obj.data.decode('utf-8')}")
        elif time.time() - last_status > 2.0:
            # Print status every 2 seconds
            print(f"Frame {frame_count}: scanning... (no QR code detected)")
            last_status = time.time()

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopped.")
finally:
    cap.release()
