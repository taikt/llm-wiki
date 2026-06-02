#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# llm-wiki — Install skill vào project hiện tại
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/taikt/llm-wiki/main/install.sh)
# ──────────────────────────────────────────────────────────────
set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com/taikt/llm-wiki/main"
TARGET=".github/skills/llm-wiki"

cd "$(pwd)"

echo "📦 Installing llm-wiki skill into $TARGET …"

mkdir -p "$TARGET/scripts"

# Download SKILL.md + config.yaml
for file in SKILL.md config.yaml; do
  url="$REPO_RAW/.github/skills/llm-wiki/$file"
  echo "   ⬇️  $file"
  curl -fsSL "$url" -o "$TARGET/$file"
done

# Download scripts
for file in convert.py notes_export.py; do
  url="$REPO_RAW/.github/skills/llm-wiki/scripts/$file"
  echo "   ⬇️  scripts/$file"
  curl -fsSL "$url" -o "$TARGET/scripts/$file"
done

chmod +x "$TARGET/scripts/"*.py

echo ""
echo "✅  Installation complete!"
echo ""
echo "📝  Next step: open the config file and set your wiki root path:"
echo "    $TARGET/config.yaml"
echo ""
echo "💡  Then use Copilot Chat with commands like:"
echo "    • \"ingest file.pdf\"         — add documents to your wiki"
echo "    • \"what does the wiki say about…\" — query the wiki"
echo "    • \"lint wiki\"              — check wiki quality"
echo ""
