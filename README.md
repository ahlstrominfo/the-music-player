# QR Code Music Player

A Raspberry Pi music player that plays albums when you scan QR codes. Perfect for kids, elderly, or anyone who wants a simple physical interface for music.

## How It Works

1. Put albums in folders like `music/beatles-abbey-road/`
2. Generate QR cards (QR code contains the folder name)
3. Scan a card with the webcam → album starts playing
4. Scan the same album again → ignored (doesn't restart)
5. Scan **SKIP** → skip to next track
6. Scan **STOP** → stop playback

## Supported Formats

MP3, M4A, OGG, FLAC, WAV

## Development (Mac)

### Setup

```bash
# Install zbar (required for QR scanning)
brew install zbar

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Add Music

```bash
# Create album folders (the folder name = QR code content)
mkdir -p music/beatles-abbey-road
mkdir -p music/pink-floyd-dark-side

# Copy audio files (they play in alphabetical order)
cp ~/Music/AbbeyRoad/*.mp3 music/beatles-abbey-road/
```

### Generate QR Cards

```bash
python tools/generate_qr.py
```

This scans `music/` and creates a QR card for each album folder in `qr-cards/`.

### Run

```bash
python src/main.py
```

Point your webcam at a QR card to start playing.

## Raspberry Pi Setup

**Starting from scratch?** See [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md) for a complete guide from blank SD card to working player.

### Prerequisites

- Raspberry Pi (tested on Pi 3/4/5)
- USB webcam
- Speakers connected via 3.5mm jack
- Raspbian/Raspberry Pi OS

### Install

```bash
# Copy project to Pi (via USB, scp, git, etc.)

# Run setup script
./install-pi.sh
```

This installs dependencies and sets up auto-start on boot.

### Configure Audio Output

Make sure audio goes to the 3.5mm jack:

```bash
sudo raspi-config
# → System Options → Audio → 3.5mm jack
```

### Service Commands

```bash
# Start
sudo systemctl start qr-music-player

# Stop
sudo systemctl stop qr-music-player

# View logs
journalctl -u qr-music-player -f

# Disable auto-start
sudo systemctl disable qr-music-player
```

## Managing Music from Mac

### Sync albums to Pi

```bash
# Put albums in local music/ folder
cp -r ~/Music/some-album ./music/some-album

# Upload new albums to Pi (skips existing)
./tools/sync_music_to_pi.sh
```

### Generate QR cards from Pi

```bash
# Fetch album list from Pi and generate QR codes locally
./tools/generate_qr_from_pi.sh
```

## Printing Cards

1. Add albums to Pi (via `sync_music_to_pi.sh` or directly)
2. Generate QR codes: `./tools/generate_qr_from_pi.sh`
3. Print images from `qr-cards/`
4. Cut and optionally laminate for durability

Tip: Print multiple cards per page, or glue them to cardboard for sturdiness.

## Project Structure

```
the-music-player/
├── src/
│   ├── main.py        # Main application loop
│   ├── scanner.py     # Webcam QR scanning
│   └── player.py      # Audio playback
├── tools/
│   ├── generate_qr.py         # QR card generator
│   ├── generate_qr_from_pi.sh # Generate QR cards from Pi's album list
│   ├── sync_music_to_pi.sh    # Upload new albums to Pi
│   └── test_scanner.py        # Debug QR scanning
├── music/             # Album folders (folder name = QR code)
├── qr-cards/          # Generated QR images
├── requirements.txt
└── install-pi.sh      # Pi setup script
```

## Troubleshooting

**Camera not found**
- Check webcam is connected: `ls /dev/video*`
- Try different camera index in code

**No sound on Pi**
- List devices: `aplay -l` (find "bcm2835 Headphones", note card number)
- Set default: `echo 'defaults.pcm.card 1' | sudo tee /etc/asound.conf`
- Test audio: `speaker-test -t wav -c 2`

**M4A files don't play on Pi**
- Install codec support: `sudo apt install ffmpeg libavcodec-extra`
- Or convert to MP3

**QR code not scanning**
- Ensure good lighting
- Hold card steady, ~15-30cm from camera
- Check card isn't blurry when printed
