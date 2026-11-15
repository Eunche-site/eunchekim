# Eun Che Kim — website

Static website hosted free on GitHub Pages, edited through [Pages CMS](https://app.pagescms.org).

## Editing (no code)

1. Go to **https://app.pagescms.org** and sign in with GitHub
   (or click the name **Eun Che Kim** in the footer of any page except Home).
2. Open this repository.
3. Edit **Schedule**, **Videos**, **Photos** or **Home page**, then **Save**.
4. The website updates about 1–2 minutes later.

- **Schedule:** order doesn't matter; the site sorts by date and hides past concerts by itself.
  Tick *Hide from website* to keep a concert listed in the editor but invisible on the site.
- **Videos / Photos:** shown in the order of the list. Drag the items to reorder them.
- **Photos:** upload full-size files; they are shrunk automatically after saving.

## What lives where

| Path | What |
|---|---|
| `content/*.yml` | Schedule, videos, photos, home photo (what Pages CMS edits) |
| `templates/` | Page layouts — the Biography text is in `templates/biography.html` |
| `static/` | CSS, JavaScript, photos (`static/uploads/` = photos added in the editor) |
| `.pages.yml` | Editor configuration (which fields the editor shows) |
| `build.py` | Turns templates + content into the finished site |
| `.github/workflows/deploy.yml` | Shrinks photos, builds and publishes on every change, and once a day |

## Preview on your computer

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # first time only
.venv/bin/python build.py && .venv/bin/python -m http.server -d _site 8000
```

Then open http://localhost:8000 (avoid port 5000 on a Mac — AirPlay uses it).

## One-time GitHub setup

1. Push this folder to a new **public** repository on GitHub.
2. Repository → **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. At https://app.pagescms.org, sign in with GitHub and install the Pages CMS app on the repository.
4. Custom domain: Settings → Pages → *Custom domain*, then add the DNS records GitHub shows
   at your domain registrar, and tick *Enforce HTTPS*.
