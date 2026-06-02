#!/usr/bin/env python3
"""
llm-wiki Notes Exporter — dump Apple Notes → .txt files into raw/ of wiki project.

Usage:
    # Export entire Notes folder
    python notes_export.py --root /path/to/wiki-root --folder "My Notes"

    # Export single note
    python notes_export.py --root /path/to/wiki-root --folder "My Notes" --note "AI news"

    # List folders and notes (no export)
    python notes_export.py --list

Output:
    Files saved to <root>/raw/notes/<folder-name>/<note-title>.txt
    Prints list of created files.

Requires: macOS + Apple Notes app. No additional dependencies (uses built-in osascript).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


# ── AppleScript helpers ───────────────────────────────────────────────────────

def run_applescript(script: str) -> str:
    """Run AppleScript via osascript, return stdout."""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        print(f"[ERROR] AppleScript failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def list_folders() -> list[str]:
    """List all folder names in Apple Notes."""
    script = """
    tell application "Notes"
        set folderNames to name of folders
        return folderNames
    end tell
    """
    raw = run_applescript(script)
    return [f.strip() for f in raw.split(",") if f.strip()]


def list_notes_in_folder(folder_name: str) -> list[str]:
    """List all note titles in a specific folder."""
    # Escape quotes for AppleScript
    safe_name = folder_name.replace('"', '\\"')
    script = f"""
    tell application "Notes"
        set folderRef to folder "{safe_name}"
        set noteTitles to name of notes of folderRef
        return noteTitles
    end tell
    """
    raw = run_applescript(script)
    return [n.strip() for n in raw.split(",") if n.strip()]


def export_note(folder_name: str, note_title: str) -> str:
    """Export a single note's body as plain text."""
    safe_folder = folder_name.replace('"', '\\"')
    safe_title = note_title.replace('"', '\\"')
    script = f"""
    tell application "Notes"
        set folderRef to folder "{safe_folder}"
        set noteRef to first note of folderRef whose name = "{safe_title}"
        set noteBody to body of noteRef
        return noteBody
    end tell
    """
    raw = run_applescript(script)

    # AppleScript returns HTML — strip tags for plain text
    # Also handle <br>, <div>, <p> → newline
    text = raw
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</?(div|p|li|h[1-6])[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)  # strip remaining tags
    text = re.sub(r"\n{3,}", "\n\n", text)  # collapse excessive blank lines
    return text.strip()


def slugify(text: str) -> str:
    """Convert text to filesystem-safe slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export Apple Notes to llm-wiki raw folder."
    )
    parser.add_argument("--root", type=Path, help="Wiki root path")
    parser.add_argument("--folder", help="Notes folder name")
    parser.add_argument("--note", help="Specific note title (optional)")
    parser.add_argument(
        "--list", action="store_true", help="List folders/notes without exporting"
    )
    args = parser.parse_args()

    if args.list:
        print("📁 Folders in Apple Notes:")
        for folder in list_folders():
            print(f"  • {folder}")
            notes = list_notes_in_folder(folder)
            if notes:
                for note in notes:
                    print(f"      - {note}")
        return

    if not args.root or not args.folder:
        parser.print_help()
        sys.exit(1)

    root = args.root.expanduser().resolve()
    folder_name = args.folder

    # Resolve target directory
    folder_slug = slugify(folder_name)
    target_dir = root / "raw" / "notes" / folder_slug
    target_dir.mkdir(parents=True, exist_ok=True)

    if args.note:
        # Export single note
        note_title = args.note
        body = export_note(folder_name, note_title)
        note_slug = slugify(note_title)
        out_path = target_dir / f"{note_slug}.txt"
        out_path.write_text(body, encoding="utf-8")
        print(f"  ✓ {out_path.relative_to(root)}")
    else:
        # Export entire folder
        notes = list_notes_in_folder(folder_name)
        if not notes:
            print(f"[INFO] No notes found in folder '{folder_name}'", file=sys.stderr)
            return
        for note_title in notes:
            body = export_note(folder_name, note_title)
            note_slug = slugify(note_title)
            out_path = target_dir / f"{note_slug}.txt"
            out_path.write_text(body, encoding="utf-8")
            print(f"  ✓ {out_path.relative_to(root)}")

    print(f"\n📝 Exported to: {target_dir}")


if __name__ == "__main__":
    main()
