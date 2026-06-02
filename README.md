# 📚 LLM Wiki — Agent Skill

> Maintain a personal LLM-powered wiki directly from VS Code Copilot Chat.

## ✨ Features

- **Ingest** documents (PDF, DOCX, XLSX, PPTX, images, text) → auto-generate wiki pages
- **Query** — ask Copilot, it answers from your wiki
- **Create pages** — "note that…", "write about…"
- **Lint/Audit** — check wiki quality (orphan pages, contradictions, missing entries)
- **Apple Notes sync** — auto-export notes into your wiki (macOS)

## 🚀 Installation

### Prerequisites
- VS Code + GitHub Copilot Chat
- GitHub CLI ≥ 2.90 (`gh --version`)
- Python 3.8+ (for document conversion)

### Option 1 — `gh skill install` (recommended)

```bash
cd /path/to/your-project
gh skill install taikt/llm-wiki llm-wiki
```

Then edit `.github/skills/llm-wiki/config.yaml` and set your wiki root path.

> `gh skill` handles versioning, updates, and provenance automatically. See `gh skill --help`.

### Option 2 — Manual download (no gh CLI needed)

```bash
cd /path/to/your-project
bash <(curl -fsSL https://raw.githubusercontent.com/taikt/llm-wiki/main/install.sh)
```

## ⚙️ Configuration

Open `.github/skills/llm-wiki/config.yaml` and set the `root` path to your wiki directory:

```yaml
projects:
  - name: default
    root: /path/to/your/wiki    # ← change this
```

## 💬 Usage

Open Copilot Chat and try:

| You say | Copilot does |
|---------|-------------|
| `ingest report.pdf` | Reads file from `raw/`, creates wiki pages |
| `what does the wiki say about machine learning?` | Searches and answers |
| `write a page about Python basics` | Creates a new page |
| `lint wiki` | Checks wiki quality |
| `sync from Apple Notes` | Exports notes from Apple Notes |

## 🗂️ Wiki folder structure

```
<root>/
├── raw/                 # Source documents (immutable)
├── .llm-wiki/cached/    # Converted file cache
└── wiki/                # Wiki pages (= Obsidian vault)
    ├── index.md         # Table of contents
    └── log.md           # Change history
```

## 📝 License

MIT
