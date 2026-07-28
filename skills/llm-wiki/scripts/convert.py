#!/usr/bin/env python3
"""
llm-wiki document converter — convert PDF/DOCX/XLSX/PPTX/... → Markdown text.

Usage:
    python convert.py <file_path> [--tool markitdown|docling] [--venv <path>] [--auto-install]

Output: prints Markdown text to stdout.
Exit 0 on success, 1 on error.

Tools (priority):
  markitdown  — Microsoft MarkItDown, lightweight, no ML models (default)
                pip install 'markitdown[all]'
  docling     — IBM Docling, ML-based, better for scanned PDFs
                pip install docling

Options:
  --venv <path>    Path to a Python virtual environment. Its pip will be used
                   when --auto-install is set.
  --auto-install   Automatically install the required tool via pip if missing.

If neither is installed (and --auto-install is not set), falls back to basic
text extraction using stdlib.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _venv_python(venv: str) -> Path | None:
    """Return the python executable inside *venv*, if it exists."""
    venv_path = Path(venv).expanduser().resolve()
    for candidate in (
        venv_path / "bin" / "python",        # POSIX
        venv_path / "Scripts" / "python.exe",  # Windows
    ):
        if candidate.exists():
            return candidate
    return None


def _reexec_under_venv_if_needed(venv: str | None) -> None:
    """If --venv is given, re-exec this script with the venv's python so
    installed packages are importable. Without this, --auto-install would
    install into <venv> but the currently running (e.g. system) interpreter
    could never import it, silently falling back to the basic-text fallback
    every time.

    Note: we deliberately do NOT compare resolved/realpath executables to
    decide whether to skip re-exec. Many venvs (esp. those created with
    `python -m venv --symlinks`, the default on Linux) have bin/python as a
    symlink that resolves all the way to the system python binary (e.g.
    /usr/bin/python3.12) — venv activation works via pyvenv.cfg discovery
    based on the *unresolved* executable path, not the realpath. Comparing
    realpaths would make the venv interpreter look identical to the system
    one and incorrectly skip the re-exec, defeating the whole purpose. The
    _LLM_WIKI_CONVERT_REEXECED env guard prevents infinite re-exec loops.
    """
    if not venv or os.environ.get("_LLM_WIKI_CONVERT_REEXECED") == "1":
        return
    target = _venv_python(venv)
    if target is None:
        return
    env = dict(os.environ)
    env["_LLM_WIKI_CONVERT_REEXECED"] = "1"
    os.execve(str(target), [str(target), __file__] + sys.argv[1:], env)

# ── Supported extensions per tool ────────────────────────────────────────────

MARKITDOWN_EXTS = frozenset({
    ".pdf", ".docx", ".doc", ".pptx", ".ppt",
    ".xlsx", ".xls",
    ".html", ".htm", ".csv", ".json", ".xml",
    ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp",
    ".wav", ".mp3", ".epub", ".zip",
})

DOCLING_EXTS = frozenset({
    ".pdf", ".docx", ".pptx", ".xlsx",
    ".html", ".htm",
    ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp",
})

TEXT_EXTS = frozenset({
    ".txt", ".md", ".rst", ".log", ".csv", ".json", ".yaml", ".yml",
    ".toml", ".ini", ".cfg", ".html", ".htm", ".xml",
})

# ── Auto-installer ────────────────────────────────────────────────────────────

_TOOL_PACKAGES: dict[str, str] = {
    "markitdown": "markitdown[all]",
    "docling": "docling",
}


def _pip_for_venv(venv: str | None) -> list[str]:
    """Return the pip command for the given venv (or the current interpreter)."""
    if venv:
        venv_path = Path(venv).expanduser().resolve()
        # Windows layout: Scripts/pip.exe  |  POSIX layout: bin/pip
        for candidate in (
            venv_path / "Scripts" / "pip.exe",
            venv_path / "bin" / "pip",
        ):
            if candidate.exists():
                return [str(candidate)]
        # Fallback: use the venv Python with -m pip
        for py_candidate in (
            venv_path / "Scripts" / "python.exe",
            venv_path / "bin" / "python",
        ):
            if py_candidate.exists():
                return [str(py_candidate), "-m", "pip"]
    return [sys.executable, "-m", "pip"]


def _auto_install(tool: str, venv: str | None) -> bool:
    """Install *tool* via pip. Returns True if the install succeeded."""
    package = _TOOL_PACKAGES.get(tool)
    if not package:
        return False
    pip_cmd = _pip_for_venv(venv) + ["install", package]
    print(f"[INFO] Auto-installing {package} …", file=sys.stderr)
    result = subprocess.run(pip_cmd)
    if result.returncode == 0:
        print(f"[INFO] {package} installed successfully.", file=sys.stderr)
        return True
    print(f"[ERROR] Failed to install {package} (exit {result.returncode}).", file=sys.stderr)
    return False



def _try_markitdown(path: Path) -> str:
    from markitdown import MarkItDown  # type: ignore[import]
    md = MarkItDown(enable_plugins=False)
    result = md.convert_local(str(path))
    return result.text_content or ""


def _try_docling(path: Path) -> str:
    from docling.document_converter import DocumentConverter  # type: ignore[import]
    converter = DocumentConverter()
    result = converter.convert(str(path))
    return result.document.export_to_markdown()


def _try_basic(path: Path) -> str:
    """Fallback: read text directly if it's a text-based file."""
    if path.suffix.lower() in TEXT_EXTS:
        return path.read_text(encoding="utf-8", errors="replace")
    return f"[Cannot convert {path.name}: install markitdown or docling]\n" \
           f"  pip install 'markitdown[all]'  (lightweight, no ML)\n" \
           f"  pip install docling             (better for scanned PDFs)"


