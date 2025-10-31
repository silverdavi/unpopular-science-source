#!/bin/bash
#
# Publish main.pdf as a GitHub release (tagged "latest")
# This keeps the PDF accessible without committing it to the repo.
#
# Prerequisites:
#   brew install gh
#   gh auth login
#
# Usage:
#   ./release_pdf.sh

set -e

FILE="main.pdf"
REPO="silverdavi/unpopular-science-source"
TAG="latest"

# Check if PDF exists
if [ ! -f "$FILE" ]; then
  echo "Error: $FILE not found. Compile the book first:"
  echo "  python3 utils/compile_realtime.py main.tex"
  exit 1
fi

# Check if gh is installed
if ! command -v gh &> /dev/null; then
  echo "Error: GitHub CLI (gh) is not installed."
  echo "Install it with: brew install gh"
  exit 1
fi

echo "📦 Publishing $FILE as release '$TAG'..."

# Delete old release and tag if they exist
echo "🗑️  Removing old release (if exists)..."
gh release delete "$TAG" -R "$REPO" -y 2>/dev/null || true
git push origin --delete "$TAG" 2>/dev/null || true

# Create new release with the PDF
echo "🚀 Creating new release..."
gh release create "$TAG" "$FILE" \
  -R "$REPO" \
  --title "Unpopular Science - Latest Build" \
  --notes "Automatically updated on $(date '+%Y-%m-%d %H:%M:%S %Z')

Download the complete book PDF:
\`\`\`bash
curl -L -o UnpopularScience.pdf https://github.com/$REPO/releases/download/$TAG/$FILE
\`\`\`

Or visit: https://github.com/$REPO/releases/tag/$TAG"

echo ""
echo "✅ Success! Your PDF is now available at:"
echo "   https://github.com/$REPO/releases/download/$TAG/$FILE"
echo ""
echo "Direct download command:"
echo "   curl -L -o UnpopularScience.pdf https://github.com/$REPO/releases/download/$TAG/$FILE"

