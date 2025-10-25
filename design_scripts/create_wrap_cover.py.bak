#!/usr/bin/env python3
import argparse
from PIL import Image
import os


def create_wrap_cover(poster_path: str, out_path: str, 
                      trim_w: float = 7.0, trim_h: float = 10.0,
                      spine: float = 1.126, bleed: float = 0.125,
                      dpi: int = 300):
    """
    Create a full wrap cover image from a poster by repeating/tiling it
    to fill the entire wrap area (back + spine + front + bleeds).
    """
    # Calculate total dimensions in inches
    total_w_in = 2 * trim_w + spine + 2 * bleed  # back + spine + front + bleeds
    total_h_in = trim_h + 2 * bleed
    
    # Convert to pixels
    total_w_px = int(round(total_w_in * dpi))
    total_h_px = int(round(total_h_in * dpi))
    
    print(f"Creating wrap cover:")
    print(f"  Dimensions: {total_w_in:.3f}\" x {total_h_in:.3f}\"")
    print(f"  Pixels: {total_w_px} x {total_h_px} @ {dpi} DPI")
    
    # Open source poster
    with Image.open(poster_path) as poster:
        # Create new image for the wrap
        wrap = Image.new('RGBA', (total_w_px, total_h_px), (255, 255, 255, 255))
        
        # Calculate how to fill the wrap
        # Option 1: Tile the poster across the entire wrap
        poster_w, poster_h = poster.size
        
        # Scale poster to cover height while maintaining aspect ratio
        scale = total_h_px / poster_h
        scaled_w = int(poster_w * scale)
        scaled_h = total_h_px
        
        if scaled_w < total_w_px:
            # If scaled poster is narrower than wrap, tile it
            poster_scaled = poster.resize((scaled_w, scaled_h), Image.LANCZOS)
            x_offset = 0
            while x_offset < total_w_px:
                wrap.paste(poster_scaled, (x_offset, 0))
                x_offset += scaled_w
        else:
            # If scaled poster is wider, crop from center
            poster_scaled = poster.resize((scaled_w, scaled_h), Image.LANCZOS)
            x_start = (scaled_w - total_w_px) // 2
            crop_box = (x_start, 0, x_start + total_w_px, scaled_h)
            poster_cropped = poster_scaled.crop(crop_box)
            wrap.paste(poster_cropped, (0, 0))
        
        # Save the wrap
        wrap.save(out_path, dpi=(dpi, dpi))
        print(f"✅ Saved wrap cover to: {out_path}")
        
        # Also save panel boundaries for reference
        panel_info = {
            'back_start': bleed * dpi,
            'back_end': (bleed + trim_w) * dpi,
            'spine_start': (bleed + trim_w) * dpi,
            'spine_end': (bleed + trim_w + spine) * dpi,
            'front_start': (bleed + trim_w + spine) * dpi,
            'front_end': (bleed + 2*trim_w + spine) * dpi,
        }
        print("\nPanel boundaries (in pixels):")
        for k, v in panel_info.items():
            print(f"  {k}: {int(v)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('poster', help='Source poster image')
    ap.add_argument('--out', default='cover_wrap_full.png', help='Output wrap image')
    ap.add_argument('--trim-w', type=float, default=7.0)
    ap.add_argument('--trim-h', type=float, default=10.0)
    ap.add_argument('--spine', type=float, default=1.126)
    ap.add_argument('--bleed', type=float, default=0.125)
    ap.add_argument('--dpi', type=int, default=300)
    args = ap.parse_args()
    
    create_wrap_cover(
        args.poster, args.out,
        args.trim_w, args.trim_h,
        args.spine, args.bleed,
        args.dpi
    )


if __name__ == '__main__':
    main()
