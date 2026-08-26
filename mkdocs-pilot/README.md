# ISURLOG Docs — MkDocs migration

MkDocs + Material site replacing the GitHub Wiki as the home for ISURLOG documentation. **Use and Hardware (Module A)** is fully migrated here, plus an interactive Power Budget calculator. **Firmware Development, Data Integration & APIs, and Troubleshooting** are still on the [GitHub Wiki](https://github.com/isurki-tecnica/isurlog-firmware/wiki) and will move here in later batches — the wiki stays live and accurate until each module has fully moved.

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

## Reverting

Nothing here affects the wiki or the rest of the repo. To revert to the wiki-only setup: delete this `mkdocs-pilot/` folder, delete the `gh-pages` branch, and turn off GitHub Pages in the repo's Settings → Pages.
