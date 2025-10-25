#!/usr/bin/env python3
"""
Chapter Analysis and CSV Report Generator
==========================================
Analyzes all chapters and generates a comprehensive CSV report with:
- File presence indicators (V/X for each file type)
- Word and character counts for main.tex files
- Based on what files \inputstory includes

Files analyzed (from \inputstory command):
- title.tex (always required)
- summary.tex (always required) 
- topicmap.tex (optional)
- quote.tex (optional)
- historical.tex (always included)
- main.tex (always included)
- phenomenon_extra.tex (optional)
- technical.tex (always included)
- joke.tex (optional)
- exercises.tex (optional)
- cartoon.tex (optional)
- imagefigure.tex (optional)
"""

import os
import re
import csv
from pathlib import Path
from datetime import datetime

def count_words_and_chars(text):
    """Count words and characters in text, excluding LaTeX commands."""
    # Remove LaTeX comments
    text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)
    
    # Remove LaTeX commands (simple heuristic)
    text = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})*', '', text)
    text = re.sub(r'\\[^a-zA-Z]', '', text)  # Remove \\ \& etc.
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Count
    words = len(text.split()) if text else 0
    chars = len(text) if text else 0
    
    return words, chars

def get_file_stats(file_path):
    """Get word and character count for a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return count_words_and_chars(content)
    except Exception:
        return 0, 0

def analyze_chapter(chapter_dir):
    """Analyze a single chapter directory."""
    chapter_path = Path(chapter_dir)
    
    if not chapter_path.is_dir():
        return None
    
    # Extract chapter number and name
    dir_name = chapter_path.name
    match = re.match(r'(\d+)_(.+)', dir_name)
    if not match:
        return None
    
    chapter_num = int(match.group(1))
    chapter_name = match.group(2)
    
    # Define all possible files based on \inputstory
    files_to_check = {
        # Always required/included
        'title.tex': 'required',
        'summary.tex': 'required', 
        'historical.tex': 'required',
        'main.tex': 'required',
        'technical.tex': 'required',
        
        # Optional files
        'topicmap.tex': 'optional',
        'quote.tex': 'optional',
        'phenomenon_extra.tex': 'optional',
        'joke.tex': 'optional',
        'exercises.tex': 'optional',
        'cartoon.tex': 'optional',
        'imagefigure.tex': 'optional',
    }
    
    result = {
        'chapter_num': chapter_num,
        'chapter_name': chapter_name,
        'folder_name': dir_name,
    }
    
    # Check file presence
    for filename, file_type in files_to_check.items():
        file_path = chapter_path / filename
        exists = file_path.exists()
        result[f'has_{filename.replace(".tex", "")}'] = 'V' if exists else 'X'
        
        # For main.tex, also get word and character counts
        if filename == 'main.tex' and exists:
            words, chars = get_file_stats(file_path)
            result['main_words'] = words
            result['main_characters'] = chars
        elif filename == 'main.tex':
            result['main_words'] = 0
            result['main_characters'] = 0
    
    # Get total file count
    all_tex_files = list(chapter_path.glob('*.tex'))
    result['total_tex_files'] = len(all_tex_files)
    
    # Check for additional files not in standard set
    standard_files = set(files_to_check.keys())
    actual_files = set(f.name for f in all_tex_files)
    extra_files = actual_files - standard_files
    result['extra_files'] = ', '.join(sorted(extra_files)) if extra_files else ''
    
    return result

def find_all_chapters():
    """Find all chapter directories."""
    chapter_dirs = []
    
    for item in Path('.').iterdir():
        if item.is_dir() and re.match(r'\d+_', item.name):
            chapter_dirs.append(item)
    
    return sorted(chapter_dirs, key=lambda x: int(re.match(r'(\d+)_', x.name).group(1)))

def generate_csv_report():
    """Generate comprehensive CSV report of all chapters."""
    print("🔍 CHAPTER ANALYSIS AND CSV REPORT")
    print("=" * 60)
    print("Analyzing chapters based on \\inputstory command...")
    print()
    
    chapters = find_all_chapters()
    if not chapters:
        print("❌ No chapter directories found!")
        return
    
    print(f"📁 Found {len(chapters)} chapter directories")
    
    # Analyze all chapters
    results = []
    total_words = 0
    total_chars = 0
    
    for chapter_dir in chapters:
        print(f"   📖 Analyzing {chapter_dir.name}...")
        result = analyze_chapter(chapter_dir)
        if result:
            results.append(result)
            total_words += result.get('main_words', 0)
            total_chars += result.get('main_characters', 0)
    
    if not results:
        print("❌ No valid chapters found!")
        return
    
    # Generate CSV filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"chapter_analysis_{timestamp}.csv"
    
    # Define CSV columns
    fieldnames = [
        'chapter_num',
        'chapter_name', 
        'folder_name',
        # Required files
        'has_title',
        'has_summary',
        'has_historical',
        'has_main',
        'has_technical',
        # Optional files
        'has_topicmap',
        'has_quote', 
        'has_phenomenon_extra',
        'has_joke',
        'has_exercises',
        'has_cartoon',
        'has_imagefigure',
        # Statistics
        'main_words',
        'main_characters',
        'total_tex_files',
        'extra_files'
    ]
    
    # Write CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print()
    print("=" * 60)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"📁 Chapters analyzed: {len(results)}")
    print(f"📝 Total words in main.tex files: {total_words:,}")
    print(f"🔤 Total characters in main.tex files: {total_chars:,}")
    print(f"📄 CSV report saved: {csv_filename}")
    print()
    
    # Show file presence statistics
    file_stats = {}
    for filename in ['title', 'summary', 'historical', 'main', 'technical', 
                    'topicmap', 'quote', 'phenomenon_extra', 'joke', 
                    'exercises', 'cartoon', 'imagefigure']:
        has_count = sum(1 for r in results if r.get(f'has_{filename}') == 'V')
        file_stats[filename] = has_count
    
    print("📋 FILE PRESENCE SUMMARY:")
    print("   Required files:")
    for filename in ['title', 'summary', 'historical', 'main', 'technical']:
        count = file_stats[filename]
        percentage = (count / len(results)) * 100
        print(f"     {filename}.tex: {count}/{len(results)} ({percentage:.1f}%)")
    
    print("   Optional files:")
    for filename in ['topicmap', 'quote', 'phenomenon_extra', 'joke', 
                    'exercises', 'cartoon', 'imagefigure']:
        count = file_stats[filename]
        percentage = (count / len(results)) * 100
        print(f"     {filename}.tex: {count}/{len(results)} ({percentage:.1f}%)")
    
    print()
    print("📈 TOP 10 CHAPTERS BY WORD COUNT (main.tex):")
    sorted_by_words = sorted(results, key=lambda x: x.get('main_words', 0), reverse=True)
    for i, chapter in enumerate(sorted_by_words[:10], 1):
        words = chapter.get('main_words', 0)
        print(f"   {i:2}. Ch.{chapter['chapter_num']:02d} {chapter['chapter_name']}: {words:,} words")
    
    print()
    print("📋 LEGEND:")
    print("   V = File exists")
    print("   X = File missing")
    print("   main_words/main_characters = Word/character count in main.tex (LaTeX commands excluded)")
    print("   extra_files = Additional .tex files not in standard \\inputstory set")

def main():
    """Main execution function."""
    print("🚀 CHAPTER ANALYSIS TOOL")
    print("=" * 60)
    print("Based on \\inputstory command from preamble.tex")
    print("Generating comprehensive CSV report...")
    print()
    
    # Check if we're in the right directory
    if not Path('.').name.startswith('MainBook'):
        print("⚠️  Warning: Not in MainBook directory")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    generate_csv_report()

if __name__ == "__main__":
    main() 