# ISURLOG Docs — MkDocs migration

MkDocs + Material site replacing the GitHub Wiki as the home for ISURLOG documentation. **All 4 modules are fully migrated** (Use and Hardware, Firmware Development, Data Integration & APIs, Troubleshooting) — 30 pages total, plus an interactive Power Budget calculator not possible on the Wiki (which sanitizes out `<script>`/`<iframe>`).

The [GitHub Wiki](https://github.com/isurki-tecnica/isurlog-firmware/wiki) is no longer being updated as the primary source — decide whether to archive/redirect it once this site has been live for a while.

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
