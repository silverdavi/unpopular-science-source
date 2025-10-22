# Multi-Chapter LaTeX Book Project

A comprehensive LaTeX book containing 53 chapters covering diverse topics in science, mathematics, technology, and philosophy.

## Project Structure

This project contains:
- **53 indexed chapter directories** (`01_BanachTarskiParadox` through `53_BodySwappingPuzzle`)
- **Main LaTeX file** (`main.tex`) with organized chapter includes
- **Utilities folder** (`utils/`) with Python scripts for project management
- **Cover graphics** and supporting materials

## Features

- **Multi-language support** with Hebrew, Sanskrit/Devanagari, and Latin scripts
- **Modern LaTeX compilation** using LuaLaTeX for advanced typography
- **Organized chapter structure** with summaries, technical sections, and image figures
- **Automated build scripts** for chapter management and path corrections

## Compilation

### Requirements
- TeX Live 2024 or later
- LuaLaTeX engine
- Required fonts: EzraSIL, CharisSIL, Noto Sans Devanagari

### Build Instructions

```bash
# Compile the main document
lualatex --interaction=nonstopmode main.tex

# For complete compilation with references
lualatex main.tex
lualatex main.tex  # Run twice for cross-references
```

## Chapter Management

### Enable/Disable Chapters
Chapters are controlled by `\def` statements at the beginning of `main.tex`:

```latex
\def\show01BanachTarskiParadox{}
\def\show07BilliardsConicsPorism{}
% Comment out or remove to disable chapters
```

### Python Utilities

The `utils/` directory contains helpful scripts:

- `parse_chapters.py` - Analyze chapter structure and generate CSV reports
- `reorganize_folders.py` - Rename folders with index prefixes  
- `update_show_variables.py` - Update variable names to match folder structure
- `fix_variables_no_underscore.py` - Remove problematic underscores from LaTeX variables
- `fix_image_paths.py` - Correct image paths to use indexed folder names

## Chapter Topics

The book covers diverse subjects including:

- **Mathematics**: Banach-Tarski Paradox, Bounded Prime Gaps, Arrow's Theorem
- **Physics**: Quantum Tunneling, Dark Matter, General Relativity vs QFT
- **Computer Science**: Zero-Knowledge Proofs, Speculative Execution Attacks
- **Chemistry**: Woodward-Hoffmann Rules, Photosynthesis
- **Philosophy**: Chinese Room Argument, Observer-Dependent Vacuum
- **History**: Christmas Truce of 1914, The Man in the Iron Mask
- **And many more...**

## File Organization

```
├── main.tex                    # Main LaTeX document
├── preamble.tex               # LaTeX preamble and packages
├── intro.tex, prologue.tex    # Introduction materials
├── cover/                     # Cover graphics
├── utils/                     # Python management scripts
├── 01_BanachTarskiParadox/    # Chapter directories
│   ├── main.tex              # Chapter content
│   ├── summary.tex           # Chapter summary  
│   ├── technical.tex         # Technical details
│   ├── imagefigure.tex       # Images and figures
│   └── ...                   # Additional chapter files
├── 02_TopologicalInsulators/
├── ...
└── 53_BodySwappingPuzzle/
```

## Contributing

When adding new chapters:
1. Create a new indexed directory (`##_ChapterName/`)
2. Add corresponding `\def\show##ChapterName{}` variable
3. Include chapter in main.tex with `\ifdefined` block
4. Update image paths to use indexed folder names

## License

This project contains original content and educational materials covering various scientific and mathematical topics.

## Build Status

- ✅ LaTeX compilation working
- ✅ Font dependencies resolved  
- ✅ Image paths corrected
- ✅ 53 chapters organized and indexed
- ✅ Python utilities functional 