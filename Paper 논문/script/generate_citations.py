#!/usr/bin/env python3
"""
generate_citations.py — Regenerate citation files from paper YAML front-matter.

This script reads the YAML front-matter of every `0X_SSRN-XXXXXXX_*.md` file in
the parent papers/ directory and emits citations in one or more formats:

    bibtex   — BibTeX format (.bib)
    ris      — Research Information Systems format (.ris)
    apa      — APA 7th edition plain text
    mla      — MLA 9th edition plain text
    chicago  — Chicago Author-Date plain text
    csl-json — Citation Style Language JSON (for Zotero/Pandoc)
    all      — emit all formats

USAGE
    python scripts/generate_citations.py --format bibtex --out BIBLIOGRAPHY.bib
    python scripts/generate_citations.py --format all
    python scripts/generate_citations.py --format apa            # stdout
    python scripts/generate_citations.py --list                  # just list papers

DEPENDENCIES
    Python 3.10+ standard library only (no third-party packages).

This script reads YAML manually with a minimal parser. The expected YAML
front-matter schema is documented in README.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Minimal YAML front-matter parser
# ---------------------------------------------------------------------------

YAML_FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def _parse_scalar(value: str) -> Any:
    """Parse a YAML scalar (string, int, bool, null)."""
    v = value.strip()
    if not v:
        return ""
    # Strip matching quotes
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    # Bool / null
    low = v.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "~", ""):
        return None
    # Int
    try:
        return int(v)
    except ValueError:
        pass
    return v


def _parse_block(lines: list[str], indent: int) -> tuple[Any, int]:
    """
    Parse a YAML block starting at `lines[0]` with given base `indent`.
    Returns (value, lines_consumed).
    """
    if not lines:
        return None, 0

    result: dict[str, Any] | list[Any] | None = None
    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.lstrip(" ")
        cur_indent = len(raw) - len(stripped)
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if cur_indent < indent:
            break

        # List item
        if stripped.startswith("- "):
            if cur_indent > indent:
                break
            if result is None:
                result = []
            if not isinstance(result, list):
                break
            item_content = stripped[2:]
            # Inline mapping like "- key: value"
            if ":" in item_content and not item_content.startswith('"'):
                key, _, val = item_content.partition(":")
                key = key.strip()
                val = val.strip()
                obj: dict[str, Any] = {}
                if val:
                    obj[key] = _parse_scalar(val)
                else:
                    obj[key] = None
                # Look ahead for more keys under this item
                j = i + 1
                while j < len(lines):
                    nxt = lines[j]
                    nxt_stripped = nxt.lstrip(" ")
                    nxt_indent = len(nxt) - len(nxt_stripped)
                    if not nxt_stripped or nxt_stripped.startswith("#"):
                        j += 1
                        continue
                    if nxt_indent <= cur_indent:
                        break
                    if nxt_stripped.startswith("- "):
                        break
                    k, _, v = nxt_stripped.partition(":")
                    k = k.strip()
                    v = v.strip()
                    if v:
                        obj[k] = _parse_scalar(v)
                    else:
                        # Nested list value
                        sub, consumed = _parse_block(lines[j + 1:], nxt_indent + 2)
                        obj[k] = sub
                        j += consumed
                    j += 1
                result.append(obj)
                i = j
                continue
            else:
                result.append(_parse_scalar(item_content))
                i += 1
                continue

        # Key: value mapping
        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            if result is None:
                result = {}
            if not isinstance(result, dict):
                break
            if val:
                # Inline value
                if val.startswith("[") and val.endswith("]"):
                    # Inline list: [a, b, c]
                    inner = val[1:-1].strip()
                    if not inner:
                        result[key] = []
                    else:
                        items = [_parse_scalar(p) for p in _split_inline_list(inner)]
                        result[key] = items
                else:
                    result[key] = _parse_scalar(val)
            else:
                # Block value follows
                sub, consumed = _parse_block(lines[i + 1:], cur_indent + 2)
                result[key] = sub
                i += consumed
            i += 1
            continue

        i += 1

    return result, i


def _split_inline_list(s: str) -> list[str]:
    """Split a comma-separated inline YAML list, respecting quoted strings."""
    parts: list[str] = []
    cur: list[str] = []
    in_quote: str | None = None
    for ch in s:
        if in_quote:
            cur.append(ch)
            if ch == in_quote:
                in_quote = None
        elif ch in ('"', "'"):
            in_quote = ch
            cur.append(ch)
        elif ch == ",":
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        parts.append("".join(cur).strip())
    return parts


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Extract and parse YAML front-matter from a Markdown file."""
    m = YAML_FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError("No YAML front-matter found at top of file")
    body = m.group(1)
    lines = body.split("\n")
    parsed, _ = _parse_block(lines, 0)
    return parsed or {}


