#!/usr/bin/env python3
import os
import argparse
import random
from PIL import Image
from pathlib import Path
import math
from typing import List, Tuple, Dict


class RandomPosterGenerator:
    def __init__(self, stickers_dir: str):
        self.stickers_dir = Path(stickers_dir)
        self.stickers = []
        self.placed_regions = []  # List of (x1, y1, x2, y2) tuples for overlap checking
        
    def load_stickers(self, max_stickers: int = None):
        """Load stickers from all chapters."""
        print(f"Loading stickers from {self.stickers_dir}...")
        
        all_stickers = []
        chapters = sorted([d for d in self.stickers_dir.iterdir() if d.is_dir()])
        
        for chapter_dir in chapters:
            for sticker_path in sorted(chapter_dir.glob("*.png")):
                try:
                    # Get image size to calculate area for sorting
                    with Image.open(sticker_path) as img:
                        all_stickers.append({
                            'path': sticker_path,
                            'chapter': chapter_dir.name,
                            'area': img.width * img.height,
                            'width': img.width,
                            'height': img.height
                        })
                except:
                    # If can't open, add without size info
                    all_stickers.append({
                        'path': sticker_path,
                        'chapter': chapter_dir.name,
                        'area': 20000  # Default average area
                    })
        
        # Randomly sample if max_stickers specified
        if max_stickers and max_stickers < len(all_stickers):
            all_stickers = random.sample(all_stickers, max_stickers)
        
        self.stickers = all_stickers
        print(f"Loaded {len(self.stickers)} stickers from {len(chapters)} chapters")
        
    def check_overlap(self, x1, y1, x2, y2, padding=0):
        """Check if a region overlaps with any placed stickers."""
        for px1, py1, px2, py2 in self.placed_regions:
            # Add minimal padding to allow stickers to be very close
            if not (x2 + padding < px1 or x1 - padding > px2 or 
                    y2 + padding < py1 or y1 - padding > py2):
                return True
        return False
    
    def find_placement(self, width, height, canvas_width, canvas_height, max_attempts=500):
        """Find a non-overlapping position for a sticker, preferring positions near existing stickers."""
        candidates = []
        
        # Try multiple random positions
        for _ in range(max_attempts):
            x = random.randint(0, max(0, canvas_width - width))
            y = random.randint(0, max(0, canvas_height - height))
            
            if not self.check_overlap(x, y, x + width, y + height):
                # Calculate distance to nearest placed sticker
                min_distance = float('inf')
                if self.placed_regions:
                    for px1, py1, px2, py2 in self.placed_regions:
                        # Distance from center to center
                        cx1, cy1 = x + width/2, y + height/2
                        cx2, cy2 = (px1 + px2)/2, (py1 + py2)/2
                        distance = math.sqrt((cx1 - cx2)**2 + (cy1 - cy2)**2)
                        min_distance = min(min_distance, distance)
                else:
                    # First sticker, prefer center
                    cx, cy = x + width/2, y + height/2
                    min_distance = math.sqrt((cx - canvas_width/2)**2 + (cy - canvas_height/2)**2)
                
                candidates.append((x, y, min_distance))
                
                # If we have enough candidates, pick the best one
                if len(candidates) >= 10:
                    break
        
        # Return the position with minimum distance to existing stickers
        if candidates:
            candidates.sort(key=lambda c: c[2])  # Sort by distance
            return candidates[0][0], candidates[0][1]
        
        return None
    
    def generate_poster(self, width: int, height: int, num_stickers: int,
                       min_scale: float = 0.3, max_scale: float = 1.0,
                       max_rotation: float = 30.0,
                       background_color: Tuple[int, int, int] = (255, 255, 255),
                       min_area_ratio: float = 0.0005):
        """Generate poster with random non-overlapping sticker placement."""
        print(f"\nGenerating {width}x{height} poster with {num_stickers} stickers...")
        
        # Create canvas
        canvas = Image.new('RGBA', (width, height), background_color + (255,))
        
        # Shuffle stickers for random selection
        random.shuffle(self.stickers)
        
        # Mix large and small stickers for better variety
        # Sort by size then interleave large and small
        sorted_by_size = sorted(self.stickers[:num_stickers], 
                               key=lambda s: s.get('area', 0), 
                               reverse=True)
        
        # Interleave large and small stickers
        sorted_stickers = []
        mid = len(sorted_by_size) // 2
        for i in range(mid):
            sorted_stickers.append(sorted_by_size[i])  # Large
            if i + mid < len(sorted_by_size):
                sorted_stickers.append(sorted_by_size[i + mid])  # Small
        # Add any remaining
        sorted_stickers.extend(sorted_by_size[len(sorted_stickers):])
        
        placed_count = 0
        attempts = 0
        max_total_attempts = num_stickers * 10  # Prevent infinite loop
        
        for i, sticker_info in enumerate(sorted_stickers):
            if attempts > max_total_attempts:
                print(f"Reached max attempts, placed {placed_count} stickers")
                break
                
            attempts += 1
            
            try:
                # Load sticker
                with Image.open(sticker_info['path']) as sticker:
                    # Convert to RGBA if needed
                    if sticker.mode != 'RGBA':
                        sticker = sticker.convert('RGBA')
                    
                    # Calculate minimum area threshold
                    canvas_area = width * height
                    min_allowed_area = canvas_area * min_area_ratio
                    
                    # Preserve natural size variation with adaptive scaling
                    original_area = sticker.width * sticker.height
                    
                    # Map original areas to scale factors
                    # Tiny stickers (< 5k px²): scale up significantly
                    # Small stickers (5k-20k px²): scale moderately
                    # Medium stickers (20k-100k px²): scale slightly
                    # Large stickers (100k-500k px²): scale down
                    # Huge stickers (> 500k px²): scale down significantly
                    
                    if original_area < 5000:
                        scale = random.uniform(0.7, 1.3)
                    elif original_area < 20000:
                        scale = random.uniform(0.5, 1.0)
                    elif original_area < 100000:
                        scale = random.uniform(0.4, 0.8)
                    elif original_area < 500000:
                        scale = random.uniform(0.25, 0.5)
                    else:
                        scale = random.uniform(0.15, 0.35)
                    
                    # Add some randomness to create more variation
                    scale *= random.uniform(0.85, 1.15)
                    new_width = int(sticker.width * scale)
                    new_height = int(sticker.height * scale)
                    new_area = new_width * new_height
                    
                    # Ensure minimum area is met
                    if new_area < min_allowed_area:
                        # Scale up to meet minimum area requirement
                        scale_factor = math.sqrt(min_allowed_area / new_area)
                        new_width = int(new_width * scale_factor)
                        new_height = int(new_height * scale_factor)
                    
                    new_size = (new_width, new_height)
                    sticker_resized = sticker.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Random rotation
                    rotation = random.uniform(-max_rotation, max_rotation)
                    sticker_rotated = sticker_resized.rotate(rotation, expand=True, fillcolor=(0, 0, 0, 0))
                    
                    # Find non-overlapping position
                    placement = self.find_placement(
                        sticker_rotated.width, sticker_rotated.height,
                        width, height
                    )
                    
                    if placement:
                        x, y = placement
                        
                        # Paste sticker
                        canvas.paste(sticker_rotated, (x, y), sticker_rotated)
                        
                        # Record placement
                        self.placed_regions.append((
                            x, y, 
                            x + sticker_rotated.width, 
                            y + sticker_rotated.height
                        ))
                        
                        placed_count += 1
                        if placed_count % 50 == 0:
                            print(f"  Placed {placed_count}/{num_stickers} stickers...")
                    else:
                        # Could not find non-overlapping position
                        continue
                        
            except Exception as e:
                print(f"Error processing {sticker_info['path']}: {e}")
                continue
        
        print(f"Successfully placed {placed_count} stickers")
        
        # Convert to RGB for saving
        final = Image.new('RGB', (width, height), background_color)
        final.paste(canvas, (0, 0), canvas)
        
        return final, placed_count
    
    def save_poster(self, poster: Image.Image, filename: str, dpi: int = 300):
        """Save the poster."""
        poster.save(filename, dpi=(dpi, dpi))
        print(f"✅ Saved poster to: {filename}")


