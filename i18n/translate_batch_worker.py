#!/usr/bin/env python3
"""
Translate all input files in a batch directory and produce locale JSONs.
Usage: python3 i18n/translate_batch_worker.py <batch_dir> <output_base_dir>
Example: python3 i18n/translate_batch_worker.py /tmp/i18n_batches/batch_1 /Users/sipi/churnlens/i18n/locales

This is called by each subagent to translate ~10 languages.
"""
import os, json, sys, subprocess, time

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 translate_batch_worker.py <batch_dir> <output_base_dir>")
        sys.exit(1)
    
    batch_dir = sys.argv[1]
    output_base = sys.argv[2]
    
    # Find all input files
    input_files = sorted([f for f in os.listdir(batch_dir) if f.startswith('input_') and f.endswith('.txt')])
    
    if not input_files:
        print(f"No input files found in {batch_dir}")
        sys.exit(1)
    
    print(f"Found {len(input_files)} languages to translate in {batch_dir}")
    
    # Read the first input file to understand the format, then store it for reference
    # Actually read the English source from locales
    en_combined_path = os.path.join(output_base, "en", "_combined.json")
    if not os.path.exists(en_combined_path):
        print(f"ERROR: English source not found at {en_combined_path}")
        sys.exit(1)
    
    with open(en_combined_path, 'r', encoding='utf-8') as f:
        en_source = json.load(f)
    
    for input_file in input_files:
        lang_code = input_file.replace('input_', '').replace('.txt', '')
        input_path = os.path.join(batch_dir, input_file)
        output_dir = os.path.join(output_base, lang_code)
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"Translating: {lang_code}")
        print(f"Input: {input_path}")
        print(f"Output: {output_dir}")
        print(f"{'='*60}")
        
        # Read the input file to get all keys+English texts
        translations = {}
        current_page = None
        
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('## PAGE:'):
                    if line.startswith('## PAGE:'):
                        current_page = line.replace('## PAGE:', '').strip()
                    continue
                
                if '|' not in line:
                    continue
                    
                key, _, val = line.partition('|')
                key = key.strip()
                val = val.strip()
                if key and val:
                    translations[key] = val
        
        print(f"  Keys to translate: {len(translations)}")
        
        # Now translate each page's keys
        # Group keys by page for context
        page_keys = {}
        page_names = sorted(set(
            k.split('__TR_')[1].split('_')[0] if '__TR_' in k else ''
            for k in translations.keys()
        ))
        
        # Build translation data: for each page, collect keys + translations
        page_data = {}
        for key, val in translations.items():
            # Extract page name from key
            if '__TR_' in key:
                page_name = key.split('__TR_')[1].split('_')[0]
            else:
                page_name = "unknown"
            
            if page_name not in page_data:
                page_data[page_name] = {}
            page_data[page_name][key] = val
        
        # Translate page by page
        for page_name, keys_dict in sorted(page_data.items()):
            print(f"  Translating page: {page_name} ({len(keys_dict)} keys)")
            
            # Translate each key individually via prompt
            translated = {}
            batch_size = 20
            keys_list = list(keys_dict.items())
            
            for i in range(0, len(keys_list), batch_size):
                batch = keys_list[i:i+batch_size]
                batch_translated = translate_batch(batch, lang_code)
                translated.update(batch_translated)
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
            
            # Write per-page JSON
            page_out = os.path.join(output_dir, f"{page_name}.json")
            with open(page_out, 'w', encoding='utf-8') as f:
                json.dump(translated, f, indent=2, ensure_ascii=False)
            print(f"    -> {page_out} ({len(translated)} keys)")
        
        # Verify completeness
        total_translated = sum(len(os.listdir(output_dir)) for _ in [1])
        print(f"  Done: {lang_code}")
    
    # Write a completion marker
    with open(os.path.join(batch_dir, "_DONE"), 'w') as f:
        f.write(f"Completed at {time.ctime()}\n")
    
    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE: {len(input_files)} languages")

def translate_batch(batch, lang_code):
    """
    Translate a batch of (key, english_text) pairs to the target language.
    This function constructs a prompt and returns a dict of {key: translated_text}.
    """
    from translate_batch_kv import translate_key_value_batch
    return translate_key_value_batch(batch, lang_code)

if __name__ == "__main__":
    main()