# ── Main ─────────────────────────────────────────────────────────────────────

def convert(path: Path, tool: str | None = None, venv: str | None = None, auto_install: bool = False) -> str:
    """Convert file → Markdown text.

    Args:
        path:         File to convert.
        tool:         Force a specific tool ("markitdown" | "docling" | None = auto).
        venv:         Path to a Python venv whose pip to use for auto-install.
        auto_install: If True, attempt to pip-install a missing tool automatically.
    """
    ext = path.suffix.lower()

    tools_to_try: list[tuple[str, frozenset[str]]] = []

    if tool == "docling":
        tools_to_try = [("docling", DOCLING_EXTS), ("markitdown", MARKITDOWN_EXTS)]
    elif tool == "markitdown":
        tools_to_try = [("markitdown", MARKITDOWN_EXTS)]
    else:
        # Auto: try markitdown first (lighter), fallback docling
        tools_to_try = [("markitdown", MARKITDOWN_EXTS), ("docling", DOCLING_EXTS)]

    for tool_name, capable_exts in tools_to_try:
        if ext not in capable_exts:
            continue
        for attempt in range(2):  # attempt 0 = normal, attempt 1 = after auto-install
            try:
                if tool_name == "markitdown":
                    return _try_markitdown(path)
                elif tool_name == "docling":
                    return _try_docling(path)
            except ImportError:
                if attempt == 0 and auto_install:
                    if not _auto_install(tool_name, venv):
                        break  # install failed, try next tool
                    # Invalidate cached import so the retry actually picks up the new package
                    for mod in list(sys.modules.keys()):
                        if mod.startswith(tool_name.replace("-", "_")):
                            del sys.modules[mod]
                    continue  # retry import after install
                break  # no auto-install, move to next tool
            except Exception as e:
                print(f"[WARN] {tool_name} failed: {e}", file=sys.stderr)
                break  # non-import error, try next tool

    return _try_basic(path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert document to Markdown text for llm-wiki ingest."
    )
    parser.add_argument("file", type=Path, help="Path to file to convert")
    parser.add_argument(
        "--tool",
        choices=["markitdown", "docling"],
        default=None,
        help="Force specific tool (default: auto, markitdown first)",
    )
    parser.add_argument(
        "--venv",
        default=None,
        metavar="PATH",
        help="Path to Python virtual environment whose pip to use for auto-install",
    )
    parser.add_argument(
        "--auto-install",
        action="store_true",
        default=False,
        help="Automatically pip-install the required converter if it is missing",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="PATH",
        help=(
            "Write Markdown output to this file instead of stdout. "
            "If the file already exists it will be overwritten. "
            "Prints the resolved output path to stdout on success."
        ),
    )
    args = parser.parse_args()

    # Re-exec under the venv's own python (if --venv was given) BEFORE doing
    # any work, so --auto-install'd packages are guaranteed importable in
    # this same process. See _reexec_under_venv_if_needed for rationale.
    _reexec_under_venv_if_needed(args.venv)

    if not args.file.exists():
        print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    result = convert(
        path=args.file,
        tool=args.tool,
        venv=args.venv,
        auto_install=args.auto_install,
    )

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result, encoding="utf-8")
        # Print the resolved output path for the agent to capture
        print(out_path.resolve())
    else:
        print(result)


if __name__ == "__main__":
    main()
