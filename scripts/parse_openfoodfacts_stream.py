#!/usr/bin/env python3
"""
MAcRIO Open Food Facts Streaming Parser for s390x (IBM LinuxONE)
Efficiently streams through `openfoodfacts-products.jsonl.gz` (or `cts.jsonl.gz`)
without loading the full file into memory.

Filters specifically for target markets:
- Asian Markets: India, Singapore, Malaysia, Indonesia
- Western Benchmarks: United States, Canada, United Kingdom, France, Germany

Extracts minimal required schema for fast cross-border matching:
- barcode (code)
- product_name
- brands
- countries_tags
- ingredients_text
- additives_tags
- nutriscore_grade
- nova_group
- key nutriments per 100g (energy, sugar, fat, saturated fat, protein, salt/sodium)
"""

import gzip
import json
import os
import sys
import time

TARGET_COUNTRIES = {
    # Asia Priority Markets
    "en:india", "en:singapore", "en:malaysia", "en:indonesia",
    # Western Reference Benchmarks for Double-Standard Comparison
    "en:united-states", "en:canada", "en:united-kingdom", "en:france", "en:germany"
}

KEY_NUTRIMENTS = [
    "energy-kcal_100g", "sugars_100g", "fat_100g",
    "saturated-fat_100g", "proteins_100g", "salt_100g", "sodium_100g"
]


def extract_product_record(item: dict):
    countries_tags = set(item.get("countries_tags", []))
    matched_countries = countries_tags.intersection(TARGET_COUNTRIES)

    if not matched_countries:
        return None

    code = item.get("code")
    if not code:
        return None

    raw_nutriments = item.get("nutriments", {})
    clean_nutriments = {}
    for k in KEY_NUTRIMENTS:
        if k in raw_nutriments and raw_nutriments[k] is not None:
            try:
                clean_nutriments[k] = float(raw_nutriments[k])
            except (ValueError, TypeError):
                pass

    return {
        "barcode": str(code).strip(),
        "product_name": item.get("product_name", "").strip(),
        "brands": item.get("brands", "").strip(),
        "categories_tags": item.get("categories_tags", []),
        "target_countries": list(matched_countries),
        "ingredients_text": item.get("ingredients_text", ""),
        "additives_tags": item.get("additives_tags", []),
        "nutriscore_grade": item.get("nutriscore_grade", ""),
        "nova_group": item.get("nova_group"),
        "nutriments": clean_nutriments
    }


def stream_parse(input_filepath: str, output_filepath: str, limit: int = None):
    print(f"[*] Starting streaming parse of {input_filepath}...")
    start_time = time.time()
    total_scanned = 0
    total_matched = 0

    open_func = gzip.open if input_filepath.endswith(".gz") else open

    with open_func(input_filepath, "rt", encoding="utf-8", errors="ignore") as in_f, \
         gzip.open(output_filepath, "wt", encoding="utf-8") as out_f:

        for line in in_f:
            total_scanned += 1
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            extracted = extract_product_record(record)
            if extracted:
                total_matched += 1
                out_f.write(json.dumps(extracted, ensure_ascii=False) + "\n")

            if total_scanned % 100000 == 0:
                elapsed = time.time() - start_time
                rate = total_scanned / elapsed if elapsed > 0 else 0
                print(f"[+] Scanned: {total_scanned:,} | Matched Target Markets: {total_matched:,} ({rate:.0f} lines/sec)")

            if limit and total_matched >= limit:
                print(f"[*] Reached limit of {limit:,} matched records.")
                break

    elapsed = time.time() - start_time
    print(f"[✓] Finished! Total lines scanned: {total_scanned:,} | Total matched: {total_matched:,} in {elapsed:.1f}s")
    print(f"[✓] Output saved to: {output_filepath}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 parse_openfoodfacts_stream.py <path_to_jsonl_or_gz> [output_path]")
        sys.exit(1)

    in_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else "filtered_target_products.jsonl.gz"

    if not os.path.exists(in_path):
        print(f"Error: Input file {in_path} does not exist.")
        sys.exit(1)

    stream_parse(in_path, out_path)
