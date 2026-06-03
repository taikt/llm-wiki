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

### Option 1 — `gh skill install`

```bash
cd /path/to/your-project
gh skill install taikt/llm-wiki llm-wiki 
or
gh skill install taikt/llm-wiki llm-wiki --dir .github\skills
```
or update
```bash
gh skill update taikt/llm-wiki llm-wiki
```

> ⚠️ **Note:** `gh` CLI ≥ 2.90 installs skills into `.agents/` (the new convention).
> VS Code Copilot scans **both** `.agents/` and `.github/skills/`, so skills work from either location.
> If you prefer the `.github/skills/` layout, use **Option 2** below.

Then edit config file and set your wiki root path.

### Option 2 — Manual download (no gh CLI needed, installs to `.github/skights/`)

```bash
cd /path/to/your-project
bash <(curl -fsSL https://raw.githubusercontent.com/taikt/llm-wiki/main/install.sh)
```

This installs to `.github/skills/llm-wiki/` (legacy location). If `.agents/` already exists in your
project, the script also creates a symlink `.agents/llm-wiki → ../.github/skills/llm-wiki/` so
Copilot can find the skill from either path.

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
