#!/usr/bin/env python3
"""
test_convert_epub.py — Bypass Calibre for EPUB input (EPUB is already a ZIP with HTML).
Uses convert.py's HTML→Markdown→chunk pipeline directly.
"""
import sys, os, zipfile, shutil, glob

# Add scripts directory to path
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from convert import convert_html_to_markdown, split_markdown_structured, create_config_file
from manifest import create_manifest, file_hash

EPUB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "The House on Mango Street.epub")
TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "The House on Mango Street_temp")
EXTRACT_DIR = TEMP_DIR + "_extract"

# 1. Extract EPUB (it's a ZIP)
print("=== Step 1: Extract EPUB ===")
if os.path.exists(EXTRACT_DIR):
    shutil.rmtree(EXTRACT_DIR)
with zipfile.ZipFile(EPUB_PATH, 'r') as z:
    z.extractall(EXTRACT_DIR)
print(f"Extracted to: {EXTRACT_DIR}")

# Find all HTML/XHTML files, sorted by name
html_files = []
for root, dirs, files in os.walk(EXTRACT_DIR):
    for f in files:
        if f.lower().endswith(('.html', '.xhtml', '.htm')) and f.lower() != 'nav.xhtml':
            html_files.append(os.path.join(root, f))
html_files.sort()
print(f"Found {len(html_files)} HTML files")

# Read and concatenate HTML content
html_content = "<html><head><meta charset='UTF-8'></head><body>\n"
for hf in html_files:
    with open(hf, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    # Extract body content
    import re
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
    if body_match:
        html_content += body_match.group(1) + "\n<hr>\n"
    else:
        html_content += content + "\n<hr>\n"
html_content += "</body></html>"

# Write combined HTML
os.makedirs(TEMP_DIR, exist_ok=True)
input_html = os.path.join(TEMP_DIR, "input.html")
with open(input_html, 'w', encoding='utf-8') as f:
    f.write(html_content)
print(f"Combined HTML: {input_html} ({len(html_content)} chars)")

# Copy images if any
for root, dirs, files in os.walk(EXTRACT_DIR):
    for d in dirs:
        if d.lower() in ['images', 'image', 'media']:
            src = os.path.join(root, d)
            dst = os.path.join(TEMP_DIR, "images")
            if not os.path.exists(dst) and os.path.exists(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
                print(f"Copied images: {src} -> {dst}")

# 2. Convert HTML to Markdown
print("\n=== Step 2: HTML → Markdown ===")
input_md = os.path.join(TEMP_DIR, "input.md")
if not convert_html_to_markdown(input_html, input_md):
    print("ERROR: HTML to Markdown conversion failed")
    sys.exit(1)
with open(input_md, 'r', encoding='utf-8') as f:
    md_content = f.read()
print(f"Markdown: {len(md_content)} chars")

# 3. Split into chunks
print("\n=== Step 3: Split into chunks ===")
chunk_files = split_markdown_structured(input_md, TEMP_DIR)
print(f"Created {len(chunk_files)} chunks")

# 4. Create manifest
create_manifest(TEMP_DIR, chunk_files, input_md)

# 5. Create config file
create_config_file(TEMP_DIR, EPUB_PATH, "en", "zh", {"title": "The House on Mango Street"})

# Write source fingerprint
import json
fingerprint = {
    "path": os.path.realpath(EPUB_PATH),
    "size": os.path.getsize(EPUB_PATH),
    "sha256": file_hash(EPUB_PATH),
}
with open(os.path.join(TEMP_DIR, "source_fingerprint.json"), 'w', encoding='utf-8') as f:
    json.dump(fingerprint, f, indent=2, sort_keys=True)

# Clean up extract dir
shutil.rmtree(EXTRACT_DIR, ignore_errors=True)

print(f"\n=== Done! {len(chunk_files)} chunks in {TEMP_DIR} ===")
for cf in chunk_files:
    fp = os.path.join(TEMP_DIR, cf)
    print(f"  {cf}: {os.path.getsize(fp)} bytes")
