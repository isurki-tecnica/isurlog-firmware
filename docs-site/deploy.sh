#!/usr/bin/env bash
# Deploy docs-site + blog to GitHub Pages (gh-pages branch).
#
# Two separate mkdocs builds, merged into one output, because the Blog
# plugin and the i18n plugin conflict when run in the same build (the i18n
# plugin creates fresh File objects in on_files, so the Blog plugin's later
# on_nav mutation that marks posts as visible never reaches the real file
# object — posts silently disappear from the built site). Building the blog
# separately, without i18n, sidesteps this entirely.
set -euo pipefail
cd "$(dirname "$0")"

echo "== Building main site (docs + i18n) =="
./venv/Scripts/mkdocs.exe build --strict

echo "== Building blog (separate, no i18n) =="
./venv/Scripts/mkdocs.exe build -f mkdocs-blog.yml --strict

echo "== Merging blog into site/blog/ =="
rm -rf site/blog
mkdir -p site/blog
cp -r blog-site/* site/blog/

echo "== Publishing site/ to gh-pages =="
./venv/Scripts/ghp-import.exe -f -p -b gh-pages site

echo "Done. Should be live shortly at https://docs.isurlog.isurki.com/"
