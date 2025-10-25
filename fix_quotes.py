#!/usr/bin/env python3
"""
Script to replace curly quotes with straight quotes in all relevant files.
"""

import os
import glob

def fix_quotes_in_file(file_path):
    """Replace curly quotes with straight quotes in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Define replacements - order matters to avoid conflicts
        replacements = [
            ('""', '""'),  # LaTeX opening double quotes
            ("""", '""'),  # LaTeX closing double quotes
            ('"', '"'),    # Left double quote
            ('"', '"'),    # Right double quote
            (''', "'"),    # Left single quote
            ("'", "'"),    # Right single quote
        ]

        for old, new in replacements:
            content = content.replace(old, new)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    # Find all files to process
    file_patterns = ['*.tex', '*.md', '*.py', '*.txt', '*.sh', '*.svg', '*.opf']
    files = []

    for pattern in file_patterns:
        files.extend(glob.glob(f'**/{pattern}', recursive=True))

    print(f'Found {len(files)} files to process...')

    updated_count = 0
    for file_path in files:
        if os.path.exists(file_path):
            if fix_quotes_in_file(file_path):
                updated_count += 1
                print(f'Updated: {file_path}')

    print(f'Updated {updated_count} files.')

if __name__ == '__main__':
    main()
