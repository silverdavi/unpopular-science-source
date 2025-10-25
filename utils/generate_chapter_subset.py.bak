#!/usr/bin/env python3
"""
Generate a custom main_ch.tex file with only selected chapters.
This allows compiling a subset of the book for faster testing.
"""

import re
import argparse
import sys
from pathlib import Path

class ChapterExtractor:
    def __init__(self, main_tex_path='main.tex'):
        self.main_tex_path = Path(main_tex_path)
        self.chapters = []
        self.preamble = []
        self.postamble = []
        
    def parse_main_tex(self):
        """Parse main.tex to extract chapters and document structure."""
        if not self.main_tex_path.exists():
            raise FileNotFoundError(f"Cannot find {self.main_tex_path}")
            
        with open(self.main_tex_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find where chapters start and end
        chapter_start_idx = None
        chapter_end_idx = None
        
        for i, line in enumerate(lines):
            # First chapter starts after prologue
            if chapter_start_idx is None and '\\chapterwithsummaryfromfile' in line and not line.strip().startswith('%'):
                chapter_start_idx = i
            # Last chapter before \end{document}
            if '\\end{document}' in line:
                chapter_end_idx = i
                break
        
        # Extract sections
        self.preamble = lines[:chapter_start_idx]
        self.postamble = lines[chapter_end_idx:]
        
        # Extract chapters
        i = chapter_start_idx
        while i < chapter_end_idx:
            line = lines[i]
            if '\\chapterwithsummaryfromfile' in line and not line.strip().startswith('%'):
                # Extract chapter info
                match = re.search(r'\\chapterwithsummaryfromfile\[([^\]]+)\]\{([^\}]+)\}', line)
                if match:
                    label = match.group(1)
                    directory = match.group(2)
                    
                    # Get chapter number from directory name
                    num_match = re.match(r'(\d+)_', directory)
                    chapter_num = int(num_match.group(1)) if num_match else None
                    
                    # Look for the corresponding \inputstory line
                    inputstory_line = None
                    comment = ""
                    if i + 1 < chapter_end_idx:
                        next_line = lines[i + 1]
                        if '\\inputstory' in next_line:
                            inputstory_line = next_line
                            # Extract comment if present
                            comment_match = re.search(r'%(.+)$', next_line)
                            if comment_match:
                                comment = comment_match.group(1).strip()
                    
                    self.chapters.append({
                        'number': chapter_num,
                        'label': label,
                        'directory': directory,
                        'chapterwithsummary_line': line,
                        'inputstory_line': inputstory_line,
                        'comment': comment,
                        'line_index': i
                    })
            i += 1
        
        print(f"Found {len(self.chapters)} chapters in {self.main_tex_path}")
        
    def list_chapters(self):
        """Display all available chapters."""
        print("\nAvailable chapters:")
        print("-" * 80)
        print(f"{'#':>3} | {'Directory':<35} | {'Label':<25} | {'Status':<10}")
        print("-" * 80)
        
        for ch in sorted(self.chapters, key=lambda x: x['number'] if x['number'] else 999):
            num = str(ch['number']) if ch['number'] else '??'
            status = ch['comment'] if ch['comment'] else ''
            print(f"{num:>3} | {ch['directory']:<35} | {ch['label']:<25} | {status:<10}")
        
    def parse_chapter_spec(self, spec):
        """Parse chapter specification into list of chapter numbers/directories."""
        selected = []
        
        # Split by comma
        parts = spec.split(',')
        
        for part in parts:
            part = part.strip()
            
            # Check if it's a range (e.g., "1-5")
            if '-' in part and part[0].isdigit():
                try:
                    start, end = map(int, part.split('-'))
                    selected.extend(range(start, end + 1))
                except ValueError:
                    print(f"Warning: Invalid range '{part}', skipping")
                    
            # Check if it's a number
            elif part.isdigit():
                selected.append(int(part))
                
            # Otherwise treat as directory name or partial match
            else:
                # Find chapters matching this string
                matches = [ch for ch in self.chapters 
                          if part.lower() in ch['directory'].lower()]
                if matches:
                    for match in matches:
                        if match['number']:
                            selected.append(match['number'])
                else:
                    print(f"Warning: No chapter found matching '{part}'")
        
        # Remove duplicates and sort
        return sorted(set(selected))
    
    def generate_subset_tex(self, chapter_numbers, output_file='main_ch.tex'):
        """Generate a new tex file with only specified chapters."""
        
        # Filter chapters
        selected_chapters = [ch for ch in self.chapters 
                           if ch['number'] in chapter_numbers]
        
        if not selected_chapters:
            print("Error: No valid chapters selected!")
            return False
        
        # Sort by original order in file
        selected_chapters.sort(key=lambda x: x['line_index'])
        
        print(f"\nGenerating {output_file} with {len(selected_chapters)} chapters:")
        for ch in selected_chapters:
            print(f"  - Chapter {ch['number']}: {ch['directory']}")
        
        # Build output
        output_lines = []
        
        # Add preamble
        output_lines.extend(self.preamble)
        
        # Add comment about this being a subset
        output_lines.append("\n% This is a generated subset of chapters\n")
        output_lines.append(f"% Selected chapters: {', '.join(map(str, sorted(chapter_numbers)))}\n")
        output_lines.append("% Generated by utils/generate_chapter_subset.py\n\n")
        
        # Add selected chapters
        for ch in selected_chapters:
            output_lines.append(ch['chapterwithsummary_line'])
            if ch['inputstory_line']:
                output_lines.append(ch['inputstory_line'])
            output_lines.append("\n")
        
        # Add postamble
        output_lines.extend(self.postamble)
        
        # Write output file
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)
        
        print(f"\n✅ Successfully generated {output_file}")
        print(f"   You can now compile with: python3 utils/compile_realtime.py {output_file}")
        
        return True

