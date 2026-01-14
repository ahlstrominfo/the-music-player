#!/bin/bash
#
# Raspberry Pi setup script for QR Music Player
# Run this on your Pi after copying the project
#

set -e

echo "=================================="
echo "QR Music Player - Pi Setup"
echo "=================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="/etc/systemd/system/qr-music-player.service"

echo ""
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    ffmpeg \
    mpv \
    python3-opencv

# Install zbar (package name varies by OS version)
sudo apt-get install -y libzbar0t64 2>/dev/null || sudo apt-get install -y libzbar0

echo ""
echo "Creating Python virtual environment..."
cd "$SCRIPT_DIR"
python3 -m venv --system-site-packages venv
source venv/bin/activate

echo ""
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements-pi.txt

echo ""
echo "Setting up systemd service..."

# Get user ID for audio session access
USER_ID=$(id -u)

# Create service file
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=QR Code Music Player
After=network.target sound.target pipewire.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
Environment=XDG_RUNTIME_DIR=/run/user/$USER_ID
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$USER_ID/bus
ExecStart=$SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/src/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "Enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable qr-music-player.service

echo ""
echo "=================================="
echo "Setup complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Add your albums to: $SCRIPT_DIR/music/"
echo "     (each album in its own folder, e.g. music/beatles-abbey-road/)"
echo ""
echo "  2. Generate QR cards:"
echo "     source venv/bin/activate"
echo "     python tools/generate_qr.py"
echo ""
echo "  3. Start the service:"
echo "     sudo systemctl start qr-music-player"
echo ""
echo "  4. Check status:"
echo "     sudo systemctl status qr-music-player"
echo "     journalctl -u qr-music-player -f"
echo ""
echo "  5. Make sure audio output is set to 3.5mm jack:"
echo "     sudo raspi-config -> System Options -> Audio"
echo ""
