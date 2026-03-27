"""Post-process CadQuery SVGs to add light/dark theme support.

Injects CSS with @media (prefers-color-scheme: dark) into each SVG.
Adds a themed background rect and inverts stroke colors for dark mode.

Usage:
    python hardware/cad/theme_svgs.py
"""

from pathlib import Path

THEME_CSS = """\
  <defs>
    <style>
      .cq-bg { fill: #ffffff; }
      @media (prefers-color-scheme: dark) {
        .cq-bg { fill: #0d1117; }
        g[stroke="rgb(0,0,0)"] { stroke: #c9d1d9 !important; }
        g[stroke="rgb(160,160,160)"] { stroke: #484f58 !important; }
        line { stroke: #c9d1d9 !important; }
        text { stroke: #c9d1d9 !important; fill: #c9d1d9 !important; }
      }
    </style>
  </defs>"""

SVG_DIR = Path(__file__).parent.parent / "svg"
SKIP = {"system_overview.svg"}  # Already themed manually


def theme_svg(path: Path) -> None:
    """Inject theme CSS into a CadQuery-generated SVG."""
    content = path.read_text()

    if "prefers-color-scheme" in content:
        return  # Already themed

    # Extract width/height from SVG tag
    w = h = "100%"
    for attr in ["width", "height"]:
        import re

        match = re.search(rf'{attr}="([^"]+)"', content)
        if match:
            if attr == "width":
                w = match.group(1)
            else:
                h = match.group(1)

    # Insert after opening <svg> tag
    bg_rect = f'  <rect width="{w}" height="{h}" class="cq-bg"/>'
    injection = f"\n{THEME_CSS}\n{bg_rect}\n"

    # Find end of <svg ...> tag
    svg_end = content.index(">") + 1
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