# ---------------------------------------------------------------------------
# Citation generators
# ---------------------------------------------------------------------------

MONTH_ABBR = ["", "jan", "feb", "mar", "apr", "may", "jun",
              "jul", "aug", "sep", "oct", "nov", "dec"]
MONTH_FULL = ["", "January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]


def _author_key(meta: dict) -> str:
    """Compute a short BibTeX key from authors + year + short_title."""
    first = meta["authors"][0]["family"].lower()
    year = str(date.fromisoformat(meta["posted_date"]).year)
    short = meta.get("short_title", meta["title"][:24])
    slug = re.sub(r"[^a-z0-9]+", "_", short.lower()).strip("_")
    slug = slug.split("_")[0] if slug else "paper"
    return f"{first}{year}_{slug}"


def _format_authors_bibtex(authors: list[dict]) -> str:
    return " and ".join(f"{a['family']}, {a['given']}" for a in authors)


def _format_authors_inline(authors: list[dict]) -> str:
    """For APA/MLA/Chicago: 'Family, G.'"""
    parts = []
    for a in authors:
        given_initial = a["given"][0] if a.get("given") else ""
        parts.append(f"{a['family']}, {given_initial}.")
    return ", ".join(parts)


def fmt_bibtex(meta: dict) -> str:
    d = date.fromisoformat(meta["posted_date"])
    key = _author_key(meta)
    kws = meta.get("keywords", [])
    return f"""@misc{{{key},
  author    = {{{_format_authors_bibtex(meta["authors"])}}},
  title     = {{{{{meta["title"]}}}}},
  year      = {{{d.year}}},
  month     = {MONTH_ABBR[d.month]},
  day       = {{{d.day}}},
  publisher = {{{meta.get("publisher", "SSRN")}}},
  type      = {{SSRN Working Paper}},
  number    = {{{meta["ssrn_id"]}}},
  doi       = {{{meta["doi"]}}},
  url       = {{{meta["url"]}}},
  keywords  = {{{", ".join(kws)}}},
  note      = {{ORCID: {meta["authors"][0]["orcid"]}}}
}}
"""


def fmt_ris(meta: dict) -> str:
    d = date.fromisoformat(meta["posted_date"])
    out = [
        "TY  - GEN",
        f"T1  - {meta['title']}",
    ]
    for a in meta["authors"]:
        out.append(f"AU  - {a['family']}, {a['given']}")
    out += [
        f"PY  - {d.year}",
        f"DA  - {d.year}/{d.month:02d}/{d.day:02d}",
        f"PB  - {meta.get('publisher', 'SSRN')}",
        "M3  - SSRN Working Paper",
        f"SN  - {meta['ssrn_id']}",
        f"DO  - {meta['doi']}",
        f"UR  - {meta['url']}",
    ]
    for kw in meta.get("keywords", []):
        out.append(f"KW  - {kw}")
    out += [
        f"N1  - SSRN Working Paper No. {meta['ssrn_id']}; ORCID {meta['authors'][0]['orcid']}",
        f"LA  - {meta.get('language', 'en')}",
        "ER  -",
        "",
    ]
    return "\n".join(out)


def fmt_apa(meta: dict) -> str:
    d = date.fromisoformat(meta["posted_date"])
    a = meta["authors"][0]
    initial = a["given"][0] + "." if a.get("given") else ""
    return (
        f"{a['family']}, {initial} ({d.year}). "
        f"*{meta['title']}* "
        f"(SSRN Working Paper No. {meta['ssrn_id']}). "
        f"{meta.get('publisher', 'SSRN')}. "
        f"https://doi.org/{meta['doi']}"
    )


def fmt_mla(meta: dict) -> str:
    d = date.fromisoformat(meta["posted_date"])
    a = meta["authors"][0]
    return (
        f"{a['family']}, {a['given']}. "
        f"\"{meta['title']}.\" "
        f"*{meta.get('publisher', 'SSRN')}*, "
        f"{d.day} {MONTH_FULL[d.month]} {d.year}, "
        f"doi:{meta['doi']}."
    )


def fmt_chicago(meta: dict) -> str:
    d = date.fromisoformat(meta["posted_date"])
    a = meta["authors"][0]
    return (
        f"{a['family']}, {a['given']}. {d.year}. "
        f"\"{meta['title']}.\" "
        f"SSRN Working Paper No. {meta['ssrn_id']}. "
        f"https://doi.org/{meta['doi']}."
    )


def fmt_csl_json(metas: list[dict]) -> str:
    items = []
    for m in metas:
        d = date.fromisoformat(m["posted_date"])
        items.append({
            "id": _author_key(m),
            "type": "article",
            "title": m["title"],
            "author": [{"family": a["family"], "given": a["given"]} for a in m["authors"]],
            "issued": {"date-parts": [[d.year, d.month, d.day]]},
            "publisher": m.get("publisher", "SSRN"),
            "DOI": m["doi"],
            "URL": m["url"],
            "number": str(m["ssrn_id"]),
            "genre": "SSRN Working Paper",
            "keyword": ", ".join(m.get("keywords", [])),
            "language": m.get("language", "en"),
        })
    return json.dumps(items, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

FORMATS = ("bibtex", "ris", "apa", "mla", "chicago", "csl-json", "all")


def load_all_papers(papers_dir: Path) -> list[dict]:
    files = sorted(papers_dir.glob("0*_SSRN-*.md"))
    metas = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        try:
            meta = parse_frontmatter(text)
        except ValueError as e:
            print(f"[WARN] {f.name}: {e}", file=sys.stderr)
            continue
        meta["_file"] = f.name
        metas.append(meta)
    return metas


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate citation files from paper YAML.")
    parser.add_argument("--format", choices=FORMATS, default="all",
                        help="Output format (default: all)")
    parser.add_argument("--out", type=Path, default=None,
                        help="Output file (default: stdout for single format, BIBLIOGRAPHY.* for 'all')")
    parser.add_argument("--list", action="store_true", help="Just list papers found")
    parser.add_argument("--papers-dir", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="Path to papers directory (default: parent of this script)")
    args = parser.parse_args()

    metas = load_all_papers(args.papers_dir)
    if not metas:
        print("ERROR: No paper files matching 0X_SSRN-*.md found.", file=sys.stderr)
        return 1

    if args.list:
        print(f"Found {len(metas)} papers:")
        for m in metas:
            print(f"  [{m['ssrn_id']}] {m['short_title']:<28} ({m['posted_date']}, p.{m['pages']}) — {m['_file']}")
        return 0

    def emit(fmt: str) -> str:
        if fmt == "bibtex":
            return "".join(fmt_bibtex(m) + "\n" for m in metas)
        if fmt == "ris":
            return "".join(fmt_ris(m) for m in metas)
        if fmt == "apa":
            return "\n".join(fmt_apa(m) for m in metas) + "\n"
        if fmt == "mla":
            return "\n".join(fmt_mla(m) for m in metas) + "\n"
        if fmt == "chicago":
            return "\n".join(fmt_chicago(m) for m in metas) + "\n"
        if fmt == "csl-json":
            return fmt_csl_json(metas) + "\n"
        raise ValueError(fmt)

    if args.format == "all":
        out_dir = args.out if args.out else args.papers_dir
        for fmt, ext in [("bibtex", "bib"), ("ris", "ris"), ("apa", "apa.txt"),
                         ("mla", "mla.txt"), ("chicago", "chicago.txt"), ("csl-json", "csl.json")]:
            target = out_dir / f"BIBLIOGRAPHY.{ext}"
            target.write_text(emit(fmt), encoding="utf-8")
            print(f"Wrote {target}")
    else:
        content = emit(args.format)
        if args.out:
            args.out.write_text(content, encoding="utf-8")
            print(f"Wrote {args.out}")
        else:
            sys.stdout.write(content)

    return 0


if __name__ == "__main__":
    sys.exit(main())
