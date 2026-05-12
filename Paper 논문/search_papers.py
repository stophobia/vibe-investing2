#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
search_papers.py — Bilingual (Korean / English) full-text search across the
papers folder.

Why this exists
---------------
The four SSRN working papers in this collection are written and indexed in
two languages.  Off-the-shelf search engines that ship with text editors do
not handle Hangul syllable blocks well, and they tend to drop frontmatter
fields (DOI, JEL codes, keywords) that are critical for academic discovery.
This script gives the author and any reader a portable, dependency-free way
to find passages by topic, by JEL code, by author, or by DOI.

Design choices
--------------
* Pure Python standard library — no `pip install` required.
* Two-track tokenization:
  - Latin / digit tokens → lowercased word tokens.
  - CJK (Hangul, Han, Kana) runs → character bigrams.
  This is the cheapest way to get usable Korean recall without an external
  morphological analyzer such as KoNLPy or mecab-ko.
* Hybrid TF scoring with a small frontmatter boost.  Hits inside the YAML
  frontmatter (title, keywords, JEL codes, DOI) outrank hits buried deep in
  the body.
* Snippet extraction returns the matching line plus its surrounding context,
  with the file path and 1-indexed line number for editor jump-to.

Usage
-----
    # query from argv
    python3 search_papers.py "volatility ratio"
    python3 search_papers.py "베타 압축"
    python3 search_papers.py G14

    # query from stdin (useful for piping)
    echo "decoupling" | python3 search_papers.py -

    # restrict to a single field
    python3 search_papers.py --field keywords "airdrop"
    python3 search_papers.py --field jel "G14"

    # limit results
    python3 search_papers.py --top 3 "LLM"

    # show full matched lines with context
    python3 search_papers.py --context 2 "Spearman"

    # list everything the index knows about
    python3 search_papers.py --index

Exit codes
----------
    0  → at least one result found (or --index / --help succeeded)
    1  → no results
    2  → invalid arguments or no readable papers
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PAPERS_DIR = SCRIPT_DIR.parent
PAPER_GLOB = "0*_SSRN-*.md"

# ---------------------------------------------------------------------------
# Tokenization
# ---------------------------------------------------------------------------

# A "word" run: ASCII letters, digits, underscore, hyphen.
_WORD_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_\-]*")

# A CJK run: any contiguous block of Hangul syllables, Han ideographs, or Kana.
# We intentionally keep this loose and let unicodedata classify each char.
def _is_cjk(ch: str) -> bool:
    if not ch:
        return False
    code = ord(ch)
    # Hangul Syllables
    if 0xAC00 <= code <= 0xD7A3:
        return True
    # Hangul Jamo
    if 0x1100 <= code <= 0x11FF:
        return True
    # Hangul Compatibility Jamo
    if 0x3130 <= code <= 0x318F:
        return True
    # CJK Unified Ideographs (common range)
    if 0x4E00 <= code <= 0x9FFF:
        return True
    # Hiragana / Katakana
    if 0x3040 <= code <= 0x30FF:
        return True
    return False


def tokenize(text: str) -> list[str]:
    """Two-track tokenizer.

    Returns a flat list of search tokens.  Latin/digit runs become single
    lowercase tokens; CJK runs are split into character bigrams (with the
    first character also emitted as a unigram so single-character queries
    still match).
    """
    if not text:
        return []

    # Normalize so that composed and decomposed Hangul forms compare equal.
    text = unicodedata.normalize("NFC", text)

    tokens: list[str] = []

    # Pass 1: pull out latin/digit words.
    for m in _WORD_RE.finditer(text):
        tokens.append(m.group(0).lower())

    # Pass 2: walk through CJK runs and emit character bigrams.
    run: list[str] = []
    for ch in text:
        if _is_cjk(ch):
            run.append(ch)
        else:
            if run:
                tokens.extend(_cjk_ngrams(run))
                run = []
    if run:
        tokens.extend(_cjk_ngrams(run))

    return tokens


def _cjk_ngrams(run: list[str]) -> list[str]:
    """Emit bigrams (and unigrams as a fallback) for a CJK character run."""
    if not run:
        return []
    if len(run) == 1:
        return [run[0]]
    grams = []
    for i in range(len(run) - 1):
        grams.append(run[i] + run[i + 1])
    # Also keep first and last chars as unigrams so 1-char queries hit.
    grams.append(run[0])
    grams.append(run[-1])
    return grams