def main():
    parser = argparse.ArgumentParser(
        description='Generate a LaTeX file with a subset of chapters for faster compilation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all chapters
  python3 utils/generate_chapter_subset.py --list
  
  # Generate with specific chapters
  python3 utils/generate_chapter_subset.py 1,3,5
  python3 utils/generate_chapter_subset.py 1-5,10,15-20
  
  # Generate using directory names (partial match)
  python3 utils/generate_chapter_subset.py Banach,Gold,Circle
  
  # Mix numbers and names
  python3 utils/generate_chapter_subset.py 1-3,Maxwell,49,Langtons
  
  # Custom output file
  python3 utils/generate_chapter_subset.py 1,2,3 -o main_first3.tex
        """
    )
    
    parser.add_argument('chapters', nargs='?', 
                      help='Comma-separated list of chapters (numbers, ranges, or directory names)')
    parser.add_argument('-l', '--list', action='store_true',
                      help='List all available chapters')
    parser.add_argument('-o', '--output', default='main_ch.tex',
                      help='Output filename (default: main_ch.tex)')
    parser.add_argument('-i', '--input', default='main.tex',
                      help='Input main.tex file (default: main.tex)')
    
    args = parser.parse_args()
    
    # Create extractor
    extractor = ChapterExtractor(args.input)
    
    try:
        extractor.parse_main_tex()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # List chapters if requested
    if args.list:
        extractor.list_chapters()
        sys.exit(0)
    
    # Check if chapters specified
    if not args.chapters:
        print("❌ Error: No chapters specified!")
        print("   Use --list to see available chapters")
        print("   Use --help for usage examples")
        sys.exit(1)
    
    # Parse chapter specification
    chapter_numbers = extractor.parse_chapter_spec(args.chapters)
    
    if not chapter_numbers:
        print("❌ Error: No valid chapters found in specification")
        sys.exit(1)
    
    # Generate subset file
    success = extractor.generate_subset_tex(chapter_numbers, args.output)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
