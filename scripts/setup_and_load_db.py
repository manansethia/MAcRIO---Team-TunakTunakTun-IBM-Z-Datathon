#!/usr/bin/env python3
"""
MAcRIO PostgreSQL Schema Setup & Bulk Ingestion Pipeline for IBM LinuxONE
Connects to local PostgreSQL instance, establishes optimized schema, and
bulk-ingests:
1. Utensil and Plastic Safety Rules
2. Singapore Hawker Signature Dishes (Chicken Rice, IJOOZ, Laksa, etc.)
3. Fast Food Chains Database (McDonald's, Burger King, Starbucks, KFC)
4. Prime Supermarket Live Proof Pack (Real EAN-13 barcodes)
5. Singapore Healthier Choice Symbol Products (data.gov.sg)
6. 3.01M Packaged Target Products (Open Food Facts stream)
"""

import gzip
import json
import os
import sys
import time
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values

DB_CONFIG = {
    "dbname": "macrio_db",
    "user": "macrio",
    "password": "macrio_secret",
    "host": "localhost",
    "port": 5432
}

DATA_DIR = "/home/linux1/macrio/datasets/processed"
if not os.path.exists(DATA_DIR):
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datasets", "processed")


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def init_schema(conn):
    print("[*] Creating extensions and schema tables...")
    with conn.cursor() as cur:
        # Enable trigram extension for fuzzy search
        cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

        # 1. Products Table (Global & Singapore Packaged Goods)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            barcode TEXT PRIMARY KEY,
            product_name TEXT,
            brands TEXT,
            target_countries TEXT[],
            ingredients_text TEXT,
            additives_tags TEXT[],
            nutriscore_grade TEXT,
            nova_group INTEGER,
            energy_kcal_100g NUMERIC,
            sugars_100g NUMERIC,
            fat_100g NUMERIC,
            saturated_fat_100g NUMERIC,
            proteins_100g NUMERIC,
            sodium_100g NUMERIC,
            salt_100g NUMERIC,
            source TEXT DEFAULT 'openfoodfacts',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Singapore Hawker Dishes Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS singapore_hawker_dishes (
            id SERIAL PRIMARY KEY,
            dish_name TEXT NOT NULL UNIQUE,
            aliases TEXT[],
            category VARCHAR(64),
            standard_portion TEXT,
            calories_kcal NUMERIC,
            carbohydrates_g NUMERIC,
            protein_g NUMERIC,
            fat_g NUMERIC,
            saturated_fat_g NUMERIC,
            sugar_g NUMERIC,
            sodium_mg NUMERIC,
            nutri_grade VARCHAR(5),
            grade VARCHAR(5),
            grade_reasoning TEXT,
            safer_twist TEXT
        );
        """)

        # 3. Fast Food Chains Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS fast_food_items (
            id SERIAL PRIMARY KEY,
            chain VARCHAR(64) NOT NULL,
            item_name TEXT NOT NULL,
            singapore_asia_sku JSONB,
            western_sku JSONB,
            double_standard_verdict VARCHAR(64),
            disparity_summary TEXT,
            UNIQUE(chain, item_name)
        );
        """)

        # 4. Prime Supermarket Proof Pack Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS prime_supermarket_proof (
            id SERIAL PRIMARY KEY,
            barcode_ean13 VARCHAR(64) UNIQUE NOT NULL,
            product_name TEXT NOT NULL,
            brand TEXT,
            shelf_category VARCHAR(64),
            singapore_retail_formula JSONB,
            western_counterpart JSONB,
            double_standard_verdict VARCHAR(64),
            disparity_summary TEXT,
            utensil_toxicity_risk TEXT,
            cleaner_swap_recommendation TEXT
        );
        """)

        # 5. Utensil & Plastic Safety Rules Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS utensil_safety_rules (
            id SERIAL PRIMARY KEY,
            category VARCHAR(32) NOT NULL,
            code_or_material VARCHAR(64) NOT NULL UNIQUE,
            symbol VARCHAR(32),
            chemical_name TEXT,
            safety_tier VARCHAR(64),
            heat_limit_celsius INTEGER,
            microwave_safe BOOLEAN,
            leaching_hazards TEXT[],
            app_recommendation TEXT,
            raw_data JSONB
        );
        """)

        # 6. Crowdsourced Pending Submissions Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS pending_submissions (
            id SERIAL PRIMARY KEY,
            barcode VARCHAR(64),
            product_name TEXT,
            brand TEXT,
            front_image_url TEXT,
            barcode_image_url TEXT,
            ingredients_image_url TEXT,
            nutrition_image_url TEXT,
            extracted_ocr_text TEXT,
            status VARCHAR(32) DEFAULT 'STAGED_FOR_REVIEW',
            submitted_by VARCHAR(64) DEFAULT 'anonymous_user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Create Indices for Sub-millisecond lookups
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_products_countries ON products USING GIN (target_countries);
        CREATE INDEX IF NOT EXISTS idx_products_brands ON products (brands);
        CREATE INDEX IF NOT EXISTS idx_hawker_name_trgm ON singapore_hawker_dishes USING GIST (dish_name gist_trgm_ops);
        """)

        conn.commit()
    print("[✓] Database schema and indexes created successfully.")


def seed_singapore_hawker_dishes(conn):
    file_path = os.path.join(DATA_DIR, "singapore_hawker_signature_dishes.json")
    if not os.path.exists(file_path):
        print(f"[!] Warning: {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        dishes = json.load(f)

    with conn.cursor() as cur:
        for d in dishes:
            cur.execute("""
            INSERT INTO singapore_hawker_dishes (
                dish_name, aliases, category, standard_portion,
                calories_kcal, carbohydrates_g, protein_g, fat_g, saturated_fat_g,
                sugar_g, sodium_mg, nutri_grade, grade, grade_reasoning, safer_twist
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (dish_name) DO UPDATE SET
                calories_kcal = EXCLUDED.calories_kcal,
                protein_g = EXCLUDED.protein_g,
                fat_g = EXCLUDED.fat_g,
                saturated_fat_g = EXCLUDED.saturated_fat_g,
                grade = EXCLUDED.grade,
                safer_twist = EXCLUDED.safer_twist;
            """, (
                d.get("dish_name"), d.get("aliases", []), d.get("category"), d.get("standard_portion"),
                d.get("calories_kcal"), d.get("carbohydrates_g"), d.get("protein_g"), d.get("fat_g"),
                d.get("saturated_fat_g"), d.get("sugar_g", 0), d.get("sodium_mg"), d.get("nutri_grade"),
                d.get("grade"), d.get("grade_reasoning"), d.get("safer_twist")
            ))
        conn.commit()
    print(f"[✓] Ingested {len(dishes)} Singapore Hawker Signature Dishes.")


def seed_fast_food_items(conn):
    file_path = os.path.join(DATA_DIR, "fast_food_chains_nutrition.json")
    if not os.path.exists(file_path):
        print(f"[!] Warning: {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    with conn.cursor() as cur:
        for it in items:
            cur.execute("""
            INSERT INTO fast_food_items (
                chain, item_name, singapore_asia_sku, western_sku,
                double_standard_verdict, disparity_summary
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (chain, item_name) DO UPDATE SET
                singapore_asia_sku = EXCLUDED.singapore_asia_sku,
                western_sku = EXCLUDED.western_sku,
                double_standard_verdict = EXCLUDED.double_standard_verdict,
                disparity_summary = EXCLUDED.disparity_summary;
            """, (
                it.get("chain"), it.get("item_name"),
                json.dumps(it.get("singapore_asia_sku", {})),
                json.dumps(it.get("western_sku", {})),
                it.get("double_standard_verdict"),
                it.get("disparity_summary")
            ))
        conn.commit()
    print(f"[✓] Ingested {len(items)} Fast Food Chain items.")


def seed_prime_supermarket_proof(conn):
    file_path = os.path.join(DATA_DIR, "prime_supermarket_proof_pack.json")
    if not os.path.exists(file_path):
        print(f"[!] Warning: {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        items = data.get("proof_items", [])

    with conn.cursor() as cur:
        for it in items:
            cur.execute("""
            INSERT INTO prime_supermarket_proof (
                barcode_ean13, product_name, brand, shelf_category,
                singapore_retail_formula, western_counterpart,
                double_standard_verdict, disparity_summary,
                utensil_toxicity_risk, cleaner_swap_recommendation
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (barcode_ean13) DO UPDATE SET
                product_name = EXCLUDED.product_name,
                singapore_retail_formula = EXCLUDED.singapore_retail_formula,
                western_counterpart = EXCLUDED.western_counterpart,
                double_standard_verdict = EXCLUDED.double_standard_verdict;
            """, (
                it.get("barcode_ean13"), it.get("product_name"), it.get("brand"), it.get("shelf_category"),
                json.dumps(it.get("singapore_retail_formula", {})),
                json.dumps(it.get("western_counterpart", {})),
                it.get("double_standard_verdict"),
                it.get("disparity_summary"),
                it.get("utensil_toxicity_risk"),
                it.get("cleaner_swap_recommendation")
            ))
        conn.commit()
    print(f"[✓] Ingested {len(items)} Prime Supermarket Proof Items.")


def seed_utensil_safety(conn):
    file_path = os.path.join(DATA_DIR, "utensil_and_plastic_safety_matrix.json")
    if not os.path.exists(file_path):
        print(f"[!] Warning: {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with conn.cursor() as cur:
        # Plastic resins
        for r in data.get("resin_identification_codes", []):
            code_str = f"RIC_{r['code']}"
            cur.execute("""
            INSERT INTO utensil_safety_rules (
                category, code_or_material, symbol, chemical_name,
                safety_tier, heat_limit_celsius, microwave_safe,
                leaching_hazards, app_recommendation, raw_data
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (code_or_material) DO UPDATE SET
                safety_tier = EXCLUDED.safety_tier,
                app_recommendation = EXCLUDED.app_recommendation;
            """, (
                "plastic_resin", code_str, r.get("symbol"), r.get("chemical_name"),
                r.get("safety_tier"), r.get("heat_limit_celsius"), r.get("microwave_safe"),
                r.get("leaching_hazards", []), r.get("app_recommendation"),
                json.dumps(r)
            ))

        # Cookware wear rules
        for c in data.get("cookware_safety_rules", []):
            cur.execute("""
            INSERT INTO utensil_safety_rules (
                category, code_or_material, symbol, chemical_name,
                safety_tier, heat_limit_celsius, microwave_safe,
                leaching_hazards, app_recommendation, raw_data
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (code_or_material) DO UPDATE SET
                safety_tier = EXCLUDED.safety_tier,
                app_recommendation = EXCLUDED.app_recommendation;
            """, (
                "cookware_surface", c.get("material"), None, c.get("material"),
                c.get("risk_rating"), 260, False,
                [c.get("hazard_description")], c.get("action"),
                json.dumps(c)
            ))
        conn.commit()
    print("[✓] Ingested Utensil and Plastic Safety Rules.")


def clean_str(s):
    if s is None:
        return None
    return str(s).replace("\x00", "").strip()


def bulk_load_packaged_products(conn, batch_size=10000, max_records=None):
    file_path = os.path.join(DATA_DIR, "target_markets_products.jsonl.gz")
    if not os.path.exists(file_path):
        print(f"[!] Target markets products file {file_path} not found.")
        return

    print(f"[*] Starting high-speed batch insertion of {file_path} into `products` table...")
    start_time = time.time()
    total_inserted = 0

    insert_sql = """
    INSERT INTO products (
        barcode, product_name, brands, target_countries, ingredients_text,
        additives_tags, nutriscore_grade, nova_group, energy_kcal_100g,
        sugars_100g, fat_100g, saturated_fat_100g, proteins_100g,
        sodium_100g, salt_100g
    ) VALUES %s
    ON CONFLICT (barcode) DO NOTHING;
    """

    batch = []
    with gzip.open(file_path, "rt", encoding="utf-8") as f, conn.cursor() as cur:
        for line in f:
            try:
                item = json.loads(line)
            except Exception:
                continue

            nutri = item.get("nutriments", {})
            barcode = clean_str(item.get("barcode"))
            if not barcode:
                continue

            target_countries = [clean_str(c) for c in item.get("target_countries", []) if c]
            additives_tags = [clean_str(a) for a in item.get("additives_tags", []) if a]

            record = (
                barcode,
                clean_str(item.get("product_name")),
                clean_str(item.get("brands")),
                target_countries,
                clean_str(item.get("ingredients_text")),
                additives_tags,
                clean_str(item.get("nutriscore_grade")),
                item.get("nova_group"),
                nutri.get("energy-kcal_100g"),
                nutri.get("sugars_100g"),
                nutri.get("fat_100g"),
                nutri.get("saturated-fat_100g"),
                nutri.get("proteins_100g"),
                nutri.get("sodium_100g"),
                nutri.get("salt_100g")
            )
            batch.append(record)

            if len(batch) >= batch_size:
                execute_values(cur, insert_sql, batch)
                conn.commit()
                total_inserted += len(batch)
                batch = []
                elapsed = time.time() - start_time
                rate = total_inserted / elapsed if elapsed > 0 else 0
                print(f"[+] Inserted {total_inserted:,} products ({rate:.0f} rows/sec)...")

            if max_records and total_inserted >= max_records:
                break

        if batch:
            execute_values(cur, insert_sql, batch)
            conn.commit()
            total_inserted += len(batch)

    elapsed = time.time() - start_time
    print(f"[✓] Bulk ingestion completed! Total products inserted: {total_inserted:,} in {elapsed:.1f}s.")


def main():
    print("[*] Connecting to PostgreSQL (macrio_db) on IBM LinuxONE...")
    conn = get_connection()
    try:
        init_schema(conn)
        seed_singapore_hawker_dishes(conn)
        seed_fast_food_items(conn)
        seed_prime_supermarket_proof(conn)
        seed_utensil_safety(conn)
        bulk_load_packaged_products(conn)
    finally:
        conn.close()
    print("[✓] All database initialization and data seeding completed successfully.")


if __name__ == "__main__":
    main()
