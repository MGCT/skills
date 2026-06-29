#!/usr/bin/env python3
"""Render an HTML file to PDF using a headless Chrome or Edge already on the machine.

No third-party deps: deliverable skills author a designed document as HTML+CSS and
call this to print it to a client-ready PDF. Finds a Chromium-family browser
(Edge or Chrome), runs it headless with --print-to-pdf, and verifies the output.

Vendored identically into each deliverable skill (roadmap-doc, timeline,
desk-research). Keep the copies in sync.

Usage:
  python render_pdf.py INPUT.html [OUTPUT.pdf] [--browser auto|edge|chrome|PATH]

Notes:
- Background colours/images print only if the CSS opts in with
  `-webkit-print-color-adjust: exact` (house-style.css does this) and `@page`
  controls size/margins.
- Set CHROME_PATH to force a specific browser binary.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

WIN_CANDIDATES = [
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]
PATH_NAMES = ["msedge", "google-chrome", "chrome", "chromium", "chromium-browser"]
MAC_CANDIDATES = [
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


def find_browser(pref="auto"):
    if pref not in ("auto", "edge", "chrome"):
        return pref  # explicit path
    env = os.environ.get("CHROME_PATH")
    if env and Path(env).exists():
        return env
    cands = []
    if sys.platform.startswith("win"):
        cands = WIN_CANDIDATES
    elif sys.platform == "darwin":
        cands = MAC_CANDIDATES
    if pref == "edge":
        cands = [c for c in cands if "edge" in c.lower()]
    elif pref == "chrome":
        cands = [c for c in cands if "hrome" in c or "hromium" in c]
    for c in cands:
        if Path(c).exists():
            return c
    for name in PATH_NAMES:
        found = shutil.which(name)
        if found:
            return found
    return None


def render(html_path: Path, pdf_path: Path, browser: str) -> None:
    url = html_path.resolve().as_uri()  # correct file:// URL on every OS
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path.resolve()}",
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        # older builds reject --headless=new; retry with legacy flag
        cmd[1] = "--headless"
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        raise SystemExit(
            f"PDF not produced. Browser: {browser}\n"
            f"stderr: {proc.stderr[-800:]}"
        )


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render HTML to PDF via headless Chrome/Edge.")
    ap.add_argument("input")
    ap.add_argument("output", nargs="?")
    ap.add_argument("--browser", default="auto")
    args = ap.parse_args(argv)

    html_path = Path(args.input)
    if not html_path.exists():
        raise SystemExit(f"Input HTML not found: {html_path}")
    pdf_path = Path(args.output) if args.output else html_path.with_suffix(".pdf")

    browser = find_browser(args.browser)
    if not browser:
        raise SystemExit(
            "No Chrome/Edge found. Install one, or set CHROME_PATH to the binary."
        )
    render(html_path, pdf_path, browser)
    print(f"Wrote {pdf_path}  ({pdf_path.stat().st_size:,} bytes)  via {Path(browser).name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
