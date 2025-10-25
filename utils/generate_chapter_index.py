#!/usr/bin/env python3
"""
Generate a comprehensive CSV index of all chapters in the book.
"""

import os
import csv
import re
from pathlib import Path

def extract_title_content(file_path):
    """Extract the content from title.tex file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # Remove LaTeX commands and clean up
            content = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', content)
            content = re.sub(r'\\[a-zA-Z]+', '', content)
            content = re.sub(r'[{}]', '', content)
            content = re.sub(r'\s+', ' ', content).strip()
            return content
    except:
        return "N/A"

def find_pdf_files(chapter_dir):
    """Find all PDF files in the chapter directory."""
    pdf_files = []
    try:
        for file in os.listdir(chapter_dir):
            if file.endswith('.pdf'):
                pdf_files.append(file)
    except:
        pass
    return pdf_files

def check_file_exists(chapter_dir, filename):
    """Check if a specific file exists in the chapter directory."""
    return os.path.exists(os.path.join(chapter_dir, filename))

def get_chapter_topic(folder_name):
    """Extract the topic name from folder name (after underscore)."""
    parts = folder_name.split('_', 1)
    if len(parts) > 1:
        return parts[1]
    return folder_name

def main():
    # Get all chapter directories
    chapters = []
    
    for item in sorted(os.listdir('.')):
        if os.path.isdir(item) and re.match(r'^\d{2}_', item):
            chapters.append(item)
    
    # Prepare CSV data
    csv_data = []
    headers = [
        'Number',
        'Folder Name',
        'Topic',
        'Title',
        'Main PDF',
        'Other PDFs',
        'Has title.tex',
        'Has summary.tex',
        'Has main.tex',
        'Has technical.tex',
        'Has historical.tex',
        'Has sidenote.tex',
        'Has topicmap.tex',
        'Has quote.tex',
        'Has exercises.tex',
        'Has joke.tex',
        'Has Images'
    ]
    
    for chapter_folder in chapters:
        # Extract chapter number
        chapter_num = int(chapter_folder[:2])
        
        # Get topic from folder name
        topic = get_chapter_topic(chapter_folder)
        
        # Extract title
        title_path = os.path.join(chapter_folder, 'title.tex')
        title_content = extract_title_content(title_path)
        
        # Find PDF files
        pdf_files = find_pdf_files(chapter_folder)
        main_pdf = None
        other_pdfs = []
        
        for pdf in pdf_files:
            if pdf.startswith(f'{chapter_num:02d}_'):
                main_pdf = pdf
            else:
                other_pdfs.append(pdf)
        
        # Check for various tex files
        tex_files = {
            'title.tex': check_file_exists(chapter_folder, 'title.tex'),
            'summary.tex': check_file_exists(chapter_folder, 'summary.tex'),
            'main.tex': check_file_exists(chapter_folder, 'main.tex'),
            'technical.tex': check_file_exists(chapter_folder, 'technical.tex'),
            'historical.tex': check_file_exists(chapter_folder, 'historical.tex'),
            'sidenote.tex': check_file_exists(chapter_folder, 'sidenote.tex'),
            'topicmap.tex': check_file_exists(chapter_folder, 'topicmap.tex'),
            'quote.tex': check_file_exists(chapter_folder, 'quote.tex'),
            'exercises.tex': check_file_exists(chapter_folder, 'exercises.tex'),
            'joke.tex': check_file_exists(chapter_folder, 'joke.tex')
        }
        
        # Check for images
        image_extensions = ['.png', '.jpg', '.jpeg', '.pdf']
        has_images = False
        for file in os.listdir(chapter_folder):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                has_images = True
                break
        
        # Add row to CSV data
        row = [
            chapter_num,
            chapter_folder,
            topic,
            title_content,
            main_pdf or '',
            '; '.join(other_pdfs),
            'Yes' if tex_files['title.tex'] else 'No',
            'Yes' if tex_files['summary.tex'] else 'No',
            'Yes' if tex_files['main.tex'] else 'No',
            'Yes' if tex_files['technical.tex'] else 'No',
            'Yes' if tex_files['historical.tex'] else 'No',
            'Yes' if tex_files['sidenote.tex'] else 'No',
            'Yes' if tex_files['topicmap.tex'] else 'No',
            'Yes' if tex_files['quote.tex'] else 'No',
            'Yes' if tex_files['exercises.tex'] else 'No',
            'Yes' if tex_files['joke.tex'] else 'No',
            'Yes' if has_images else 'No'
        ]
        csv_data.append(row)
    
    # Write CSV file
    output_file = 'chapter_index.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(csv_data)
    
    print(f"✅ Chapter index created: {output_file}")
    print(f"📊 Total chapters indexed: {len(csv_data)}")
    
    # Print summary statistics
    total_with_exercises = sum(1 for row in csv_data if row[14] == 'Yes')
    total_with_jokes = sum(1 for row in csv_data if row[15] == 'Yes')
    total_with_images = sum(1 for row in csv_data if row[16] == 'Yes')
    
    print(f"\n📈 Statistics:")
    print(f"  - Chapters with exercises: {total_with_exercises}")
    print(f"  - Chapters with jokes: {total_with_jokes}")
    print(f"  - Chapters with images: {total_with_images}")

if __name__ == "__main__":
    main()