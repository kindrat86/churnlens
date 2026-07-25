#!/usr/bin/env python3
"""Fail if an internal working doc would be served publicly.

Why this exists: on 2026-07-25 eleven internal Markdown files were being served
200 and were crawlable, among them QA-SECURITY-SPEED-AUDIT-2026-07-19.md — a
report enumerating this site's own security weaknesses — plus CLAUDE.md and the
HERMES task/report files (unpublished go-to-market strategy). `.vercelignore`
already excluded `*.py` and `scripts/`; nothing excluded `*.md`.

This repo IS the deploy root (outputDirectory ".", buildCommand null), so any
tracked file not matched by .vercelignore is a live URL. That makes "did I
remember to ignore it" a release-blocking question, not a style question.

Policy: every tracked .md / .csv must be either matched by .vercelignore or on
the PUBLIC_ALLOWLIST below. New docs default to private — the failure mode we
want is a red build, not a silent leak.
"""
import fnmatch
import subprocess
import sys

# Files deliberately served to the public. Anything not here must be ignored.
PUBLIC_ALLOWLIST = {
    "agents.md",                      # AI-agent discovery, same role as llms.txt
    ".well-known/agents.md",          # ditto, well-known location
    "saas-churn-benchmarks-2026.csv",  # published dataset, linked from /benchmarks
}


def ignore_patterns(path=".vercelignore"):
    try:
        with open(path, encoding="utf-8") as fh:
            return [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    except FileNotFoundError:
        print(f"[check_public_docs] FAIL: {path} not found", file=sys.stderr)
        sys.exit(1)


def is_ignored(rel, patterns):
    base = rel.split("/")[-1]
    for p in patterns:
        if p.endswith("/") and (rel.startswith(p) or rel.startswith(p.rstrip("/") + "/")):
            return p
        if fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(base, p):
            return p
    return None


def main():
    tracked = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, check=True
    ).stdout.split()
    docs = [f for f in tracked if f.lower().endswith((".md", ".csv"))]
    patterns = ignore_patterns()

    leaked = [
        d for d in docs
        if d not in PUBLIC_ALLOWLIST and not is_ignored(d, patterns)
    ]

    print(f"[check_public_docs] {len(docs)} tracked doc(s); "
          f"{len(PUBLIC_ALLOWLIST)} allowlisted public")
    if leaked:
        print(f"[check_public_docs] FAIL: {len(leaked)} internal doc(s) would be "
              f"served publicly:", file=sys.stderr)
        for d in leaked:
            print(f"  https://churnlens.site/{d}", file=sys.stderr)
        print("\nFix: add a pattern to .vercelignore, or — only if the file is "
              "genuinely meant to be public — add it to PUBLIC_ALLOWLIST in "
              "scripts/check_public_docs.py.", file=sys.stderr)
        return 1

    print("[check_public_docs] OK — no internal docs exposed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
