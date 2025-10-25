#!/usr/bin/env python3
"""
Chapter Page Analysis Tool
==========================
Analyzes the compiled LaTeX document to determine:
- How many pages each chapter occupies
- Page distribution statistics
- Chapter density metrics

Methods:
1. Parse .toc file for chapter start pages
2. Optionally analyze PDF directly for verification
3. Generate comprehensive CSV report with statistics

Usage:
    python analyze_chapter_pages.py [basename]
    
    basename: Base filename without extension (default: "main")
              Examples: "main", "main_sidenotes"
"""

import os
import re
import csv
from pathlib import Path
from datetime import datetime
import subprocess
import sys
import argparse

# Optional PDF analysis
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

def parse_toc_file(basename="main"):
    """Parse LaTeX .toc file to extract chapter information."""
    toc_path = f"{basename}.toc"
    if not os.path.exists(toc_path):
        print(f"❌ TOC file not found: {toc_path}")
        return []
    
    chapters = []
    
    try:
        with open(toc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse TOC entries for chapters - use the working pattern from debug
        # Format: \contentsline {chapter}{\numberline {1}Chapter Title \\ {...long summary...}}{page}{chapter.1}
        chapter_pattern = r'\\contentsline\s*\{chapter\}\s*\{\\numberline\s*\{(\d+)\}.*?\}\s*\{(\d+)\}'
        
        matches = re.findall(chapter_pattern, content)
        
        for match in matches:
            chapter_num = int(match[0])
            start_page = int(match[1])
            
            # Extract the title by finding the line and parsing it more carefully
            chapter_line_pattern = r'\\contentsline\s*\{chapter\}\s*\{\\numberline\s*\{' + str(chapter_num) + r'\}([^}]*?)(?:\s*\\\\|\})'
            title_match = re.search(chapter_line_pattern, content)
            
            if title_match:
                chapter_title = title_match.group(1).strip()
            else:
                chapter_title = f"Chapter {chapter_num}"
            
            chapters.append({
                'chapter_num': chapter_num,
                'chapter_title': chapter_title,
                'start_page': start_page
            })
    
    except Exception as e:
        print(f"❌ Error parsing TOC file: {e}")
        return []
    
    return sorted(chapters, key=lambda x: x['chapter_num'])

def get_total_pages_from_log(basename="main"):
    """Extract total page count from LaTeX log file."""
    log_path = f"{basename}.log"
    if not os.path.exists(log_path):
        return None
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for "Output written on basename.pdf (XXX pages"
        match = re.search(r'Output written on [^(]*\((\d+) pages', content)
        if match:
            return int(match.group(1))
    
    except Exception as e:
        print(f"⚠️  Could not read log file: {e}")
    
    return None

def get_pdf_page_count(basename="main"):
    """Get page count directly from PDF file."""
    pdf_path = f"{basename}.pdf"
    if not os.path.exists(pdf_path):
        return None
    
    if HAS_PYPDF2:
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return len(reader.pages)
        except Exception as e:
            print(f"⚠️  Could not read PDF with PyPDF2: {e}")
    
    # Fallback: try using pdfinfo if available
    try:
        result = subprocess.run(['pdfinfo', pdf_path], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            match = re.search(r'Pages:\s*(\d+)', result.stdout)
            if match:
                return int(match.group(1))
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    return None

def calculate_chapter_lengths(chapters, total_pages):
    """Calculate page length for each chapter."""
    if not chapters:
        return []
    
    results = []
    
    for i, chapter in enumerate(chapters):
        # Calculate end page
        if i < len(chapters) - 1:
            # End page is one less than next chapter's start page
            end_page = chapters[i + 1]['start_page'] - 1
        else:
            # Last chapter goes to end of document
            end_page = total_pages if total_pages else chapter['start_page']
        
        length = max(1, end_page - chapter['start_page'] + 1)
        
        result = {
            'chapter_num': chapter['chapter_num'],
            'chapter_title': chapter['chapter_title'],
            'start_page': chapter['start_page'],
            'end_page': end_page,
            'page_length': length
        }
        
        results.append(result)
    
    return results

def get_chapter_folder_info(basename="main"):
    """Get chapter folder information by parsing the actual inclusion order."""
    folders = {}
    
    # Try to read the main tex file to get actual chapter order
    tex_file = f"{basename}.tex"
    if os.path.exists(tex_file):
        try:
            with open(tex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove comment blocks first
            # Remove \begin{comment}...\end{comment} blocks
            content_no_comments = re.sub(r'\\begin\{comment\}.*?\\end\{comment\}', '', content, flags=re.DOTALL)
            
            # Find all \inputstory{folder_name} entries in order
            input_pattern = r'\\inputstory\{([^}]+)\}'
            matches = re.findall(input_pattern, content_no_comments)
            
            for chapter_position, folder_name in enumerate(matches, 1):
                if os.path.exists(folder_name):
                    # Extract the descriptive name (after the number prefix)
                    folder_match = re.match(r'(\d+)_(.+)', folder_name)
                    if folder_match:
                        descriptive_name = folder_match.group(2)
                    else:
                        descriptive_name = folder_name
                    
                    folders[chapter_position] = {
                        'folder_name': descriptive_name,
                        'full_folder': folder_name
                    }
        
        except Exception as e:
            print(f"⚠️  Could not parse chapter order from {tex_file}: {e}")
    
    # Fallback to old method if parsing failed
    if not folders:
        print("⚠️  Using folder number fallback (may be inaccurate)")
        for item in Path('.').iterdir():
            if item.is_dir() and re.match(r'\d+_', item.name):
                match = re.match(r'(\d+)_(.+)', item.name)
                if match:
                    chapter_num = int(match.group(1))
                    folder_name = match.group(2)
                    folders[chapter_num] = {
                        'folder_name': folder_name,
                        'full_folder': item.name
                    }
    
    return folders

def analyze_chapter_pages(basename="main"):
    """Main analysis function."""
    print("📊 CHAPTER PAGE ANALYSIS")
    print("=" * 60)
    print(f"Analyzing compiled document page distribution for: {basename}")
    print()
    
    # Parse TOC file
    print("📖 Parsing table of contents...")
    chapters = parse_toc_file(basename)
    
    if not chapters:
        print("❌ No chapters found in TOC file!")
        return
    
    print(f"   ✅ Found {len(chapters)} chapters in TOC")
    
    # Get total page count
    print("📄 Determining total page count...")
    total_pages = get_total_pages_from_log(basename)
    if total_pages:
        print(f"   ✅ From log file: {total_pages} pages")
    else:
        total_pages = get_pdf_page_count(basename)
        if total_pages:
            print(f"   ✅ From PDF file: {total_pages} pages")
        else:
            print("   ⚠️  Could not determine total pages, estimating...")
            total_pages = chapters[-1]['start_page'] + 10  # Rough estimate
    
    # Calculate chapter lengths
    print("📏 Calculating chapter page lengths...")
    results = calculate_chapter_lengths(chapters, total_pages)
    
    # Get folder information
    folders = get_chapter_folder_info(basename)
    
    # Enhance results with folder info
    for result in results:
        chapter_num = result['chapter_num']
        if chapter_num in folders:
            result['folder_name'] = folders[chapter_num]['folder_name']
            result['full_folder'] = folders[chapter_num]['full_folder']
        else:
            result['folder_name'] = 'Unknown'
            result['full_folder'] = f"Chapter{chapter_num:02d}"
    
    return results, total_pages

def generate_statistics(results):
    """Generate comprehensive statistics."""
    if not results:
        return {}
    
    lengths = [r['page_length'] for r in results]
    
    stats = {
        'total_chapters': len(results),
        'total_pages': sum(lengths),
        'avg_length': sum(lengths) / len(lengths),
        'median_length': sorted(lengths)[len(lengths) // 2],
        'min_length': min(lengths),
        'max_length': max(lengths),
        'std_dev': (sum((x - sum(lengths)/len(lengths))**2 for x in lengths) / len(lengths))**0.5
    }
    
    return stats

def save_csv_report(results, stats, basename="main"):
    """Save detailed CSV report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"chapter_pages_analysis_{basename}_{timestamp}.csv"
    
    fieldnames = [
        'chapter_num',
        'chapter_title', 
        'folder_name',
        'full_folder',
        'start_page',
        'end_page',
        'page_length'
    ]
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"📄 CSV report saved: {csv_filename}")
    return csv_filename

def display_results(results, stats, total_pages):
    """Display comprehensive analysis results."""
    if not results:
        return
    
    print()
    print("=" * 60)
    print("📊 PAGE DISTRIBUTION ANALYSIS")
    print("=" * 60)
    
    # Summary statistics
    print(f"📚 Document Summary:")
    print(f"   📖 Total chapters: {stats['total_chapters']}")
    print(f"   📄 Total pages: {total_pages}")
    print(f"   📊 Average chapter length: {stats['avg_length']:.1f} pages")
    print(f"   📊 Median chapter length: {stats['median_length']} pages")
    print(f"   📊 Range: {stats['min_length']}-{stats['max_length']} pages")
    print(f"   📊 Standard deviation: {stats['std_dev']:.1f} pages")
    print()
    
    # Top 10 longest chapters
    print("📈 TOP 10 LONGEST CHAPTERS:")
    sorted_by_length = sorted(results, key=lambda x: x['page_length'], reverse=True)
    for i, chapter in enumerate(sorted_by_length[:10], 1):
        title = chapter['chapter_title'][:40] + "..." if len(chapter['chapter_title']) > 40 else chapter['chapter_title']
        print(f"   {i:2}. Ch.{chapter['chapter_num']:02d}: {chapter['page_length']:2d} pages - {title}")
    
    print()
    
    # Top 10 shortest chapters
    print("📉 TOP 10 SHORTEST CHAPTERS:")
    sorted_by_length_asc = sorted(results, key=lambda x: x['page_length'])
    for i, chapter in enumerate(sorted_by_length_asc[:10], 1):
        title = chapter['chapter_title'][:40] + "..." if len(chapter['chapter_title']) > 40 else chapter['chapter_title']
        print(f"   {i:2}. Ch.{chapter['chapter_num']:02d}: {chapter['page_length']:2d} pages - {title}")
    
    print()
    
    # Page length distribution
    print("📊 PAGE LENGTH DISTRIBUTION:")
    length_counts = {}
    for result in results:
        length = result['page_length']
        length_counts[length] = length_counts.get(length, 0) + 1
    
    for length in sorted(length_counts.keys()):
        count = length_counts[length]
        percentage = (count / len(results)) * 100
        bar = "█" * min(20, count)
        print(f"   {length:2d} pages: {count:2d} chapters ({percentage:4.1f}%) {bar}")

def cleanup_old_csvs():
    """Remove old chapter analysis CSV files from previous runs."""
    pattern = "chapter_pages_analysis_*.csv"
    old_files = list(Path('.').glob(pattern))
    
    if old_files:
        print(f"🧹 Cleaning up {len(old_files)} old CSV files...")
        for file in old_files:
            try:
                file.unlink()
                print(f"   🗑️  Deleted: {file.name}")
            except Exception as e:
                print(f"   ⚠️  Could not delete {file.name}: {e}")
        print()

def main():
    """Main execution function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Analyze chapter page distribution in compiled LaTeX document",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_chapter_pages.py                    # Analyze main.pdf
  python analyze_chapter_pages.py main_sidenotes    # Analyze main_sidenotes.pdf
        """
    )
    parser.add_argument(
        'basename', 
        nargs='?', 
        default='main',
        help='Base filename without extension (default: main)'
    )
    
    args = parser.parse_args()
    basename = args.basename
    
    # Clean up old CSV files first
    cleanup_old_csvs()
    
    print("🚀 CHAPTER PAGE ANALYSIS TOOL")
    print("=" * 60)
    print(f"Analyzing page distribution across chapters for: {basename}")
    
    if HAS_PYPDF2:
        print("✅ PyPDF2 available for PDF analysis")
    else:
        print("⚠️  PyPDF2 not available, using alternative methods")
        print("   Install with: pip install PyPDF2")
    
    print()
    
    # Check if we're in the right directory
    base_files = list(Path('.').glob(f'{basename}.*'))
    if not base_files:
        print(f"⚠️  Warning: No {basename}.* files found")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    else:
        print(f"✅ Found files: {', '.join(f.name for f in base_files)}")
    
    # Run analysis
    try:
        results, total_pages = analyze_chapter_pages(basename)
        
        if not results:
            print("❌ Analysis failed - no results generated")
            return
        
        stats = generate_statistics(results)
        csv_filename = save_csv_report(results, stats, basename)
        display_results(results, stats, total_pages)
        
        print()
        print("✨ Analysis complete!")
        print(f"📄 Detailed report: {csv_filename}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    main() 