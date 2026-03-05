#!/bin/bash
# Script to create GitHub Release v1.0.0
# Run this after authenticating with GitHub CLI

set -e

echo "🚀 Creating GitHub Release v1.0.0..."

# Check if gh is authenticated
if ! gh auth status &>/dev/null; then
    echo "❌ Not authenticated with GitHub CLI"
    echo "Please run: gh auth login"
    exit 1
fi

# Create the release
gh release create v1.0.0 \
    --title "LegalAI-Agent v1.0.0 - Initial Release" \
    --notes-file RELEASE_NOTES_v1.0.0.md \
    --generate-notes=false

echo "✅ Release v1.0.0 created successfully!"
echo "🔗 View release: https://github.com/ENDcodeworld/LegalAI-Agent/releases/tag/v1.0.0"
