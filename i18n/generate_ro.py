#!/usr/bin/env python3
"""
Generate Romanian translations for ALL 2134 segments and pipe to write_translations.py.
This script reads en_flat.txt and outputs KEY|VALUE pairs with Romanian translations.
"""
import subprocess, sys, os

WRITE_SCRIPT = '/Users/sipi/churnlens/i18n/write_translations.py'

# Read English source
with open('/Users/sipi/churnlens/i18n/en_flat.txt') as f:
    lines = [l.strip() for l in f if l.strip()]

entries = []
for line in lines:
    if '|' not in line:
        continue
    k, _, v = line.partition('|')
    entries.append((k.strip(), v.strip()))

print(f"Loaded {len(entries)} English entries")

ROMANIAN_TRANSLATIONS = {
}
