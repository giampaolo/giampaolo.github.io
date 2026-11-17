#!/usr/bin/env python3
"""Build resume.yaml into HTML (and optionally PDF).

Reads:
    resume.yaml           data (JSON Resume-ish)
    resume.html           Jinja template
    style.css             stylesheet (embedded into the HTML)
    fonts/*.woff2         fonts (embedded into the HTML)

Writes:
    _build/resume.html    always
    _build/resume.pdf     only when --pdf is passed
"""

import argparse
import base64
import re
import sys
from pathlib import Path

import jinja2
import markdown
import weasyprint
import yaml
from markupsafe import Markup

YAML_PATH = None
TEMPLATE_PATH = None
CSS_PATH = None
HTML_OUT = None
PDF_OUT = None
MAKE_PDF = None

MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def parse_cli():
    global YAML_PATH, TEMPLATE_PATH, CSS_PATH, HTML_OUT, PDF_OUT, MAKE_PDF
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--yaml", default=str(here / "resume.yaml"))
    ap.add_argument("--template", default=str(here / "resume.html"))
    ap.add_argument("--css", default=str(here / "style.css"))
    ap.add_argument("--html", default=str(here / "_build" / "resume.html"))
    ap.add_argument("--pdf-out", default=str(here / "_build" / "resume.pdf"))
    ap.add_argument(
        "--pdf",
        action="store_true",
        help="Also generate a PDF (default: HTML only)",
    )
    args = ap.parse_args()
    YAML_PATH = args.yaml
    TEMPLATE_PATH = args.template
    CSS_PATH = args.css
    HTML_OUT = args.html
    PDF_OUT = args.pdf_out
    MAKE_PDF = args.pdf


def fmt_date(value):
    """Format a date string for display.

    "2020-09" -> "Sep 2020"
    "2020"    -> "2020"
    "Present" -> "Present"
    None      -> "Present"
    """
    if not value:
        return "Present"
    s = str(value)
    m = re.match(r"^(\d{4})-(\d{1,2})$", s)
    if m:
        year, month = m.group(1), int(m.group(2))
        if 1 <= month <= 12:
            return f"{MONTHS[month - 1]} {year}"
    return s


def strip_scheme(url):
    if not url:
        return ""
    url = re.sub(r"^https?://", "", url)
    return url.rstrip("/")


def render_md(text):
    """Full markdown render (produces block-level HTML)."""
    if not text:
        return ""
    return markdown.markdown(
        text.strip(), extensions=["extra", "sane_lists", "smarty"]
    )


def render_md_inline(text):
    """Markdown render for inline use: strip the outer <p> tags."""
    html = render_md(text)
    m = re.match(r"^\s*<p>(.*)</p>\s*$", html, re.DOTALL)
    if m and "<p>" not in m.group(1):
        return m.group(1)
    return html


def load_yaml(path):
    return yaml.safe_load(Path(path).read_text())


def build_env(template_dir, links=None):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        autoescape=jinja2.select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    # Append shared link reference defs to every markdown string so any
    # prose can use [name] / [text][name] syntax. Unused refs are
    # harmless — Python-Markdown just drops them.
    refs = ""
    if links:
        refs = "\n\n" + "\n".join(
            f"[{name}]: {url}" for name, url in links.items()
        )

    # Markdown filters return pre-rendered HTML, so mark them safe.
    env.filters["md"] = lambda s: Markup(render_md((s or "") + refs))
    env.filters["md_inline"] = lambda s: Markup(
        render_md_inline((s or "") + refs)
    )
    env.filters["fmt_date"] = fmt_date
    env.filters["strip_scheme"] = strip_scheme
    return env


def load_avatar(path):
    """Read image and return a data URI, or None if the file is
    missing. Embedding avoids relative-path issues between source and
    build dirs, and keeps the HTML self-contained.
    """
    import base64

    if not path.exists():
        return None
    ext = path.suffix.lstrip(".").lower() or "jpeg"
    mime = "jpeg" if ext in {"jpg", "jpeg"} else ext
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/{mime};base64,{data}"


def load_icons(path):
    icons = {}
    for f in sorted(path.glob("*.svg")):
        svg = f.read_text().replace("<svg ", '<svg aria-hidden="true" ', 1)
        icons[f.stem] = Markup(svg)
    return icons


def embed_fonts(css_text, base_dir):
    def repl(m):
        data = base64.b64encode((base_dir / m.group(1)).read_bytes()).decode()
        return f'url("data:font/woff2;base64,{data}")'

    return re.sub(r'url\("(fonts/[^"]+\.woff2)"\)', repl, css_text)


def main():
    data = load_yaml(YAML_PATH)
    links = data.get("links") or {}
    css_text = embed_fonts(Path(CSS_PATH).read_text(), Path(CSS_PATH).parent)
    avatar_uri = load_avatar(Path(TEMPLATE_PATH).parent / "me.jpg")
    icons = load_icons(Path(TEMPLATE_PATH).parent / "icons")

    template_path = Path(TEMPLATE_PATH)
    env = build_env(template_path.parent, links=links)
    template = env.get_template(template_path.name)

    html = template.render(
        css=Markup(css_text), avatar=avatar_uri, icons=icons, **data
    )
    Path(HTML_OUT).parent.mkdir(parents=True, exist_ok=True)
    Path(HTML_OUT).write_text(html)
    print(f"Wrote {HTML_OUT}", file=sys.stderr)

    if MAKE_PDF:
        # base_url lets weasyprint resolve any relative refs (images,
        # fonts) against the project directory.
        weasyprint.HTML(
            string=html, base_url=str(template_path.parent)
        ).write_pdf(PDF_OUT)
        print(f"Wrote {PDF_OUT}", file=sys.stderr)


if __name__ == "__main__":
    parse_cli()
    main()
