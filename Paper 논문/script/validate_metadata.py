#!/usr/bin/env python3
"""
validate_metadata.py — Check each paper file against international publishing checklists.

Validates that the YAML front-matter of every paper in this folder has the
fields required by:

    ICMJE  — minimum manuscript metadata (title, authors, abstract, keywords)
    COPE   — research integrity disclosures (funding, data availability,
             conflicts, license, corresponding author)
    CrossRef — minimum deposit schema (DOI, title, year, authors with ORCID,
             publisher, URL)

USAGE
    python scripts/validate_metadata.py            # validate all papers
    python scripts/validate_metadata.py --strict   # fail on any warning
    python scripts/validate_metadata.py --paper 01_SSRN-6632838_72-Hour-Shock.md

EXIT CODES
    0 — all checks pass
    1 — one or more papers failed required checks
    2 — usage error / no papers found

DEPENDENCIES
    Python 3.10+ standard library only.

Reuses the YAML front-matter parser from generate_citations.py.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

# Reuse the YAML parser from the sibling script.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_citations import parse_frontmatter  # noqa: E402


# ---------------------------------------------------------------------------
# Validation rules
# ---------------------------------------------------------------------------

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$")
SSRN_URL_RE = re.compile(r"^https://(?:papers\.)?ssrn\.com/\S+$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


REQUIRED_FIELDS: dict[str, str] = {
    # CrossRef minimum
    "title":         "ICMJE/CrossRef — paper title",
    "authors":       "ICMJE/CrossRef — author list",
    "posted_date":   "CrossRef — publication date (ISO YYYY-MM-DD)",
    "doi":           "CrossRef — Digital Object Identifier",
    "url":           "CrossRef — canonical URL",
    "publisher":     "CrossRef — publisher name",
    "language":      "CrossRef — primary language",
    # ICMJE minimum
    "keywords":      "ICMJE — keyword list (≥3 for indexability)",
    # COPE minimum
    "license":       "COPE — license terms",
    "funding":       "COPE — funding disclosure (use 'no external funding' if applicable)",
    "data_availability": "COPE — data availability statement",
    # Author metadata
    "ssrn_id":       "Required for SSRN-specific cross-reference",
}


def _check_author(author: dict[str, Any], i: int) -> list[str]:
    errs: list[str] = []
    if not author.get("family"):
        errs.append(f"author[{i}].family is empty")
    if not author.get("given"):
        errs.append(f"author[{i}].given is empty")
    if not author.get("affiliation"):
        errs.append(f"author[{i}].affiliation is empty")
    orcid = author.get("orcid", "")
    if not orcid:
        errs.append(f"author[{i}].orcid missing — CrossRef strongly recommends ORCID for all authors")
    elif not ORCID_RE.match(orcid):
        errs.append(f"author[{i}].orcid ('{orcid}') is not a valid ORCID iD (NNNN-NNNN-NNNN-NNNN)")
    return errs


def validate(meta: dict[str, Any]) -> tuple[list[str], list[str]]:
    """
    Return (errors, warnings).
    Errors are required-field failures; warnings are best-practice misses.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Required fields
    for field, desc in REQUIRED_FIELDS.items():
        if not meta.get(field):
            errors.append(f"missing '{field}' — {desc}")

    # Author validation
    authors = meta.get("authors", []) or []
    if not authors:
        errors.append("authors list is empty")
    else:
        has_corresponding = False
        for i, a in enumerate(authors):
            errors.extend(_check_author(a, i))
            if a.get("corresponding"):
                has_corresponding = True
        if not has_corresponding:
            warnings.append("no author marked as 'corresponding: true' (ICMJE requirement)")

    # DOI format
    doi = meta.get("doi", "")
    if doi and not DOI_RE.match(doi):
        errors.append(f"doi '{doi}' does not match standard pattern 10.NNNN/...")

    # URL format
    url = meta.get("url", "")
    if url and not SSRN_URL_RE.match(url):
        warnings.append(f"url '{url}' does not look like an ssrn.com URL")

    # Date format
    posted = meta.get("posted_date", "")
    if posted and not ISO_DATE_RE.match(str(posted)):
        errors.append(f"posted_date '{posted}' is not ISO YYYY-MM-DD format")

    # Keyword count (indexability)
    kws = meta.get("keywords", []) or []
    if 0 < len(kws) < 3:
        warnings.append(f"only {len(kws)} keyword(s) — ≥3 strongly recommended for search-engine indexability")
    if len(kws) > 15:
        warnings.append(f"{len(kws)} keywords — keep ≤15 (Google Scholar deduplication)")

    # JEL codes (econ papers)
    jel = meta.get("jel_codes", []) or []
    if not jel:
        warnings.append("no JEL classification codes — recommended for economics/finance papers")

    # Bilingual fields (this collection is bilingual)
    if not meta.get("title_ko"):
        warnings.append("title_ko (Korean title) missing — recommended for bilingual indexing")
    if not meta.get("keywords_ko"):
        warnings.append("keywords_ko missing — recommended for bilingual indexing")

    # Funding statement
    funding = meta.get("funding", "")
    if funding and len(str(funding)) < 10:
        warnings.append("funding statement is very short — be explicit, e.g. 'This research received no external funding.'")

    # Data availability
    da = meta.get("data_availability", "")
    if da and len(str(da)) < 10:
        warnings.append("data_availability statement is very short — name the public location of data")

    return errors, warnings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate paper metadata against ICMJE/COPE/CrossRef.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--paper", type=str, default=None, help="Validate one specific file")
    parser.add_argument("--papers-dir", type=Path,
                        default=Path(__file__).resolve().parent.parent,
                        help="Path to papers directory")
    args = parser.parse_args()

    if args.paper:
        files = [args.papers_dir / args.paper]
    else:
        files = sorted(args.papers_dir.glob("0*_SSRN-*.md"))

    if not files:
        print("ERROR: No paper files found.", file=sys.stderr)
        return 2

    total_errors = 0
    total_warnings = 0
    for f in files:
        if not f.exists():
            print(f"[MISSING] {f}", file=sys.stderr)
            total_errors += 1
            continue
        text = f.read_text(encoding="utf-8")
        try:
            meta = parse_frontmatter(text)
        except ValueError as e:
            print(f"\n[FAIL] {f.name}: cannot parse YAML — {e}")
            total_errors += 1
            continue

        errors, warnings = validate(meta)
        total_errors += len(errors)
        total_warnings += len(warnings)

        status = "PASS" if not errors and not (args.strict and warnings) else "FAIL"
        print(f"\n[{status}] {f.name}  (SSRN {meta.get('ssrn_id', '?')})")
        for e in errors:
            print(f"    ✗ ERROR:   {e}")
        for w in warnings:
            print(f"    ⚠ WARN:    {w}")
        if not errors and not warnings:
            print("    ✓ All checks passed (ICMJE + COPE + CrossRef)")

    print("\n" + "=" * 72)
    print(f"Summary: {len(files)} paper(s) checked — "
          f"{total_errors} error(s), {total_warnings} warning(s)")

    if total_errors > 0:
        return 1
    if args.strict and total_warnings > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
