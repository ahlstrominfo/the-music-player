#!/usr/bin/env python3
"""
QR Code Music Player

Scans QR codes via webcam and plays corresponding albums.
QR code contains the album folder name directly (e.g., "beatles-abbey-road").
"""

import sys
import time
from pathlib import Path

from scanner import QRScanner
from player import AlbumPlayer


# Special QR code value to stop playback
STOP_CODE = "STOP"

# Minimum time between processing the same QR code (seconds)
DEBOUNCE_TIME = 2.0


def main():
    # Determine paths relative to script location
    script_dir = Path(__file__).parent.parent
    music_dir = script_dir / "music"

    # Allow overriding via command line
    if len(sys.argv) > 1:
        music_dir = Path(sys.argv[1])

    print("=" * 50)
    print("QR Code Music Player")
    print("=" * 50)
    print(f"Music folder: {music_dir}")

    # List available albums
    albums = [d.name for d in music_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    print(f"Found {len(albums)} albums")
    print()

    # Track last scanned code for debouncing
    last_code = None
    last_code_time = 0

    print("Starting scanner... (Press Ctrl+C to exit)")
    print("-" * 50)

    with QRScanner() as scanner, AlbumPlayer(music_dir) as player:
        try:
            while True:
                code = scanner.scan()

                if code:
                    current_time = time.time()

                    # Debounce: ignore if same code scanned recently
                    if code == last_code and (current_time - last_code_time) < DEBOUNCE_TIME:
                        continue

                    last_code = code
                    last_code_time = current_time

                    print(f"\nScanned: {code}")

                    if code == STOP_CODE:
                        player.stop_playback()
                    elif (music_dir / code).is_dir():
                        player.play_album(code)
                    else:
                        print(f"Album not found: {code}")

                # Small delay to reduce CPU usage
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\nShutting down...")


if __name__ == "__main__":
    main()
