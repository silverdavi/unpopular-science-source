#!/usr/bin/env python3
import os
import argparse
from PIL import Image
from pathlib import Path
import numpy as np
import math


def analyze_stickers(stickers_dir: str, min_area_cm2: float = 1.0):
    """
    Analyze all stickers to determine optimal poster size.
    
    Args:
        stickers_dir: Directory containing sticker subdirectories
        min_area_cm2: Minimum area per sticker in cm²
    """
    sticker_info = []
    total_pixels = 0
    
    # Walk through all subdirectories
    for chapter_dir in sorted(Path(stickers_dir).iterdir()):
        if not chapter_dir.is_dir():
            continue
            
        chapter_name = chapter_dir.name
        
        # Find all PNG files in this chapter
        for sticker_path in sorted(chapter_dir.glob("*.png")):
            try:
                with Image.open(sticker_path) as img:
                    width, height = img.size
                    area = width * height
                    total_pixels += area
                    
                    sticker_info.append({
                        'chapter': chapter_name,
                        'filename': sticker_path.name,
                        'path': sticker_path,
                        'width': width,
                        'height': height,
                        'area': area,
                        'aspect_ratio': width / height if height > 0 else 1
                    })
            except Exception as e:
                print(f"Error reading {sticker_path}: {e}")
    
    print(f"\n=== Sticker Analysis ===")
    print(f"Total stickers found: {len(sticker_info)}")
    print(f"Total chapters: {len(set(s['chapter'] for s in sticker_info))}")
    
    # Calculate statistics
    areas = [s['area'] for s in sticker_info]
    widths = [s['width'] for s in sticker_info]
    heights = [s['height'] for s in sticker_info]
    
    print(f"\nSize statistics:")
    print(f"  Average area: {np.mean(areas):,.0f} px²")
    print(f"  Median area: {np.median(areas):,.0f} px²")
    print(f"  Min area: {min(areas):,} px²")
    print(f"  Max area: {max(areas):,} px²")
    print(f"  Average dimensions: {np.mean(widths):.0f} x {np.mean(heights):.0f} px")
    
    # Stickers per chapter
    chapters = {}
    for s in sticker_info:
        chapters[s['chapter']] = chapters.get(s['chapter'], 0) + 1
    
    print(f"\nStickers per chapter:")
    print(f"  Average: {np.mean(list(chapters.values())):.1f}")
    print(f"  Min: {min(chapters.values())}")
    print(f"  Max: {max(chapters.values())}")
    
    return sticker_info, total_pixels


