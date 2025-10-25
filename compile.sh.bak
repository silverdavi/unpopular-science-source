#!/bin/bash

# LaTeX Compilation Script with Timing
# Compiles main.tex with detailed timing measurements

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  LaTeX Compilation Script${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

print_step() {
    echo -e "${YELLOW}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

format_time() {
    local duration=$1
    if (( $(echo "$duration < 60" | bc -l) )); then
        printf "%.2f seconds" "$duration"
    else
        local minutes=$(echo "$duration / 60" | bc -l)
        printf "%.1f minutes (%.2f seconds)" "$minutes" "$duration"
    fi
}

# Start timing
SCRIPT_START=$(date +%s.%N)

print_header

# Check if main.tex exists
if [ ! -f "main.tex" ]; then
    print_error "main.tex not found in current directory"
    exit 1
fi

# Clean previous build artifacts
print_step "Cleaning previous build artifacts..."
CLEAN_START=$(date +%s.%N)
rm -f *.aux *.log *.out *.toc *.lot *.lof *.synctex.gz *.fls *.fdb_latexmk *.idx *.ilg *.ind main.pdf
CLEAN_END=$(date +%s.%N)
CLEAN_TIME=$(echo "$CLEAN_END - $CLEAN_START" | bc -l)
print_success "Cleanup completed in $(format_time $CLEAN_TIME)"
echo ""

# First compilation pass
print_step "First LuaLaTeX compilation pass..."
FIRST_START=$(date +%s.%N)
if lualatex --interaction=nonstopmode main.tex > compile_pass1.log 2>&1; then
    FIRST_END=$(date +%s.%N)
    FIRST_TIME=$(echo "$FIRST_END - $FIRST_START" | bc -l)
    print_success "First pass completed in $(format_time $FIRST_TIME)"
else
    FIRST_END=$(date +%s.%N)
    FIRST_TIME=$(echo "$FIRST_END - $FIRST_START" | bc -l)
    print_error "First pass failed after $(format_time $FIRST_TIME)"
    echo "Check compile_pass1.log for details"
    exit 1
fi

# Check if PDF was generated
if [ ! -f "main.pdf" ]; then
    print_error "PDF was not generated after first pass"
    exit 1
fi

# Get first pass statistics
FIRST_PAGES=$(grep "Output written" main.log | tail -1 | grep -o '[0-9]\+ pages' | grep -o '[0-9]\+' || echo "0")
FIRST_SIZE=$(ls -lh main.pdf | awk '{print $5}' 2>/dev/null || echo "0")

echo "  - Pages generated: $FIRST_PAGES"
echo "  - PDF size: $FIRST_SIZE"
echo ""

# Second compilation pass (for cross-references)
print_step "Second LuaLaTeX compilation pass (for cross-references)..."
SECOND_START=$(date +%s.%N)
if lualatex --interaction=nonstopmode main.tex > compile_pass2.log 2>&1; then
    SECOND_END=$(date +%s.%N)
    SECOND_TIME=$(echo "$SECOND_END - $SECOND_START" | bc -l)
    print_success "Second pass completed in $(format_time $SECOND_TIME)"
else
    SECOND_END=$(date +%s.%N)
    SECOND_TIME=$(echo "$SECOND_END - $SECOND_START" | bc -l)
    print_error "Second pass failed after $(format_time $SECOND_TIME)"
    echo "Check compile_pass2.log for details"
    # Don't exit - first pass PDF might still be usable
fi

# Get final statistics
if [ -f "main.pdf" ]; then
    FINAL_PAGES=$(grep "Output written" main.log | tail -1 | grep -o '[0-9]\+ pages' | grep -o '[0-9]\+' || echo "0")
    FINAL_SIZE=$(ls -lh main.pdf | awk '{print $5}' 2>/dev/null || echo "0")
    FINAL_BYTES=$(stat -f%z main.pdf 2>/dev/null || stat -c%s main.pdf 2>/dev/null || echo "0")
    
    # Calculate MB
    FINAL_MB=$(echo "scale=2; $FINAL_BYTES / 1048576" | bc -l)
fi

# Calculate total compilation time
SCRIPT_END=$(date +%s.%N)
TOTAL_TIME=$(echo "$SCRIPT_END - $SCRIPT_START" | bc -l)
COMPILE_TIME=$(echo "$FIRST_TIME + $SECOND_TIME" | bc -l)

# Summary
echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  Compilation Summary${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

printf "%-25s %s\n" "Cleanup time:" "$(format_time $CLEAN_TIME)"
printf "%-25s %s\n" "First pass time:" "$(format_time $FIRST_TIME)"
printf "%-25s %s\n" "Second pass time:" "$(format_time $SECOND_TIME)"
printf "%-25s %s\n" "Total compile time:" "$(format_time $COMPILE_TIME)"
printf "%-25s %s\n" "Total script time:" "$(format_time $TOTAL_TIME)"
echo ""

if [ -f "main.pdf" ]; then
    printf "%-25s %s\n" "Final page count:" "$FINAL_PAGES pages"
    printf "%-25s %s\n" "Final PDF size:" "$FINAL_SIZE (${FINAL_MB} MB)"
    printf "%-25s %.2f\n" "Pages per second:" "$(echo "scale=2; $FINAL_PAGES / $COMPILE_TIME" | bc -l)"
    printf "%-25s %.2f\n" "MB per second:" "$(echo "scale=2; $FINAL_MB / $COMPILE_TIME" | bc -l)"
    echo ""
    print_success "PDF compilation completed successfully!"
    echo "Output file: main.pdf"
else
    print_error "PDF compilation failed!"
fi

# Show any warnings
WARNINGS=$(grep -i "warning\|error" main.log | wc -l | tr -d ' ')
if [ "$WARNINGS" -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}Found $WARNINGS warnings/errors in main.log${NC}"
    echo "Use 'grep -i \"warning\\|error\" main.log' to see details"
fi

echo ""
echo -e "${BLUE}Compilation logs saved:${NC}"
echo "  - compile_pass1.log (first pass)"
echo "  - compile_pass2.log (second pass)"  
echo "  - main.log (latest compilation)"
echo "" 