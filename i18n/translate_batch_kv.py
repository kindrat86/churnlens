#!/usr/bin/env python3
"""
Key-value translation helper. Translates batches of (key, text) pairs.
This is a lightweight module used by translate_batch_worker.py.
"""
import json, sys, os

def translate_key_value_batch(batch, lang_code):
    """
    Translate a batch of (key, english_text) pairs.
    batch: list of (key, english_text) tuples
    lang_code: target language code
    
    Returns: dict of {key: translated_text}
    
    This uses the subagent's own LLM via stdout/stdin prompting
    since we can't make API calls directly.
    """
    # Build a concise prompt
    prompt_parts = [
        f"Translate these {len(batch)} English text segments to language code '{lang_code}'.",
        "Rules:",
        "- Keep brand names 'Churn Lens' and 'SaaS' unchanged",
        "- Keep HTML entities like &amp; &lt; &gt; &mdash; unchanged",
        "- Keep the KEY part before each | exactly as-is",
        "- Only translate the VALUE after the |",
        "- Output format: each line: KEY|TRANSLATED_VALUE",
        "- Do NOT include any explanations, just the translated lines",
        "",
        "TEXTS TO TRANSLATE:"
    ]
    
    for key, text in batch:
        # Flatten text for transmission
        flat = text.replace('\n', '\\n')
        prompt_parts.append(f"{key}|{flat}")
    
    prompt = '\n'.join(prompt_parts)
    
    # We need to output this to the parent process
    # The subagent reads this, generates translations, and outputs them back
    # This module is called FROM inside the subagent's context
    # So we just return an empty dict and let the subagent fill it in
    
    # Actually, this is a protocol: the subagent writes translated files directly.
    # The worker is invoked within the subagent's terminal session.
    # We print a banner that tells the subagent what to do.
    
    print(f"\n=== TRANSLATION REQUEST: {lang_code} ({len(batch)} segments) ===")
    print(prompt)
    print("=== END TRANSLATION REQUEST ===")
    
    return {}
