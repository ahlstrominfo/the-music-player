#!/usr/bin/env python3
"""
QR Code Music Player

Scans QR codes via webcam and plays corresponding albums.
QR code contains the album folder name directly (e.g., "beatles-abbey-road").
"""

import logging
import sys
import time
from pathlib import Path

from scanner import QRScanner
from player import AlbumPlayer

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# Special QR code values
STOP_CODE = "STOP"
SKIP_CODE = "SKIP"

# Minimum time between processing the same QR code (seconds)
DEBOUNCE_TIME = 2.0


def main():
    # Determine paths relative to script location
    script_dir = Path(__file__).parent.parent
    music_dir = script_dir / "music"

    # Allow overriding via command line
    if len(sys.argv) > 1:
        music_dir = Path(sys.argv[1])

    logger.info("=" * 50)
    logger.info("QR Code Music Player")
    logger.info("=" * 50)
    logger.info(f"Music folder: {music_dir}")

    # List available albums
    albums = [d.name for d in music_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    logger.info(f"Found {len(albums)} albums: {albums}")

    # Track last scanned code for debouncing
    last_code = None
    last_code_time = 0

    logger.info("Starting scanner... (Press Ctrl+C to exit)")
    logger.info("-" * 50)

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

                    logger.info(f"Scanned: {code}")

                    if code == STOP_CODE:
                        player.stop_playback()
                    elif code == SKIP_CODE:
                        player.skip_track()
                    elif (music_dir / code).is_dir():
                        # Don't restart if same album is already playing
                        if player.current_album == code and player.is_playing:
                            logger.info(f"Album '{code}' already playing, ignoring")
                        else:
                            player.play_album(code)
                    else:
                        logger.warning(f"Album not found: '{code}'")
                        logger.warning(f"Available albums: {albums}")

                # Small delay to reduce CPU usage
                time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Shutting down...")


if __name__ == "__main__":
    main()
