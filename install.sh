#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# llm-wiki — Install skill vào project hiện tại
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/taikt/llm-wiki/main/install.sh)
# ──────────────────────────────────────────────────────────────
set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com/taikt/llm-wiki/main"
TARGET=".github/skills/llm-wiki"

cd "$(pwd)"

echo "📦 Cài đặt skill llm-wiki vào $TARGET …"

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
echo "✅  Cài đặt thành công!"
echo ""
echo "📝  Bước tiếp theo: Mở file sau và sửa đường dẫn wiki root của bạn:"
echo "    $TARGET/config.yaml"
echo ""
echo "💡  Sau đó dùng Copilot Chat với các lệnh như:"
echo "    • \"ingest file.pdf\"         — thêm tài liệu vào wiki"
echo "    • \"wiki có nội dung gì về…\" — tra cứu wiki"
echo "    • \"lint wiki\"              — kiểm tra wiki"
echo ""
