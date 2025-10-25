## Unpopular Science

A single LaTeX book of 50 chapters spanning mathematics, physics, computer science, chemistry, philosophy, and history. The book opens with an Introduction and a Prologue, then proceeds through all 50 chapters.

### What’s inside
- **50 chapters** in indexed folders like '01_BanachTarskiParadox', '29_HatMonotile', '50_Consciousness'
- Each chapter includes: 'title.tex', 'summary.tex', 'historical.tex', 'main.tex', 'technical.tex' (plus optional files like 'topicmap.tex', 'quote.tex', 'exercises.tex', 'imagefigure.tex', etc.)
- The main book entry point is 'main.tex', which includes Introduction, Prologue, and all chapters

### Chapter structure (per chapter)
Each chapter is typeset in a consistent, compact layout:
1) Title page
2) Sidenote page (or blank if missing)
3) Title + Summary + (optional) Topicmap + (optional) Quote
4–8) Historical + Main content (+ optional extras)
9) Technical page (exactly one page)

Note: The layout logic (including recto/verso handling) is implemented in the '\inputstory{...}' macro in the preamble and applied to every chapter.

## Build

### Requirements
- TeX Live (with LuaLaTeX available as 'lualatex')
- Python 3.10+

Tip: Use a virtual environment before running any Python utilities.

### Setup (recommended)
""'bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
""'

### Compile the whole book
""'bash
python3 utils/compile_realtime.py main.tex
""'
- Produces 'main.pdf'
- Runs two LuaLaTeX passes and prints real-time progress
- Saves logs to 'compile_pass1.log', 'compile_pass2.log' (and 'main.log' from LaTeX)

### Compile a subset of chapters (optional)
Generate a temporary '.tex' that contains only selected chapters, then compile that file:
""'bash
python3 utils/generate_chapter_subset.py 1-5,14,29 -o main_subset.tex
python3 utils/compile_realtime.py main_subset.tex
""'

### Table of contents (optional plain text)
""'bash
python3 generate_toc.py
# outputs TABLE_OF_CONTENTS.txt
""'

## Repository layout
""'text
├── main.tex                  # Book entry point (Intro, Prologue, 50 chapters)
├── preamble.tex              # Packages, macros, layout commands
├── intro.tex, prologue.tex   # Front matter
├── utils/                    # Build and analysis utilities
│   ├── compile_realtime.py
│   ├── generate_chapter_subset.py
│   ├── analyze_chapters.py
│   └── generate_page_table.py
├── generate_toc.py           # Plain-text TOC generator
├── 01_BanachTarskiParadox/
├── 02_TopologicalInsulators/
├── ...
└── 50_Consciousness/
""'

## Troubleshooting
- Activate your virtual environment first: 'source venv/bin/activate'
- If LaTeX fails, inspect 'compile_pass1.log', 'compile_pass2.log', and 'main.log'
- Ensure 'lualatex' is on your PATH (TeX Live installed)

## License
Original content © David H. Silver. All rights reserved. 