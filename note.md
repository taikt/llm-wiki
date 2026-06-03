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

## 🤔 How GitHub skill "management" actually works

### There is no skill registry

GitHub has **no special mechanism** for skills. It's purely **convention-based** — `gh skill install` does not register or publish anything. Here's what actually happens:

### How `gh skill install owner/repo name` works

```
gh skill install taikt/llm-wiki llm-wiki
```

This command simply:

1. **Clones/fetches** the repo `taikt/llm-wiki` from GitHub (read-only, no auth needed for public repos)
2. **Looks for** the folder `skills/llm-wiki/` inside the repo
3. **Copies** all files from `skills/llm-wiki/` into `<target>/llm-wiki/` in the **user's local project**

**Where is `<target>`?** It depends on the `gh` CLI version:

| `gh` version | Target directory | Notes |
|---|---|---|
| `< 2.90` | `.github/skills/` | Legacy location |
| `≥ 2.90` | `.agents/` | **New default** — GitHub moved to `.agents/` |

VS Code Copilot actually scans **both** directories, so skills work from either location.

> 💡 **Pro tip:** If you want to keep your skills in `.github/skills/`, use the `install.sh` script instead:
> `bash <(curl -fsSL https://raw.githubusercontent.com/taikt/llm-wiki/main/install.sh)`
>
> The script installs to `.github/skills/` and also creates a symlink under `.agents/` → `.github/skills/`
> so Copilot sees it from both paths.

That's it. No API registration, no database entry, no "publishing" step.
The `gh skill update` command does the same thing — re-download and overwrite.

### GitHub does NOT know this is a skill

Compare with other convention-based systems:

| Technology | How GitHub recognizes it | Special mechanism? |
|---|---|---|
| npm package | `package.json` at root | ✅ npm registry + `npm publish` |
| Docker image | `Dockerfile` at root | ✅ Docker Hub / GitHub Container Registry |
| GitHub Action | `.github/actions/` or `action.yml` | ✅ GitHub Actions marketplace |
| **Copilot Skill** | `skills/<name>/SKILL.md` | ❌ **No registry, no publish command** |

A Copilot Skill is the **simplest** of all — just files in a folder, zero infrastructure.

### How VS Code Copilot discovers skills

When you open a project in VS Code:

1. Copilot scans **both** `.github/skills/` and `.agents/` in the workspace
2. For each subfolder that contains `SKILL.md` (or agent config), it reads the instructions
3. Those instructions become part of the AI context when you chat

That's all. No config file, no extension, no restart needed.

> ⚠️ **`gh` CLI ≥ 2.90** installs skills into `.agents/` instead of `.github/skills/`.
> The `install.sh` script in this repo installs to `.github/skills/` and creates a symlink
> at `.agents/llm-wiki` → `.github/skills/llm-wiki` so both paths are covered.

### Multiple skills in one repo

You can have as many skills as you want in a single repo:

```
your-repo/
├── skills/
│   ├── llm-wiki/SKILL.md
│   ├── llm-todo/SKILL.md
│   └── llm-journal/SKILL.md
├── shared-scripts/    ← shared code (not in any skill folder)
└── README.md
```

Users install a specific one by name:

```bash
gh skill install your-name/your-repo llm-wiki
gh skill install your-name/your-repo llm-todo
```

Each installs to its own subfolder: `.github/skills/llm-wiki/`, `.github/skills/llm-todo/`, etc.

### When to use one repo vs multiple repos

| Scenario | Recommendation |
|---|---|
| Skills share common scripts/utils | ✅ **One repo** — avoid duplication |
| Skills are a "personal toolkit" | ✅ **One repo** — easy to maintain |
| Publishing to community separately | ✅ **Separate repos** — independent versioning |
| Each skill has different authors | ✅ **Separate repos** — independent access control |

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