def calculate_poster_dimensions(sticker_info, total_pixels, min_area_cm2=1.0, dpi=300):
    """
    Calculate optimal poster dimensions based on sticker analysis.
    """
    num_stickers = len(sticker_info)
    
    # Calculate minimum total area needed
    min_area_cm2_total = num_stickers * min_area_cm2
    
    # Convert to inches (1 inch = 2.54 cm)
    min_area_in2_total = min_area_cm2_total / (2.54 ** 2)
    
    # Add padding factor (stickers won't pack perfectly)
    packing_efficiency = 0.7  # Assume 70% efficient packing
    required_area_in2 = min_area_in2_total / packing_efficiency
    
    print(f"\n=== Poster Size Calculation ===")
    print(f"Number of stickers: {num_stickers}")
    print(f"Min area per sticker: {min_area_cm2} cm²")
    print(f"Total min area needed: {min_area_cm2_total:.1f} cm²")
    print(f"With packing efficiency ({packing_efficiency:.0%}): {required_area_in2 * 2.54**2:.1f} cm²")
    
    # Calculate dimensions for different aspect ratios
    aspect_ratios = [
        (1.0, "Square"),
        (1.414, "ISO A series (√2)"),
        (1.5, "Photo 3:2"),
        (1.618, "Golden ratio"),
        (2.0, "Double square")
    ]
    
    print(f"\nPoster dimension options at {dpi} DPI:")
    print(f"{'Aspect':<15} {'Width':<12} {'Height':<12} {'Area':<15} {'Pixels'}")
    print("-" * 70)
    
    recommendations = []
    
    for ratio, name in aspect_ratios:
        # width * height = area, width/height = ratio
        # height = sqrt(area/ratio)
        height_in = math.sqrt(required_area_in2 / ratio)
        width_in = height_in * ratio
        
        area_in2 = width_in * height_in
        area_cm2 = area_in2 * (2.54 ** 2)
        
        width_px = int(width_in * dpi)
        height_px = int(height_in * dpi)
        total_px = width_px * height_px
        
        # Calculate average pixels per sticker
        avg_px_per_sticker = total_px * packing_efficiency / num_stickers
        
        recommendations.append({
            'name': name,
            'ratio': ratio,
            'width_in': width_in,
            'height_in': height_in,
            'width_cm': width_in * 2.54,
            'height_cm': height_in * 2.54,
            'width_px': width_px,
            'height_px': height_px,
            'total_px': total_px,
            'avg_px_per_sticker': avg_px_per_sticker
        })
        
        print(f"{name:<15} {width_in:>6.1f}\" x {height_in:>6.1f}\" "
              f"{area_cm2:>7.0f} cm²   {width_px:>5} x {height_px:<5}")
    
    # Check against average sticker size
    avg_sticker_area = np.mean([s['area'] for s in sticker_info])
    
    print(f"\nAverage sticker area: {avg_sticker_area:,.0f} px²")
    print(f"\nPixels per sticker at different poster sizes:")
    
    for rec in recommendations:
        scale_factor = math.sqrt(rec['avg_px_per_sticker'] / avg_sticker_area)
        print(f"  {rec['name']:<15}: {rec['avg_px_per_sticker']:>8,.0f} px² "
              f"(scale: {scale_factor:.2f}x)")
    
    return recommendations


def main():
    ap = argparse.ArgumentParser(description="Analyze stickers to determine optimal poster size")
    ap.add_argument('--stickers-dir', default='stickers_sam',
                    help='Directory containing sticker subdirectories')
    ap.add_argument('--min-area', type=float, default=1.0,
                    help='Minimum area per sticker in cm²')
    ap.add_argument('--dpi', type=int, default=300,
                    help='DPI for poster output')
    args = ap.parse_args()
    
    # Get absolute path
    stickers_path = Path(args.stickers_dir).resolve()
    
    if not stickers_path.exists():
        print(f"Error: Stickers directory not found: {stickers_path}")
        return
    
    # Analyze stickers
    sticker_info, total_pixels = analyze_stickers(stickers_path, args.min_area)
    
    if not sticker_info:
        print("No stickers found!")
        return
    
    # Calculate poster dimensions
    recommendations = calculate_poster_dimensions(
        sticker_info, total_pixels, args.min_area, args.dpi
    )
    
    # Save analysis results
    output_file = "sticker_analysis_results.txt"
    with open(output_file, 'w') as f:
        f.write(f"Sticker Analysis Results\n")
        f.write(f"========================\n\n")
        f.write(f"Total stickers: {len(sticker_info)}\n")
        f.write(f"Minimum area per sticker: {args.min_area} cm²\n")
        f.write(f"DPI: {args.dpi}\n\n")
        
        f.write("Recommended poster sizes:\n")
        for rec in recommendations:
            f.write(f"\n{rec['name']}:\n")
            f.write(f"  Dimensions: {rec['width_cm']:.1f} x {rec['height_cm']:.1f} cm\n")
            f.write(f"  Pixels: {rec['width_px']} x {rec['height_px']}\n")
            f.write(f"  Average area per sticker: {rec['avg_px_per_sticker']:,.0f} px²\n")
    
    print(f"\n✅ Analysis saved to: {output_file}")


if __name__ == '__main__':
    main()