def main():
    ap = argparse.ArgumentParser(description="Generate random poster with non-overlapping stickers")
    ap.add_argument('--stickers-dir', default='stickers_sam',
                    help='Directory containing sticker subdirectories')
    ap.add_argument('--output', default='random_poster.png',
                    help='Output poster filename')
    ap.add_argument('--width', type=int, default=3840,
                    help='Poster width in pixels (default: 3840 for 4K)')
    ap.add_argument('--height', type=int, default=2160,
                    help='Poster height in pixels (default: 2160 for 4K)')
    ap.add_argument('--num-stickers', type=int, default=200,
                    help='Number of stickers to place (default: 200)')
    ap.add_argument('--min-scale', type=float, default=0.3,
                    help='Minimum sticker scale (default: 0.3)')
    ap.add_argument('--max-scale', type=float, default=1.0,
                    help='Maximum sticker scale (default: 1.0)')
    ap.add_argument('--max-rotation', type=float, default=30.0,
                    help='Maximum rotation in degrees (default: 30)')
    ap.add_argument('--seed', type=int, default=None,
                    help='Random seed for reproducibility')
    ap.add_argument('--dpi', type=int, default=300,
                    help='DPI for output (default: 300)')
    ap.add_argument('--bg-color', nargs=3, type=int, default=[255, 255, 255],
                    help='Background color RGB (default: 255 255 255)')
    ap.add_argument('--min-area-ratio', type=float, default=0.0005,
                    help='Minimum area as ratio of canvas area (default: 0.0005)')
    
    args = ap.parse_args()
    
    # Set random seed if provided
    if args.seed:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")
    
    # Initialize generator
    generator = RandomPosterGenerator(args.stickers_dir)
    
    # Load stickers
    generator.load_stickers()
    
    # Generate poster
    poster, placed = generator.generate_poster(
        args.width, args.height, 
        num_stickers=args.num_stickers,
        min_scale=args.min_scale,
        max_scale=args.max_scale,
        max_rotation=args.max_rotation,
        background_color=tuple(args.bg_color),
        min_area_ratio=args.min_area_ratio
    )
    
    # Save poster
    generator.save_poster(poster, args.output, dpi=args.dpi)
    
    # Print summary
    print(f"\n=== Poster Summary ===")
    print(f"Dimensions: {args.width}x{args.height} pixels")
    print(f"Physical size at {args.dpi} DPI: {args.width/args.dpi:.1f}\" x {args.height/args.dpi:.1f}\"")
    print(f"Stickers placed: {placed} / {args.num_stickers} requested")
    print(f"Placement success rate: {placed/args.num_stickers*100:.1f}%")


if __name__ == '__main__':
    main()