# ---------------------------------------------------------------------------
# YAML frontmatter parser (a minimal, stdlib-only subset)
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str, int]:
    """Split a markdown file into (frontmatter_dict, body, body_start_line).

    Supports the subset of YAML used in this paper folder:
      * scalar values (strings, numbers, ISO dates)
      * inline lists `[a, b, c]`
      * block lists with `-` items
      * one level of nested mapping
    """
    if not text.startswith("---"):
        return {}, text, 1

    lines = text.splitlines()
    if not lines:
        return {}, text, 1

    # Find the closing `---`.
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx == -1:
        return {}, text, 1

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :])
    body_start_line = end_idx + 2  # 1-indexed line where body starts

    data: dict = {}
    current_key: str | None = None
    current_list: list | None = None
    current_map: dict | None = None
    current_map_key: str | None = None

    for raw in fm_lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue

        # Nested-map item ( "  - key: value" or "    key: value" )
        stripped = raw.lstrip()
        indent = len(raw) - len(stripped)

        if indent >= 2 and current_list is not None and stripped.startswith("- "):
            # Start of a new dict in a list of dicts
            rest = stripped[2:].strip()
            if ":" in rest:
                k, _, v = rest.partition(":")
                new_obj = {k.strip(): _coerce(v.strip())}
                current_list.append(new_obj)
                current_map = new_obj
            else:
                current_list.append(_coerce(rest))
                current_map = None
            continue

        if indent >= 4 and current_map is not None and ":" in stripped:
            k, _, v = stripped.partition(":")
            current_map[k.strip()] = _coerce(v.strip())
            continue

        if indent >= 2 and current_list is not None and stripped.startswith("- "):
            current_list.append(_coerce(stripped[2:].strip()))
            continue

        # Top-level key
        if ":" in stripped and indent == 0:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            current_map = None
            current_map_key = None
            if not val:
                # Could be a block list or block map starting on next line
                current_key = key
                current_list = []
                data[key] = current_list
            elif val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                if inner:
                    items = [_coerce(p.strip()) for p in _split_inline(inner)]
                else:
                    items = []
                data[key] = items
                current_key = None
                current_list = None
            else:
                data[key] = _coerce(val)
                current_key = None
                current_list = None
        elif indent >= 2 and current_key is not None and stripped.startswith("- "):
            current_list.append(_coerce(stripped[2:].strip()))

    # If a "list" only ever got dict-shaped pushes via `- key: value`, leave it
    # as-is — downstream consumers treat list-of-dicts uniformly.

    return data, body, body_start_line


def _coerce(v: str):
    """Best-effort scalar coercion: keep strings as strings, strip quotes."""
    if v == "":
        return ""
    if (v.startswith('"') and v.endswith('"')) or (
        v.startswith("'") and v.endswith("'")
    ):
        return v[1:-1]
    # Booleans
    if v.lower() in {"true", "false"}:
        return v.lower() == "true"
    # Integers
    if re.fullmatch(r"-?\d+", v):
        try:
            return int(v)
        except ValueError:
            pass
    # Floats
    if re.fullmatch(r"-?\d+\.\d+", v):
        try:
            return float(v)
        except ValueError:
            pass
    return v


def _split_inline(s: str) -> list[str]:
    """Split a comma-separated inline list while respecting quoted commas."""
    parts: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    for ch in s:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            buf.append(ch)
        elif ch == ",":
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf).strip())
    return parts


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

@dataclass
class PaperDoc:
    path: Path
    frontmatter: dict
    body: str
    body_start_line: int
    # field_name -> joined string for that field (used for --field search)
    fields: dict[str, str] = field(default_factory=dict)


def load_papers(papers_dir: Path) -> list[PaperDoc]:
    docs: list[PaperDoc] = []
    for md in sorted(papers_dir.glob(PAPER_GLOB)):
        try:
            text = md.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"warn: could not read {md}: {exc}", file=sys.stderr)
            continue
        fm, body, body_start = parse_frontmatter(text)
        fields = _flatten_fields(fm)
        docs.append(
            PaperDoc(
                path=md,
                frontmatter=fm,
                body=body,
                body_start_line=body_start,
                fields=fields,
            )
        )
    return docs


def _flatten_fields(fm: dict) -> dict[str, str]:
    """Produce a flat field_name -> string mapping for field-restricted search."""
    out: dict[str, str] = {}
    for k, v in fm.items():
        out[k.lower()] = _stringify(v)
    return out


