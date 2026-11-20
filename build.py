"""Build the static website into _site/.

Content lives in content/*.yml (edited through Pages CMS at app.pagescms.org, or by hand);
page layouts live in templates/. GitHub Actions runs this on every change.

Local preview:
    python build.py && python -m http.server -d _site 8000
"""
import datetime as dt
import hashlib
import os
import re
import shutil
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_site"
BASE = os.environ.get("BASE_PATH", "").rstrip("/")      # e.g. "/eunchekim" on a github.io project site
SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")   # e.g. "https://eunchekim.com"
EDITOR_URL = "https://app.pagescms.org"

PAGES = {"home": "", "biography": "biography/", "concerts": "concerts/", "media": "media/", "contact": "contact/"}
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def load(name):
    return yaml.safe_load((ROOT / "content" / f"{name}.yml").read_text(encoding="utf-8")) or []


def url_for(endpoint, filename=None, _external=False):
    """Mimics Flask's url_for so the templates stay simple."""
    if endpoint == "login":
        return EDITOR_URL
    path = BASE + ("/static/" + filename if endpoint == "static" else "/" + PAGES[endpoint])
    if endpoint == "static" and filename.startswith("assets/"):
        # Cache-busting: a new file version gets a new URL, so phones never keep stale CSS/JS
        path += "?v=" + hashlib.md5((ROOT / "static" / filename).read_bytes()).hexdigest()[:8]
    return SITE_URL + path if _external and SITE_URL else path


def asset(path):
    """Prefix site-relative media paths (as stored by Pages CMS) with the base path."""
    path = str(path or "")
    return path if path.startswith(("http://", "https://")) else BASE + "/" + path.lstrip("/")


def iso(value):
    return str(value)[:10]


def concert_date(value):
    y, m, d = map(int, iso(value).split("-"))
    return f"{MONTHS[m - 1]} {d}, {y}"


YOUTUBE_ID = re.compile(r"(?:youtu\.be/|v=|/embed/|/shorts/|/live/)([A-Za-z0-9_-]{11})")


def youtube_id(text):
    text = str(text or "").strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", text):
        return text
    m = YOUTUBE_ID.search(text)
    if not m:
        raise SystemExit(f"Not a YouTube link in content/videos.yml: {text!r}")
    return m.group(1)


def paragraphs(text):
    """Split text into paragraphs at empty lines; single line breaks are joined with a space."""
    blocks = re.split(r"\n\s*\n", str(text or "").strip())
    return [" ".join(line.strip() for line in b.splitlines()) for b in blocks if b.strip()]


def visible(items):
    return [x for x in items if x and not x.get("hidden")]


def main():
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=True)
    env.globals.update(url_for=url_for)
    env.filters.update(asset=asset, concert_date=concert_date, iso=iso, paragraphs=paragraphs)

    settings = load("settings")
    today = dt.date.today().isoformat()
    concerts = sorted((x for x in visible(load("concerts")) if iso(x["date"]) >= today), key=lambda x: iso(x["date"]))
    videos = [dict(v, youtube=youtube_id(v.get("youtube"))) for v in visible(load("videos"))]
    photos = [p for p in visible(load("photos")) if p.get("image")]

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT / "static", ignore=shutil.ignore_patterns(".gitkeep"))
    shutil.copy(ROOT / "static" / "favicon.ico", OUT / "favicon.ico")  # crawlers also look at /favicon.ico

    context = {
        "home": dict(c=settings),
        "biography": dict(bio=load("biography")),
        "concerts": dict(concerts=concerts),
        "media": dict(videos=videos, photos=photos),
        "contact": {},
    }
    for page, extra in context.items():
        html = env.get_template("index.html" if page == "home" else f"{page}.html").render(page=page, **extra)
        target = OUT / PAGES[page] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
    (OUT / "404.html").write_text(env.get_template("404.html").render(page="notfound"), encoding="utf-8")
    (OUT / ".nojekyll").touch()
    if SITE_URL:  # help search engines find every page
        urls = "".join(f"<url><loc>{url_for(p, _external=True)}</loc><lastmod>{today}</lastmod></url>" for p in PAGES)
        (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                         f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
        (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}{BASE}/sitemap.xml\n")
    print(f"Built {len(context)} pages into {OUT} "
          f"({len(concerts)} upcoming concerts, {len(videos)} videos, {len(photos)} photos)")


if __name__ == "__main__":
    main()
