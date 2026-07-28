#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path
from datetime import date
import sys

def read_cached(path: Path) -> str:
    return path.read_text(encoding='utf-8')

def normalize(text: str) -> str:
    lines = text.splitlines()
    normalized = []
    i = 0
    while i < len(lines):
        m = re.match(r'^\s*(\d+(?:\.\d+)*)\.\s*$', lines[i])
        if m and i+1 < len(lines):
            j = i+1
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            if j < len(lines):
                normalized.append(f"{m.group(1)}. {lines[j].strip()}")
                i = j+1
                continue
        normalized.append(lines[i])
        i += 1
    return '\n'.join(normalized)

def split_top_level(text: str) -> dict[str,str]:
    # Find top-level headings like '1. Title'. Require the title to start with
    # an uppercase letter to avoid false positives from embedded numbered lists
    # such as retry sequences ("3. attempt 10 sec", "4. attempt 15 sec", ...)
    # which would otherwise be mistaken for real section headings and corrupt
    # the split (since they reuse small numbers like 1-10).
    top = list(re.finditer(r'^(\d+)\.\s+([A-Z].*)$', text, flags=re.M))
    result = {}
    for i, m in enumerate(top):
        num = m.group(1)
        if num in result:
            # keep the first (real) occurrence; later matches with the same
            # number are almost certainly noise.
            continue
        title = m.group(2).strip()
        start = m.end()
        end = top[i+1].start() if i+1 < len(top) else len(text)
        body = text[start:end].strip()
        result[num] = (title, body)
    return result

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s).strip('-')
    return s or 'section'

def write_pages(sections: dict[str,tuple[str,str]], cached: Path, wiki_root: Path) -> list[Path]:
    outdir = wiki_root / 'wiki'
    outdir.mkdir(parents=True, exist_ok=True)
    detailed_dir = outdir / '_detailed'
    detailed_dir.mkdir(parents=True, exist_ok=True)
    # Relocate (never delete) any stale top-level-looking pages from a previous
    # (possibly buggy) run before writing the corrected set, so old wrongly
    # named files don't linger in wiki/ root, e.g. "3-attempt-10-sec.md" when
    # the real title is "Requirements". They are moved into _detailed/ instead
    # of removed outright, since some may still hold real (if misfiled) content.
    new_names = {f"{num}-{slugify(title)}.md" for num, (title, _) in sections.items()}
    for stale in outdir.glob('*.md'):
        if stale.name in new_names:
            continue
        if re.match(r'^\d+-.+\.md$', stale.name):
            target = detailed_dir / stale.name
            if target.exists():
                stale.unlink()
            else:
                stale.rename(target)
    pages = []
    for num, (title, body) in sections.items():
        name = f"{num}-{slugify(title)}.md"
        path = outdir / name
        summary = (body.strip().split('\n')[0][:240] + '...') if body.strip() else ''
        content = f"# {title}\n\n**Summary**: {summary}\n\n**Sources**: raw/{cached.name.replace('.md','.pdf')}\n\n**Last updated**: {date.today().isoformat()}\n\n---\n\n{body}\n\n## Related pages\n\n-\n"
        path.write_text(content, encoding='utf-8')
        pages.append(path)
    return pages

def update_detailed_index(outdir: Path) -> list[Path]:
    """Regenerate _detailed_index.md by scanning wiki/_detailed/ directly,
    rather than tracking moved files, since ingest_cached.py writes there too."""
    detailed_dir = outdir / '_detailed'
    detailed_dir.mkdir(parents=True, exist_ok=True)
    detailed_pages = sorted(detailed_dir.glob('*.md'))
    det = outdir / '_detailed_index.md'
    lines = ['# Detailed Pages (archived)\n\n']
    for p in detailed_pages:
        lines.append(f"- [{p.stem}](_detailed/{p.name})\n")
    det.write_text(''.join(lines), encoding='utf-8')
    return detailed_pages

def update_index(outdir: Path, pages: list[Path]):
    idx = outdir / 'index.md'
    lines = ['# Wiki Index\n\n']
    for p in sorted(pages):
        lines.append(f"- [{p.stem}]({p.name})\n")
    idx.write_text(''.join(lines), encoding='utf-8')

def append_log(outdir: Path, cached: Path, pages: list[Path]):
    log = outdir / 'log.md'
    prev = log.read_text(encoding='utf-8') if log.exists() else ''
    entry = f"## {date.today().isoformat()} — Grouped ingest: {cached.name.replace('.md','.pdf')}\n"
    entry += "- Created: " + ', '.join(p.name for p in pages) + "\n"
    entry += "- Updated: index.md, log.md\n\n"
    log.write_text(prev + entry, encoding='utf-8')

def main():
    if len(sys.argv) < 3:
        print('Usage: ingest_grouped.py <cached_md> <wiki_root>')
        return
    cached = Path(sys.argv[1])
    wiki_root = Path(sys.argv[2])
    if not cached.exists():
        print('Cached file missing:', cached)
        return
    text = read_cached(cached)
    text = normalize(text)
    sections = split_top_level(text)
    outdir = wiki_root / 'wiki'
    pages = write_pages(sections, cached, wiki_root)
    update_index(outdir, pages)
    detailed_pages = update_detailed_index(outdir)
    append_log(outdir, cached, pages)
    print('Wrote', len(pages), 'grouped pages;', len(detailed_pages), 'detailed pages indexed')

if __name__ == '__main__':
    main()
