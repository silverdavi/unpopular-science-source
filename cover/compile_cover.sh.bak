#!/bin/bash
# Script to compile the book cover with barcode

echo "==> Compiling barcode..."
latex --interaction=nonstopmode barcode.tex
dvips -o barcode.ps barcode.dvi
ps2pdf barcode.ps barcode.pdf

echo "==> Compiling cover..."
lualatex --interaction=nonstopmode cover_refined.tex

echo "==> Cleaning up auxiliary files..."
rm -f barcode.aux barcode.dvi barcode.ps barcode.log
rm -f cover_refined.aux cover_refined.log

echo "==> Done! Output: cover_refined.pdf"

