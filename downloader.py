# coding: utf-8
# Asset bundler for PMDV.
#
# Fetches the vendored CSS/JS libraries, gzips and base64-encodes them, and
# rewrites the ASSETS dict inside pmdv/viewer.py *in place*.
#
# This script used to carry a full copy of viewer.py in a VIEWER_TEMPLATE
# string and regenerate the module from scratch. That copy drifted out of sync
# with the real source, so running it silently reverted features. Editing only
# the ASSETS block removes that failure mode: viewer.py is the single source of
# truth for code, this file is the single source of truth for bundled assets.
#
# units: s

import argparse
import base64
import gzip
import os
import sys
import urllib.request

TIMEOUT = 15

ASSET_URLS = {
    "github_css": "https://cdn.jsdelivr.net/npm/github-markdown-css@5.5.1/github-markdown.min.css",
    "prism_css": "https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css",
    "katex_css": "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css",
    "marked_js": "https://cdn.jsdelivr.net/npm/marked@12.0.1/marked.min.js",
    "markdown_it_js": "https://cdn.jsdelivr.net/npm/markdown-it@14.1.0/dist/markdown-it.min.js",
    "prism_js": "https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js",
    "katex_js": "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js",
    "mermaid_js": "https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js",
}

BLOCK_START = "ASSETS = {"
BLOCK_END = "\n}\n"


def find_viewer(explicit=None):
    """Locate pmdv/viewer.py relative to this script, or use an explicit path."""
    if explicit:
        if not os.path.exists(explicit):
            sys.exit(f"Error: {explicit} does not exist.")
        return os.path.abspath(explicit)

    here = os.path.dirname(os.path.abspath(__file__))
    for candidate in (
        os.path.join(here, "pmdv", "viewer.py"),
        os.path.join(here, "viewer.py"),
    ):
        if os.path.exists(candidate):
            return candidate

    sys.exit("Error: could not find viewer.py. Pass its path with --viewer.")


def download_assets():
    """Fetch every asset and return {name: gzip+base64 text}."""
    assets_b64 = {}
    print("Starting assets downloading...")
    for name, url in ASSET_URLS.items():
        print(f"Downloading {name} from {url}...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                content = response.read()
        except Exception as e:
            sys.exit(f"Failed to download {name}: {e}")

        encoded = base64.b64encode(gzip.compress(content)).decode("utf-8")
        print(f"  {len(content):,} bytes -> {len(encoded):,} chars encoded")
        assets_b64[name] = encoded
    return assets_b64


def render_block(assets):
    """Render the ASSETS dict literal, one asset per line, in ASSET_URLS order."""
    names = [name for name in ASSET_URLS if name in assets]
    lines = [BLOCK_START]
    for index, name in enumerate(names):
        comma = "," if index < len(names) - 1 else ""
        lines.append(f'    "{name}": b"""{assets[name]}"""{comma}')
    lines.append("}")
    return "\n".join(lines) + "\n"


def read_block(source):
    """Return (start, end) offsets of the ASSETS dict literal in source."""
    try:
        start = source.index(BLOCK_START)
    except ValueError:
        sys.exit(f"Error: could not find `{BLOCK_START}` in viewer.py.")
    try:
        end = source.index(BLOCK_END, start) + len(BLOCK_END)
    except ValueError:
        sys.exit("Error: the ASSETS block in viewer.py is not terminated by a lone `}`.")
    return start, end


def parse_embedded(source):
    """Extract {name: base64} from the ASSETS block already in viewer.py."""
    start, end = read_block(source)
    embedded = {}
    for line in source[start:end].splitlines():
        line = line.strip()
        if not line.startswith('"'):
            continue
        name, _, rest = line.partition('":')
        name = name.lstrip('"')
        value = rest.strip().rstrip(",").strip()
        if value.startswith('b"""') and value.endswith('"""'):
            embedded[name] = value[4:-3]
    return embedded


def check_assets(assets, label):
    """Decode every asset so a corrupt bundle fails here, not at runtime."""
    problems = []
    for name in ASSET_URLS:
        raw = assets.get(name)
        if not raw:
            problems.append(f"{name}: missing")
            continue
        if raw.startswith("$"):
            problems.append(f"{name}: still a placeholder")
            continue
        try:
            decoded = gzip.decompress(base64.b64decode(raw)).decode("utf-8")
        except Exception as e:
            problems.append(f"{name}: {e.__class__.__name__}: {e}")
            continue
        print(f"  ok {name}: {len(decoded):,} chars")

    if problems:
        print(f"\n{label} FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return False

    print(f"{label} passed ({len(ASSET_URLS)} assets).")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Bundle offline assets into the ASSETS dict of pmdv/viewer.py."
    )
    parser.add_argument("--viewer", help="path to viewer.py (default: ./pmdv/viewer.py)")
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the assets already embedded in viewer.py; downloads nothing",
    )
    args = parser.parse_args()

    viewer_path = find_viewer(args.viewer)
    with open(viewer_path, "r", encoding="utf-8") as f:
        source = f.read()

    if args.check:
        print(f"Checking embedded assets in {viewer_path}")
        sys.exit(0 if check_assets(parse_embedded(source), "Check") else 1)

    assets = download_assets()

    print("\nVerifying downloaded assets...")
    if not check_assets(assets, "Verification"):
        sys.exit(1)

    start, end = read_block(source)
    updated = source[:start] + render_block(assets) + source[end:]

    # Refuse to write a file that would not import.
    import ast

    try:
        ast.parse(updated)
    except SyntaxError as e:
        sys.exit(f"Refusing to write: generated source is invalid Python ({e}).")

    with open(viewer_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(updated)

    print(f"\nUpdated ASSETS in {viewer_path} ({len(assets)} assets embedded).")
    print("Code outside the ASSETS block was left untouched.")


if __name__ == '__main__':
    main()
