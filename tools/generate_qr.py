#!/usr/bin/env python3
"""
Generate QR code cards for albums.

Usage:
    python generate_qr.py                     # Generate for all albums in music/
    python generate_qr.py --single CODE LABEL # Generate a single QR code
"""

import sys
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont


def create_qr_card(code: str, label: str, output_path: Path, size: int = 400):
    """
    Create a QR code card with label.

    Args:
        code: The data to encode in the QR code
        label: Human-readable label to print below the QR code
        output_path: Where to save the image
        size: Size of the QR code in pixels
    """
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(code)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.resize((size, size), Image.Resampling.NEAREST)

    # Create card with space for label
    label_height = 60
    card_width = size + 40
    card_height = size + label_height + 40

    card = Image.new("RGB", (card_width, card_height), "white")

    # Paste QR code centered
    qr_x = (card_width - size) // 2
    qr_y = 20
    card.paste(qr_img, (qr_x, qr_y))

    # Add label
    draw = ImageDraw.Draw(card)

    # Try to use a nice font, fall back to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except OSError:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except OSError:
            font = ImageFont.load_default()

    # Center the label
    bbox = draw.textbbox((0, 0), label, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (card_width - text_width) // 2
    text_y = size + 30

    draw.text((text_x, text_y), label, fill="black", font=font)

    card.save(output_path)
    print(f"Created: {output_path}")


def generate_from_music_folder(music_dir: Path, output_dir: Path):
    """Generate QR codes for all album folders."""
    if not music_dir.exists():
        print(f"Music folder not found: {music_dir}")
        print("Create album folders in music/ first.")
        sys.exit(1)

    # Find all album folders
    albums = [d for d in sorted(music_dir.iterdir()) if d.is_dir() and not d.name.startswith(".")]

    if not albums:
        print(f"No album folders found in {music_dir}")
        print("Create folders like: music/beatles-abbey-road/")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    for album_path in albums:
        album_name = album_path.name
        # Create nice label from folder name
        label = album_name.replace("-", " ").replace("_", " ").title()
        output_path = output_dir / f"{album_name}.png"
        # QR code contains the folder name directly
        create_qr_card(album_name, label, output_path)

    # Always generate control cards
    stop_path = output_dir / "STOP.png"
    create_qr_card("STOP", "STOP", stop_path)

    skip_path = output_dir / "SKIP.png"
    create_qr_card("SKIP", "SKIP", skip_path)

    print(f"\nGenerated {len(albums) + 2} QR cards in {output_dir}")


def main():
    script_dir = Path(__file__).parent.parent
    music_dir = script_dir / "music"
    output_dir = script_dir / "qr-cards"

    if len(sys.argv) >= 4 and sys.argv[1] == "--single":
        # Generate single QR code
        code = sys.argv[2]
        label = sys.argv[3]
        output_path = output_dir / f"{code}.png"
        output_dir.mkdir(parents=True, exist_ok=True)
        create_qr_card(code, label, output_path)
    else:
        # Generate from music folder
        generate_from_music_folder(music_dir, output_dir)


if __name__ == "__main__":
    main()
