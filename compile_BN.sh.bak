#!/bin/bash
# Compile script for Barnes & Noble print files

echo "Compiling Barnes & Noble print files..."

# Compile interior (without cover)
echo "Compiling interior PDF..."
pdflatex -interaction=nonstopmode main_interior_BN.tex
pdflatex -interaction=nonstopmode main_interior_BN.tex  # Run twice for TOC

# Compile cover
echo "Compiling wraparound cover PDF..."
cd cover
xelatex -interaction=nonstopmode cover_refined.tex
cd ..

echo "Done!"
echo ""
echo "Files ready for Barnes & Noble:"
echo "1. Interior: main_interior_BN.pdf"
echo "2. Cover: cover/cover_refined.pdf"
echo ""
echo "Book specifications:"
echo "- Trim size: 7\" x 10\""
echo "- Spine width: 1.29\" (for ~515 pages)"
echo "- Total cover width: 15.54\" x 10.25\" (includes bleeds)"
echo ""
echo "Upload these files separately to Barnes & Noble Press."
