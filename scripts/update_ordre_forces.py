#!/usr/bin/env python3
"""
Download FCE ordre de forces PDF for Escacs Comtal, verify club identity, render PNGs for the site.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import fitz

# Federació Catalana d'Escacs — endpoint (idClub may change if FCE reassigns; validate text below)
URL_BASE = "https://escacs.cat/components/com_fce/gmvw20/conn/ordre-forces-pdf.php"
ID_CLUB = 90

# Must appear in PDF text (case-insensitive)
REQUIRED_SUBSTRING = "COMTAL"

# ~150 DPI equivalent for readability (72 pt page * zoom)
RENDER_ZOOM = 150 / 72

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:149.0) Gecko/20100101 Firefox/149.0"
)
REFERER = "https://escacs.cat/index.php/component/fce?op=1"


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _pdf_url() -> str:
    return f"{URL_BASE}?idClub={ID_CLUB}"


def fetch_pdf() -> bytes:
    req = Request(
        _pdf_url(),
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": REFERER,
        },
        method="GET",
    )
    try:
        with urlopen(req, timeout=60) as resp:
            status = getattr(resp, "status", 200)
            if status != 200:
                raise SystemExit(f"HTTP {status} from {_pdf_url()}")
            ctype = resp.headers.get("Content-Type", "")
            data = resp.read()
    except HTTPError as e:
        raise SystemExit(f"HTTP error {e.code}: {e.reason}") from e
    except URLError as e:
        raise SystemExit(f"Network error: {e.reason}") from e

    if not data:
        raise SystemExit("Empty response body")
    if "pdf" not in ctype.lower() and not data.startswith(b"%PDF"):
        raise SystemExit(
            f"Expected PDF (Content-Type: {ctype!r}), got {len(data)} bytes"
        )
    return data


def verify_comtal(doc: fitz.Document) -> None:
    text = "".join(page.get_text() for page in doc)
    normalized = re.sub(r"\s+", " ", text).strip()
    if REQUIRED_SUBSTRING.upper() not in normalized.upper():
        raise SystemExit(
            f"Refusing to update: PDF text does not contain {REQUIRED_SUBSTRING!r}. "
            "Wrong idClub or club renamed — check FCE."
        )


def render_pages(doc: fitz.Document, out_dir: Path, zoom: float) -> None:
    n = doc.page_count
    if n != 2:
        raise SystemExit(
            f"Expected exactly 2 PDF pages (site has two PNGs), got {n}"
        )

    mat = fitz.Matrix(zoom, zoom)
    for i in range(n):
        page = doc[i]
        pix = page.get_pixmap(matrix=mat, alpha=False)
        out_path = out_dir / f"ordre-forces_COM-{i + 1}.png"
        pix.save(str(out_path))
        print(f"Wrote {out_path}")


def main() -> None:
    pdf_bytes = fetch_pdf()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        verify_comtal(doc)
        out_dir = _repo_root() / "assets" / "images"
        if not out_dir.is_dir():
            raise SystemExit(f"Missing directory: {out_dir}")
        render_pages(doc, out_dir, RENDER_ZOOM)
    finally:
        doc.close()


if __name__ == "__main__":
    main()
