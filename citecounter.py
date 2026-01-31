# coding=utf-8
from collections import Counter
import re

# === CONFIGURE FILE PATHS ===
aux_file = "C:/Users/jmayhall/Downloads/masters_paper/amspaperV6.1.aux"     # your LaTeX .aux file
bib_file = "C:/Users/jmayhall/Downloads/masters_paper/references.bib"  # your BibTeX file

# === 1. Read the .aux file ===
with open(aux_file, 'r', encoding='utf-8') as f:
    aux_text = f.read()

# === 2. Extract all citation keys ===
keys = []

# Biblatex / Biber format: \abx@aux@cite{0}{key1,key2,...}
abx_matches = re.findall(r'\\abx@aux@cite\{[0-9]+\}\{([^}]*)\}', aux_text)
for m in abx_matches:
    keys.extend([k.strip() for k in m.split(',') if k.strip()])

# Classic BibTeX format: \citation{key1,key2,...}
bibtex_matches = re.findall(r'\\citation\{([^}]*)\}', aux_text)
for m in bibtex_matches:
    keys.extend([k.strip() for k in m.split(',') if k.strip()])

# Count occurrences
citation_counter = Counter(keys)

# === 3. Parse .bib file for all keys ===
with open(bib_file, 'r', encoding='utf-8') as f:
    bib_text = f.read()

# Match BibTeX entries: @article{key, ...}, @book{key, ...}, etc.
bib_keys = re.findall(r'@\w+\{([^,]+),', bib_text)
bib_keys = [k.strip() for k in bib_keys]

# === 4. Report ===
print("=== Citation Usage Report ===\n")

print("CITED ENTRIES:")
for key, count in citation_counter.most_common():
    print(f"{key}: {count} time(s) cited")

# Unused BibTeX entries
unused_keys = [k for k in bib_keys if k not in citation_counter]
if unused_keys:
    print("\nUNUSED BIBLIOGRAPHY ENTRIES:")
    for k in unused_keys:
        print(k)
else:
    print("\nAll BibTeX entries are cited.")
