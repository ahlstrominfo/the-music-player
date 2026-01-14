"""Audio player for albums using system audio players."""

import subprocess
import threading
import platform
from pathlib import Path


class AlbumPlayer:
    def __init__(self, music_dir: str | Path):
        self.music_dir = Path(music_dir)
        self.current_album = None
        self.tracks = []
        self.current_track_index = 0
        self.is_playing = False
        self._stop_event = threading.Event()
        self._play_thread = None
        self._current_process = None

    def start(self):
        """Initialize player."""
        pass

    def stop(self):
        """Cleanup."""
        self.stop_playback()

    def get_album_tracks(self, album_id: str) -> list[Path]:
        """Get sorted list of audio files in an album folder."""
        album_path = self.music_dir / album_id
        if not album_path.exists():
            return []

        # Collect all supported formats
        extensions = ["*.mp3", "*.m4a", "*.ogg", "*.flac", "*.wav"]
        tracks = []
        for ext in extensions:
            tracks.extend(album_path.glob(ext))

        return sorted(tracks)

    def _get_play_command(self, track_path: Path) -> list[str]:
        """Get the command to play a track based on OS."""
        if platform.system() == "Darwin":
            # macOS: use afplay (built-in)
            return ["afplay", str(track_path)]
        else:
            # Linux/Pi: try ffplay first (supports more formats), fallback to mpg123
            return ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(track_path)]

    def play_album(self, album_id: str):
        """Start playing an album from the beginning."""
        # Stop any current playback
        self.stop_playback()

        tracks = self.get_album_tracks(album_id)
        if not tracks:
            print(f"No tracks found for album: {album_id}")
            return False

        self.current_album = album_id
        self.tracks = tracks
        self.current_track_index = 0
        self.is_playing = True
        self._stop_event.clear()

        # Start playback in a separate thread
        self._play_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self._play_thread.start()

        print(f"Playing album: {album_id} ({len(tracks)} tracks)")
        return True

    def _playback_loop(self):
        """Internal playback loop running in a thread."""
        while not self._stop_event.is_set() and self.current_track_index < len(self.tracks):
            track = self.tracks[self.current_track_index]
            print(f"  Track {self.current_track_index + 1}/{len(self.tracks)}: {track.name}")

            try:
                cmd = self._get_play_command(track)
                self._current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                # Wait for track to finish or stop event
                while self._current_process.poll() is None:
                    if self._stop_event.is_set():
                        self._current_process.terminate()
                        self._current_process.wait()
                        break
                    self._stop_event.wait(0.1)

                if self._stop_event.is_set():
                    break

                self.current_track_index += 1

            except FileNotFoundError as e:
                print(f"Audio player not found: {e}")
                print("Install ffmpeg: brew install ffmpeg (Mac) or sudo apt install ffmpeg (Pi)")
                break
            except Exception as e:
                print(f"Error playing {track}: {e}")
                self.current_track_index += 1

        self._current_process = None
        self.is_playing = False
        if not self._stop_event.is_set():
            print(f"Album finished: {self.current_album}")

    def stop_playback(self):
        """Stop current playback."""
        if self.is_playing:
            self._stop_event.set()
            if self._current_process:
                self._current_process.terminate()
                try:
                    self._current_process.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    self._current_process.kill()
            if self._play_thread:
                self._play_thread.join(timeout=1.0)
            self.is_playing = False
            print("Playback stopped")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
