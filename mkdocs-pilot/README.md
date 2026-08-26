# ISURLOG Docs — MkDocs pilot

A small, reduced trial of MkDocs + Material as an alternative home for the ISURLOG documentation, to test whether it's worth migrating away from the GitHub Wiki. Only 3 pages are migrated here (Home, 2. Sensor Connections, and a Power Budget calculator) — the real, current documentation is still the [GitHub Wiki](https://github.com/isurki-tecnica/isurlog-firmware/wiki), untouched by this experiment.

## Why this exists

The GitHub Wiki can't run JavaScript (it sanitizes `<script>`/`<iframe>` out of every page), so an interactive tool like the power budget calculator can't be embedded there directly. This pilot proves it can be embedded natively — same page, same site — in MkDocs.

## Preview locally

```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
mkdocs serve
```

Then open <http://127.0.0.1:8000>.

## Undoing this pilot

Nothing here affects the wiki or the rest of the repo. To remove it entirely: delete this `mkdocs-pilot/` folder, delete the `gh-pages` branch (if a deployment was made), and turn off GitHub Pages in the repo's Settings → Pages.