def _stringify(v) -> str:
    if isinstance(v, list):
        return " ".join(_stringify(x) for x in v)
    if isinstance(v, dict):
        return " ".join(f"{k} {_stringify(val)}" for k, val in v.items())
    return str(v)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

@dataclass
class Hit:
    doc: PaperDoc
    score: float
    matched_tokens: set[str]
    snippets: list[tuple[int, str]]  # (line_number, line_text)


# Friendly field aliases: short user-facing name -> list of frontmatter keys.
# `--field jel` should find jel_codes, `--field keywords` should find both
# English and Korean keyword lists, etc.
FIELD_ALIASES: dict[str, list[str]] = {
    "jel": ["jel", "jel_codes"],
    "keywords": ["keywords", "keywords_en", "keywords_ko"],
    "kw": ["keywords", "keywords_en", "keywords_ko"],
    "title": ["title", "title_ko", "short_title"],
    "authors": ["authors"],
    "doi": ["doi"],
    "ssrn": ["ssrn_id", "url", "canonical_url"],
    "ssrn_id": ["ssrn_id"],
    "orcid": ["authors"],
    "license": ["license"],
    "language": ["language"],
}


def _resolve_field(field_name: str, doc: PaperDoc) -> str:
    """Resolve a user-facing field name to a concatenated string from the
    matching frontmatter key(s), honoring FIELD_ALIASES.
    """
    key = field_name.lower()
    candidates = FIELD_ALIASES.get(key, [key])
    parts: list[str] = []
    for c in candidates:
        v = doc.fields.get(c.lower(), "")
        if v:
            parts.append(v)
    return " ".join(parts)


def search(
    docs: list[PaperDoc],
    query: str,
    field_name: str | None = None,
    context: int = 1,
    top: int = 5,
) -> list[Hit]:
    q_tokens = tokenize(query)
    if not q_tokens:
        return []
    q_set = set(q_tokens)

    hits: list[Hit] = []
    for doc in docs:
        if field_name:
            field_text = _resolve_field(field_name, doc)
            if not field_text:
                continue
            d_tokens = set(tokenize(field_text))
            matched = q_set & d_tokens
            if not matched:
                continue
            score = len(matched)
            snippets = [(0, field_text[:240])]
            hits.append(Hit(doc=doc, score=score, matched_tokens=matched, snippets=snippets))
            continue

        # Full-document search: tokenize frontmatter values + body
        fm_text = " ".join(doc.fields.values())
        fm_tokens = set(tokenize(fm_text))
        body_tokens = set(tokenize(doc.body))
        matched_fm = q_set & fm_tokens
        matched_body = q_set & body_tokens
        matched = matched_fm | matched_body
        if not matched:
            continue

        # Frontmatter hits weight 2x — they're closer to the paper's identity.
        score = 2.0 * len(matched_fm) + 1.0 * len(matched_body)

        snippets = _extract_snippets(doc, q_set, context=context)
        hits.append(Hit(doc=doc, score=score, matched_tokens=matched, snippets=snippets))

    hits.sort(key=lambda h: (-h.score, h.doc.path.name))
    return hits[:top]


