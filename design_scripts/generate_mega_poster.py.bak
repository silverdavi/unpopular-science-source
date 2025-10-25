#!/usr/bin/env python3
import os
import argparse
import random
from PIL import Image
from pathlib import Path
import numpy as np
import math
from typing import List, Tuple, Dict
import json


class MegaPosterGenerator:
    def __init__(self, stickers_dir: str, output_path: str):
        self.stickers_dir = Path(stickers_dir)
        self.output_path = Path(output_path)
        self.stickers = []
        self.chapter_colors = {}
        
    def load_stickers(self, sample_fraction: float = 0.95):
        """Load stickers from all chapters."""
        print(f"Loading stickers from {self.stickers_dir}...")
        
        all_stickers = []
        chapters = sorted([d for d in self.stickers_dir.iterdir() if d.is_dir()])
        
        # Generate unique colors for each chapter
        for i, chapter in enumerate(chapters):
            hue = i / len(chapters)
            # Convert HSV to RGB (full saturation and value)
            rgb = self._hsv_to_rgb(hue, 0.7, 0.9)
            self.chapter_colors[chapter.name] = rgb
        
        for chapter_dir in chapters:
            chapter_stickers = []
            
            for sticker_path in sorted(chapter_dir.glob("*.png")):
                try:
                    with Image.open(sticker_path) as img:
                        width, height = img.size
                        chapter_stickers.append({
                            'path': sticker_path,
                            'chapter': chapter_dir.name,
                            'chapter_idx': chapters.index(chapter_dir),
                            'width': width,
                            'height': height,
                            'area': width * height,
                            'aspect_ratio': width / height
                        })
                except Exception as e:
                    print(f"Error loading {sticker_path}: {e}")
            
            # Sample from this chapter
            if sample_fraction < 1.0:
                sample_size = max(1, int(len(chapter_stickers) * sample_fraction))
                chapter_stickers = random.sample(chapter_stickers, sample_size)
            
            all_stickers.extend(chapter_stickers)
        
        self.stickers = all_stickers
        print(f"Loaded {len(self.stickers)} stickers from {len(chapters)} chapters")
        
    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB color."""
        i = int(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        i = i % 6
        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
            
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def calculate_layout(self, target_width: int, target_height: int, 
                        min_size_cm: float = 1.5, dpi: int = 300,
                        padding_factor: float = 1.1):
        """Calculate optimal layout for stickers."""
        # Convert minimum size from cm to pixels
        min_size_px = (min_size_cm / 2.54) * dpi
        min_area_px = min_size_px * min_size_px
        
        # Calculate scale factors for each sticker
        layouts = []
        for sticker in self.stickers:
            # Calculate scale to meet minimum size requirement
            current_area = sticker['area']
            if current_area < min_area_px:
                scale = math.sqrt(min_area_px / current_area)
            else:
                # For large stickers, limit max size
                max_area_px = min_area_px * 9  # Max 3x linear dimension
                if current_area > max_area_px:
                    scale = math.sqrt(max_area_px / current_area)
                else:
                    scale = 1.0
            
            new_width = int(sticker['width'] * scale * padding_factor)
            new_height = int(sticker['height'] * scale * padding_factor)
            
            layouts.append({
                'sticker': sticker,
                'scale': scale,
                'width': new_width,
                'height': new_height,
                'area': new_width * new_height
            })
        
        # Sort by area (largest first) for better packing
        layouts.sort(key=lambda x: x['area'], reverse=True)
        
        return layouts
    
    def pack_stickers(self, layouts: List[Dict], canvas_width: int, canvas_height: int):
        """Pack stickers onto canvas using a bin packing algorithm."""
        placed = []
        
        # Simple row-based packing
        current_y = 0
        row_height = 0
        current_x = 0
        
        for layout in layouts:
            width = layout['width']
            height = layout['height']
            
            # Check if we need to start a new row
            if current_x + width > canvas_width:
                current_y += row_height
                current_x = 0
                row_height = 0
            
            # Check if we've run out of vertical space
            if current_y + height > canvas_height:
                break
            
            # Place the sticker
            placed.append({
                **layout,
                'x': current_x,
                'y': current_y
            })
            
            current_x += width
            row_height = max(row_height, height)
        
        return placed
    
    def generate_poster(self, width: int, height: int, min_size_cm: float = 1.5,
                       dpi: int = 300, background_color: Tuple[int, int, int] = (240, 240, 240)):
        """Generate the mega poster."""
        print(f"\nGenerating {width}x{height} poster...")
        print(f"Minimum sticker size: {min_size_cm} cm")
        
        # Create canvas
        canvas = Image.new('RGB', (width, height), background_color)
        
        # Calculate layouts
        layouts = self.calculate_layout(width, height, min_size_cm, dpi)
        
        # Pack stickers
        placed = self.pack_stickers(layouts, width, height)
        
        print(f"Placing {len(placed)} out of {len(self.stickers)} stickers...")
        
        # Place stickers on canvas
        for i, item in enumerate(placed):
            if i % 100 == 0:
                print(f"  Placed {i}/{len(placed)} stickers...")
            
            sticker_info = item['sticker']
            
            # Load and resize sticker
            with Image.open(sticker_info['path']) as sticker:
                # Convert to RGBA if needed
                if sticker.mode != 'RGBA':
                    sticker = sticker.convert('RGBA')
                
                # Resize
                scale = item['scale']
                new_size = (int(sticker.width * scale), int(sticker.height * scale))
                sticker_resized = sticker.resize(new_size, Image.Resampling.LANCZOS)
                
                # Add subtle colored border based on chapter
                border_color = self.chapter_colors.get(sticker_info['chapter'], (200, 200, 200))
                bordered = Image.new('RGBA', 
                                   (sticker_resized.width + 4, sticker_resized.height + 4),
                                   border_color + (255,))
                bordered.paste(sticker_resized, (2, 2), sticker_resized)
                
                # Paste onto canvas
                canvas.paste(bordered, (item['x'], item['y']), bordered)
        
        return canvas, placed
    
    def save_poster(self, poster: Image.Image, filename: str, dpi: int = 300):
        """Save the poster with metadata."""
        poster.save(filename, dpi=(dpi, dpi))
        print(f"✅ Saved poster to: {filename}")
        
    def save_metadata(self, placed: List[Dict], metadata_file: str):
        """Save metadata about placed stickers."""
        metadata = {
            'total_stickers': len(self.stickers),
            'placed_stickers': len(placed),
            'chapters': list(self.chapter_colors.keys()),
            'placement_rate': len(placed) / len(self.stickers) if self.stickers else 0
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Saved metadata to: {metadata_file}")


def main():
    ap = argparse.ArgumentParser(description="Generate mega poster with stickers")
    ap.add_argument('--stickers-dir', default='stickers_sam',
                    help='Directory containing sticker subdirectories')
    ap.add_argument('--output', default='mega_poster.png',
                    help='Output poster filename')
    ap.add_argument('--width', type=int, default=7680,
                    help='Poster width in pixels (default: 7680 for 8K)')
    ap.add_argument('--height', type=int, default=4320,
                    help='Poster height in pixels (default: 4320 for 8K)')
    ap.add_argument('--min-size', type=float, default=1.5,
                    help='Minimum sticker size in cm (default: 1.5)')
    ap.add_argument('--dpi', type=int, default=300,
                    help='DPI for output (default: 300)')
    ap.add_argument('--sample', type=float, default=0.95,
                    help='Fraction of stickers to include (default: 0.95)')
    ap.add_argument('--preset', choices=['4k', '8k', '16k', 'print-a0', 'print-a1', 'custom'],
                    help='Use preset dimensions')
    
    args = ap.parse_args()
    
    # Apply presets
    if args.preset:
        presets = {
            '4k': (3840, 2160),
            '8k': (7680, 4320),
            '16k': (15360, 8640),
            'print-a0': (9933, 14043),  # A0 at 300 DPI
            'print-a1': (7016, 9933),   # A1 at 300 DPI
        }
        if args.preset in presets:
            args.width, args.height = presets[args.preset]
            print(f"Using {args.preset} preset: {args.width}x{args.height}")
    
    # Initialize generator
    generator = MegaPosterGenerator(args.stickers_dir, args.output)
    
    # Load stickers
    generator.load_stickers(sample_fraction=args.sample)
    
    # Generate poster
    poster, placed = generator.generate_poster(
        args.width, args.height, 
        min_size_cm=args.min_size,
        dpi=args.dpi
    )
    
    # Save results
    generator.save_poster(poster, args.output, dpi=args.dpi)
    
    # Save metadata
    metadata_file = args.output.replace('.png', '_metadata.json')
    generator.save_metadata(placed, metadata_file)
    
    # Print summary
    print(f"\n=== Poster Summary ===")
    print(f"Dimensions: {args.width}x{args.height} pixels")
    print(f"Physical size: {args.width/args.dpi:.1f}\" x {args.height/args.dpi:.1f}\"")
    print(f"Physical size: {args.width/args.dpi*2.54:.1f} x {args.height/args.dpi*2.54:.1f} cm")
    print(f"Stickers placed: {len(placed)} / {len(generator.stickers)} ({len(placed)/len(generator.stickers)*100:.1f}%)")


if __name__ == '__main__':
    main()
