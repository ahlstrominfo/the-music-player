#!/bin/bash
#
# Fetches album list from Pi and generates QR codes locally
#
# Usage: ./tools/generate_qr_from_pi.sh [pi-hostname]
#

PI_HOST="${1:-album@musicplayer.local}"
MUSIC_PATH="~/the-music-player/music"

echo "Fetching album list from $PI_HOST..."

# Get album list from Pi
ALBUMS=$(ssh "$PI_HOST" "ls -1 $MUSIC_PATH" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "Error: Could not connect to $PI_HOST"
    echo "Usage: $0 [user@hostname]"
    exit 1
fi

if [ -z "$ALBUMS" ]; then
    echo "No albums found in $MUSIC_PATH on Pi"
    exit 1
fi

echo "Found albums:"
echo "$ALBUMS" | sed 's/^/  - /'
echo ""

# Generate QR codes locally
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create a temporary Python script to generate QRs for specific albums
python3 - "$ALBUMS" <<'PYTHON'
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent / "tools"))
from generate_qr import create_qr_card

output_dir = Path("qr-cards")
output_dir.mkdir(exist_ok=True)

albums = sys.argv[1].strip().split('\n')

for album_name in albums:
    album_name = album_name.strip()
    if not album_name or album_name.startswith('.'):
        continue

    label = album_name.replace("-", " ").replace("_", " ").title()
    output_path = output_dir / f"{album_name}.png"
    create_qr_card(album_name, label, output_path)

# Generate control cards
create_qr_card("STOP", "STOP", output_dir / "STOP.png")
create_qr_card("SKIP", "SKIP", output_dir / "SKIP.png")

print(f"\nGenerated {len(albums) + 2} QR cards in {output_dir}")
PYTHON

echo ""
echo "QR cards are in: qr-cards/"
