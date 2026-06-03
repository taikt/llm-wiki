# llm-wiki — Developer Guide

## 📁 Repo structure

```
taikt/llm-wiki/
├── skills/llm-wiki/     ← skill content (single source of truth!)
│   ├── SKILL.md         ← main skill instructions (Copilot reads this)
│   ├── config.yaml      ← default config template
│   └── scripts/         ← helper scripts (convert.py, notes_export.py)
├── install.sh           ← one-liner installer (bash <(curl ...))
├── commit.sh            ← helper to commit & push
└── README.md            ← user-facing docs
```

> **Single-source principle:** `skills/llm-wiki/` is the **only** folder with skill files. Both `gh skill install` and `install.sh` read from this same folder — no duplication.

---

## 🛠 How to create a skill from scratch

1. **Create a GitHub repo** (e.g., `your-name/your-skill`)
2. **Add the skill folder** at the repo root:
   ```
   your-skill/
   └── skills/<skill-name>/
       ├── SKILL.md            ← required: the AI instructions
       ├── config.yaml         ← optional: user config
       └── scripts/            ← optional: helper scripts
   ```
3. **Write `SKILL.md`** with the skill's instructions (see [AgentSkills.io spec](https://agentskills.io/specification))
4. **Write `install.sh`** to download the skill folder into the user's project (see `llm-wiki/install.sh` as a template)
5. **Write `README.md`** with install & usage instructions

---

## 🚀 How to publish / update

### First-time publish

```bash
cd /path/to/your-skill-repo

# 1. Authenticate gh CLI (only once)
gh auth login

# 2. Create repo on GitHub first (github.com/new), then:
git remote add origin https://github.com/your-name/your-skill.git
git push -u origin main

# ✅ Done — skill is live! No "publish" command needed.
# Users can now install via:
#   gh skill install your-name/your-skill <skill-name>
```

The skill is **automatically published** once pushed to a public GitHub repo. There is no `gh skill publish` command — `gh skill install owner/repo name` reads the skill directly from the repo.

### Subsequent updates

```bash
cd /path/to/your-skill-repo

# Review changes
git diff

# Stage & commit
git add -A
git commit -m "Description of changes"

# Push
git push

# (Recommended) Create a release tag so gh skill can track versions
git tag v1.5
git push origin v1.5
# Then go to github.com/your-name/your-skill → "Create a new release" from that tag
```

After pushing, users update via `gh skill update` or re-run `install.sh`.

---

## 📥 How users install / update

### Option A — `gh skill install` (requires gh CLI ≥ 2.90)

```bash
# First, authenticate (one-time)
gh auth login

cd /path/to/their-project

# Install
gh skill install taikt/llm-wiki llm-wiki

# Later, update
gh skill update taikt/llm-wiki llm-wiki
```

Pros: version tracking, provenance, auto-updates.
Cons: requires `gh` CLI (not included with VS Code — install separately).

### Option B — `bash <(curl ...)` (no gh CLI needed)

```bash
cd /path/to/their-project
bash <(curl -fsSL https://raw.githubusercontent.com/taikt/llm-wiki/main/install.sh)
```

**How it works:** `curl` downloads `install.sh` from GitHub raw → pipes it to `bash` directly (no file saved, no clone needed). The script then downloads all skill files into `.github/skills/llm-wiki/`.

Pros: one line, no extra tools, no git needed.
Cons: re-run to update (re-downloads everything).

**For non-tech users:** Option B is recommended — only need terminal + `curl` (built-in on macOS/Linux, available on Windows 10+).

### ⚠️ Important note about `gh` CLI

`gh` does **NOT** come with VS Code. VS Code only includes:
- The editor itself
- Git (bundled or auto-detected)
- GitHub Copilot extension (if installed)

To install `gh`:
- macOS: `brew install gh`
- Windows: `winget install --id GitHub.cli`
- Linux: `sudo apt install gh`

---

## 🧪 Testing before publishing

1. Manually create `.github/skills/llm-wiki/` in any test project
2. Copy your skill files into it (SKILL.md, config.yaml, scripts/)
3. Test directly in Copilot Chat — it will read the skill from the local path
4. Iterate until it works, then commit & push

