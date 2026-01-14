#!/bin/bash
#
# Syncs local music folders to Pi (uploads new albums only)
#
# Usage: ./tools/sync_music_to_pi.sh [pi-hostname]
#

PI_HOST="${1:-album@musicplayer.local}"
PI_MUSIC_PATH="~/the-music-player/music"
LOCAL_MUSIC_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/music"

echo "Syncing music to $PI_HOST"
echo "Local:  $LOCAL_MUSIC_PATH"
echo "Remote: $PI_MUSIC_PATH"
echo ""

# Check local music folder exists
if [ ! -d "$LOCAL_MUSIC_PATH" ]; then
    echo "Error: Local music folder not found: $LOCAL_MUSIC_PATH"
    exit 1
fi

# Get local albums
LOCAL_ALBUMS=$(ls -1 "$LOCAL_MUSIC_PATH" 2>/dev/null | grep -v '^\.' | grep -v '.gitkeep')

if [ -z "$LOCAL_ALBUMS" ]; then
    echo "No local albums found in $LOCAL_MUSIC_PATH"
    exit 0
fi

# Get remote albums
echo "Checking Pi for existing albums..."
REMOTE_ALBUMS=$(ssh "$PI_HOST" "ls -1 $PI_MUSIC_PATH 2>/dev/null" | grep -v '^\.')

if [ $? -ne 0 ]; then
    echo "Error: Could not connect to $PI_HOST"
    exit 1
fi

# Find albums that need to be uploaded
TO_UPLOAD=""
for album in $LOCAL_ALBUMS; do
    if ! echo "$REMOTE_ALBUMS" | grep -q "^${album}$"; then
        TO_UPLOAD="$TO_UPLOAD $album"
    fi
done

if [ -z "$TO_UPLOAD" ]; then
    echo "All albums already exist on Pi. Nothing to upload."
    exit 0
fi

echo "Albums to upload:"
for album in $TO_UPLOAD; do
    SIZE=$(du -sh "$LOCAL_MUSIC_PATH/$album" | cut -f1)
    echo "  - $album ($SIZE)"
done
echo ""

read -p "Proceed with upload? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Upload each album
for album in $TO_UPLOAD; do
    echo ""
    echo "Uploading: $album"
    rsync -avz --progress "$LOCAL_MUSIC_PATH/$album" "$PI_HOST:$PI_MUSIC_PATH/"

    if [ $? -eq 0 ]; then
        echo "✓ Uploaded: $album"
    else
        echo "✗ Failed: $album"
    fi
done

echo ""
echo "Done! You may want to regenerate QR codes:"
echo "  ./tools/generate_qr_from_pi.sh"
