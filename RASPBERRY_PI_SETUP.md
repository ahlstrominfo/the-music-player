# Raspberry Pi Setup from Scratch

Complete guide to set up the QR Music Player on a fresh Raspberry Pi.

## What You Need

- Raspberry Pi (3, 4, or 5)
- MicroSD card (8GB minimum, 32GB+ recommended for music)
- USB webcam
- Speakers with 3.5mm jack
- Power supply for Pi
- Computer to flash the SD card

## Step 1: Flash Raspberry Pi OS

1. Download **Raspberry Pi Imager** from https://www.raspberrypi.com/software/

2. Insert your microSD card into your computer

3. Open Raspberry Pi Imager and click **Choose OS**
   - Select **Raspberry Pi OS (64-bit)** (under "Raspberry Pi OS (other)" if not shown)
   - The Lite version works fine (no desktop needed)

4. Click **Choose Storage** and select your SD card

5. Click the **gear icon** (⚙️) for advanced options:
   - **Set hostname:** `musicplayer` (or whatever you prefer)
   - **Enable SSH:** Yes, use password authentication
   - **Set username and password:** e.g., `pi` / `yourpassword`
   - **Configure WiFi:** Enter your network name and password
   - **Set locale:** Your timezone and keyboard layout

6. Click **Save**, then **Write**

7. Wait for flashing to complete, then eject the SD card

## Step 2: Boot the Pi

1. Insert SD card into Pi
2. Connect USB webcam
3. Connect speakers to 3.5mm audio jack
4. Connect power

The Pi will boot and connect to your WiFi automatically.

## Step 3: Connect via SSH

Find your Pi on the network:

```bash
# On Mac/Linux
ping musicplayer.local

# Or scan your network
arp -a | grep raspberry
```

Connect:

```bash
ssh pi@musicplayer.local
# Enter your password when prompted
```

## Step 4: Update the System

```bash
sudo apt update && sudo apt upgrade -y
```

## Step 5: Configure Audio Output

Set the 3.5mm jack as the default audio output:

```bash
echo 'defaults.pcm.card 1
defaults.ctl.card 1' | sudo tee /etc/asound.conf
```

Test audio:

```bash
speaker-test -t wav -c 2
```

You should hear "Front Left, Front Right" from your speakers. Press Ctrl+C to stop.

If you don't hear anything, check which card is the headphone output:

```bash
aplay -l
```

Look for "bcm2835 Headphones" - note the card number and update `/etc/asound.conf` accordingly.

## Step 6: Install Git

```bash
sudo apt install -y git
```

## Step 7: Clone the Project

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/the-music-player.git
cd the-music-player
```

Or copy from your computer:

```bash
# On your Mac, run:
scp -r /Users/ahlstrominfo/repos/the-music-player pi@musicplayer.local:~/
```

## Step 8: Run the Install Script

```bash
cd ~/the-music-player
chmod +x install-pi.sh
./install-pi.sh
```

This installs all dependencies and sets up auto-start on boot.

## Step 9: Add Your Music

### Option A: Copy from your computer

```bash
# On your Mac:
scp -r /path/to/album pi@musicplayer.local:~/the-music-player/music/album-name/
```

### Option B: Copy from USB drive

```bash
# Plug in USB drive, then on Pi:
sudo mkdir -p /mnt/usb
sudo mount /dev/sda1 /mnt/usb
cp -r /mnt/usb/my-album ~/the-music-player/music/
sudo umount /mnt/usb
```

### Folder structure

```
music/
├── beatles-abbey-road/
│   ├── 01-come-together.mp3
│   ├── 02-something.mp3
│   └── ...
├── pink-floyd-dark-side/
│   ├── 01-speak-to-me.mp3
│   └── ...
```

## Step 10: Generate QR Cards

On the Pi:

```bash
cd ~/the-music-player
source venv/bin/activate
python tools/generate_qr.py
```

Copy QR cards back to your computer to print:

```bash
# On your Mac:
scp -r pi@musicplayer.local:~/the-music-player/qr-cards ./
```

Print the images from `qr-cards/` folder.

## Step 11: Start the Player

```bash
sudo systemctl start qr-music-player
```

Check it's running:

```bash
sudo systemctl status qr-music-player
```

View live logs:

```bash
journalctl -u qr-music-player -f
```

## Step 12: Test It

Hold a printed QR card in front of the webcam. You should see the album start playing in the logs, and hear music from your speakers.

Scan the STOP card to stop playback.

## Auto-Start on Boot

The install script already configured this. The player starts automatically when the Pi boots.

To disable auto-start:

```bash
sudo systemctl disable qr-music-player
```

To re-enable:

```bash
sudo systemctl enable qr-music-player
```

## Troubleshooting

### No audio

```bash
# Check available audio devices
aplay -l

# Set 3.5mm jack (usually card 1) as default
echo 'defaults.pcm.card 1
defaults.ctl.card 1' | sudo tee /etc/asound.conf

# Test speakers
speaker-test -t wav -c 2

# Check volume
alsamixer
# Use arrow keys to adjust, ESC to exit
```

### Audio works manually but not from service

The service needs access to your pipewire session. Check the service has these environment variables:

```bash
sudo systemctl cat qr-music-player | grep Environment
```

Should show:
```
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
```

If missing, re-run `./install-pi.sh` or add them manually:

```bash
sudo systemctl edit qr-music-player
```

Add:
```ini
[Service]
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
```

Then `sudo systemctl daemon-reload && sudo systemctl restart qr-music-player`

### Camera not detected

```bash
# Check camera is connected
ls /dev/video*
# Should show /dev/video0

# Test camera
sudo apt install -y fswebcam
fswebcam test.jpg
```

### Service won't start

```bash
# Check logs for errors
journalctl -u qr-music-player -n 50

# Try running manually
cd ~/the-music-player
source venv/bin/activate
python src/main.py
```

### QR codes not scanning

- Ensure good lighting
- Hold card 15-30cm from camera
- Make sure card is printed clearly (not blurry)
- Try a different webcam

### Permission denied on camera

```bash
# Add user to video group
sudo usermod -a -G video $USER
# Then reboot
sudo reboot
```

## Useful Commands

```bash
# Start player
sudo systemctl start qr-music-player

# Stop player
sudo systemctl stop qr-music-player

# Restart player
sudo systemctl restart qr-music-player

# View status
sudo systemctl status qr-music-player

# View logs (live)
journalctl -u qr-music-player -f

# View recent logs
journalctl -u qr-music-player -n 100

# Reboot Pi
sudo reboot

# Shutdown Pi
sudo shutdown -h now
```

## Adding More Albums Later

1. Copy album folder to `~/the-music-player/music/`
2. Generate new QR card:
   ```bash
   cd ~/the-music-player
   source venv/bin/activate
   python tools/generate_qr.py
   ```
3. Copy and print the new QR card
4. Restart the service (optional, it detects new albums automatically):
   ```bash
   sudo systemctl restart qr-music-player
   ```
