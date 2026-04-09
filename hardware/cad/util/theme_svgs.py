"""Post-process SVGs (CadQuery or OpenSCAD) to add light/dark theme support.

Injects CSS with @media (prefers-color-scheme: dark) into each SVG.
Adds a themed background rect and inverts stroke colors for dark mode.

Usage:
    python hardware/cad/util/theme_svgs.py
"""

import re
from pathlib import Path

THEME_STYLE = """\
  <defs>
    <style>
      .cq-bg { fill: #ffffff; }
      @media (prefers-color-scheme: dark) {
        .cq-bg { fill: #0d1117; }
        /* CadQuery SVG selectors */
        g[stroke="rgb(0,0,0)"] { stroke: #c9d1d9 !important; }
        g[stroke="rgb(160,160,160)"] { stroke: #484f58 !important; }
        /* OpenSCAD SVG selectors */
        path { stroke: #c9d1d9 !important; }
        polygon { stroke: #c9d1d9 !important; fill: #161b22 !important; }
        /* Common selectors */
        line { stroke: #c9d1d9 !important; }
        text { stroke: #c9d1d9 !important; fill: #c9d1d9 !important; }
      }
    </style>
  </defs>"""

SVG_DIR = Path(__file__).parent.parent.parent / "svg"
SKIP = {"system_overview.svg"}


def theme_svg(path: Path) -> None:
    """Inject theme CSS into a CadQuery-generated SVG."""
    content = path.read_text()

    if "prefers-color-scheme" in content:
        return

    # Find the end of the <svg ...> opening tag (not <?xml ?>)
    match = re.search(r"<svg\b[^>]*>", content)
    if not match:
        print(f"Skipped: {path.name} (no <svg> tag found)")
        return

    svg_end = match.end()

    # Extract width/height
    w_match = re.search(r'width="([^"]+)"', match.group())
    h_match = re.search(r'height="([^"]+)"', match.group())
    w = w_match.group(1) if w_match else "100%"
    h = h_match.group(1) if h_match else "100%"

    bg_rect = f'  <rect width="{w}" height="{h}" class="cq-bg"/>'
    injection = f"\n{THEME_STYLE}\n{bg_rect}"

    themed = content[:svg_end] + injection + content[svg_end:]
    path.write_text(themed)
    print(f"Themed: {path.name}")


def main() -> None:
    """Theme all SVGs in hardware/svg/."""
    for svg in sorted(SVG_DIR.glob("*.svg")):
        if svg.name in SKIP:
            print(f"Skipped: {svg.name} (manually themed)")
            continue
        theme_svg(svg)


if __name__ == "__main__":
    main()