def _extract_snippets(
    doc: PaperDoc,
    q_set: set[str],
    context: int = 1,
    max_snippets: int = 4,
) -> list[tuple[int, str]]:
    """Pull up to `max_snippets` matching body lines with `context` lines around."""
    lines = doc.body.splitlines()
    matched_line_indices: list[int] = []
    for i, line in enumerate(lines):
        line_tokens = set(tokenize(line))
        if q_set & line_tokens:
            matched_line_indices.append(i)
            if len(matched_line_indices) >= max_snippets:
                break

    snippets: list[tuple[int, str]] = []
    seen: set[int] = set()
    for idx in matched_line_indices:
        lo = max(0, idx - context)
        hi = min(len(lines) - 1, idx + context)
        for j in range(lo, hi + 1):
            if j in seen:
                continue
            seen.add(j)
            line_no = doc.body_start_line + j
            text = lines[j].rstrip()
            if not text:
                continue
            snippets.append((line_no, text))
    return snippets


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_hits(hits: list[Hit], query: str, as_json: bool = False) -> None:
    if as_json:
        payload = {
            "query": query,
            "result_count": len(hits),
            "results": [
                {
                    "file": str(h.doc.path),
                    "title": h.doc.frontmatter.get("title", ""),
                    "title_ko": h.doc.frontmatter.get("title_ko", ""),
                    "doi": h.doc.frontmatter.get("doi", ""),
                    "ssrn_id": h.doc.frontmatter.get("ssrn_id", ""),
                    "score": h.score,
                    "matched_tokens": sorted(h.matched_tokens),
                    "snippets": [
                        {"line": ln, "text": tx} for ln, tx in h.snippets
                    ],
                }
                for h in hits
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    if not hits:
        print(f"No results for: {query}")
        return

    print(f"\n{len(hits)} result(s) for: {query}\n")
    for i, h in enumerate(hits, 1):
        title = h.doc.frontmatter.get("title", "(untitled)")
        title_ko = h.doc.frontmatter.get("title_ko", "")
        doi = h.doc.frontmatter.get("doi", "")
        ssrn = h.doc.frontmatter.get("ssrn_id", "")
        print(f"[{i}] score={h.score:.1f}  {h.doc.path.name}")
        print(f"     EN : {title}")
        if title_ko:
            print(f"     KO : {title_ko}")
        if doi:
            print(f"     DOI: {doi}    SSRN: {ssrn}")
        print(f"     hits: {', '.join(sorted(h.matched_tokens))}")
        for ln, tx in h.snippets:
            if ln == 0:
                print(f"        | {tx}")
            else:
                print(f"     L{ln:>4} | {tx}")
        print()


def print_index(docs: list[PaperDoc]) -> None:
    print(f"Indexed {len(docs)} paper(s) under {PAPERS_DIR}\n")
    for d in docs:
        title = d.frontmatter.get("title", "(untitled)")
        title_ko = d.frontmatter.get("title_ko", "")
        doi = d.frontmatter.get("doi", "")
        ssrn = d.frontmatter.get("ssrn_id", "")
        pages = d.frontmatter.get("pages", "")
        kw = d.frontmatter.get("keywords", []) or d.frontmatter.get("keywords_en", [])
        jel = d.frontmatter.get("jel", []) or d.frontmatter.get("jel_codes", [])
        print(f"- {d.path.name}")
        print(f"    EN  : {title}")
        if title_ko:
            print(f"    KO  : {title_ko}")
        print(f"    DOI : {doi}")
        print(f"    SSRN: {ssrn}   pages: {pages}")
        if kw:
            kw_str = ", ".join(str(x) for x in (kw if isinstance(kw, list) else [kw]))
            print(f"    kw  : {kw_str}")
        if jel:
            jel_str = ", ".join(str(x) for x in (jel if isinstance(jel, list) else [jel]))
            print(f"    JEL : {jel_str}")
        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="search_papers.py",
        description=(
            "Bilingual (KO/EN) full-text search across the SSRN papers folder. "
            "Use '-' as the query to read from stdin."
        ),
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Search query. Use '-' to read from stdin.",
    )
    parser.add_argument(
        "--field",
        help=(
            "Restrict search to a single frontmatter field "
            "(e.g. keywords, jel, doi, authors, title)."
        ),
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Max number of results to show (default: 5).",
    )
    parser.add_argument(
        "--context",
        type=int,
        default=1,
        help="Lines of context around each matching line (default: 1).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit results as JSON (machine-readable).",
    )
    parser.add_argument(
        "--index",
        action="store_true",
        help="Print the indexed paper list and exit.",
    )
    parser.add_argument(
        "--papers-dir",
        type=Path,
        default=PAPERS_DIR,
        help=f"Folder containing paper markdown files (default: {PAPERS_DIR}).",
    )
    args = parser.parse_args(argv)

    docs = load_papers(args.papers_dir)
    if not docs:
        print(
            f"error: no paper files found under {args.papers_dir} "
            f"(expected pattern: {PAPER_GLOB})",
            file=sys.stderr,
        )
        return 2

    if args.index:
        print_index(docs)
        return 0

    if not args.query:
        parser.print_help()
        return 2

    if args.query == "-":
        query = sys.stdin.read().strip()
    else:
        query = args.query

    if not query:
        print("error: empty query", file=sys.stderr)
        return 2

    hits = search(
        docs,
        query,
        field_name=args.field,
        context=args.context,
        top=args.top,
    )
    print_hits(hits, query, as_json=args.json)
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())
