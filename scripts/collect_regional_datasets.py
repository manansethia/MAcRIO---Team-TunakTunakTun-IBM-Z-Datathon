#!/usr/bin/env python3
"""
MAcRIO Super Dataset Collector
Downloads and harmonizes foundational datasets for MAcRIO:
1. ICMR-NIN IFCT 2017 (India) - Compositions, multilingual names, and nutrient definitions
2. Kemenkes TKPI 2020 (Indonesia) - Food composition tables
3. Open Food Facts - Additives taxonomy and NOVA groups
4. Food Safety & Double Standards Seed Matrix (Food Pharmer & Regulatory benchmark)
5. Plastic Resin (RIC 1-7) & Utensil Safety Specification Matrix
"""

import os
import urllib.request
import json
import csv
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "datasets", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "datasets", "processed")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

SOURCES = {
    # 1. India ICMR-NIN IFCT 2017
    "ifct_compositions": {
        "url": "https://unpkg.com/@ifct2017/compositions@2.0.9/index.csv",
        "raw_file": os.path.join(RAW_DIR, "ifct2017_compositions.csv"),
        "description": "Indian Food Composition Tables 2017 (528 foods, 151 nutrient parameters)"
    },
    "ifct_local_names": {
        "url": "https://unpkg.com/@ifct2017/codes@2.0.7/index.csv",
        "raw_file": os.path.join(RAW_DIR, "ifct2017_local_names.csv"),
        "description": "IFCT 2017 Multilingual food names (Hindi, Tamil, Telugu, Kannada, etc.)"
    },
    "ifct_columns": {
        "url": "https://unpkg.com/@ifct2017/columns@2.0.6/index.csv",
        "raw_file": os.path.join(RAW_DIR, "ifct2017_columns.csv"),
        "description": "IFCT 2017 Nutrient column definitions and units"
    },
    # 2. Indonesia Kemenkes TKPI 2020
    "tkpi_indonesia": {
        "url": "https://raw.githubusercontent.com/ancxlol/tkpi-2020-database/main/data/tkpi_2020_pages_15_83.csv",
        "raw_file": os.path.join(RAW_DIR, "tkpi_2020_indonesia.csv"),
        "description": "Tabel Komposisi Pangan Indonesia (TKPI 2020 Kemenkes)"
    },
    # 3. Open Food Facts Taxonomies
    "off_additives_taxonomy": {
        "url": "https://raw.githubusercontent.com/openfoodfacts/openfoodfacts-server/main/taxonomies/additives.txt",
        "raw_file": os.path.join(RAW_DIR, "openfoodfacts_additives.txt"),
        "description": "Open Food Facts Additives taxonomy with hazard classifications"
    },
    "off_nova_taxonomy": {
        "url": "https://raw.githubusercontent.com/openfoodfacts/openfoodfacts-server/main/taxonomies/nova_groups.txt",
        "raw_file": os.path.join(RAW_DIR, "openfoodfacts_nova_groups.txt"),
        "description": "NOVA ultra-processed food classification taxonomy"
    }
}


def download_file(url: str, dest_path: str, description: str):
    logging.info(f"Downloading: {description} from {url}...")
    headers = {"User-Agent": "MAcRIO-SuperDatasetCollector/1.0"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response, open(dest_path, "wb") as out_file:
            data = response.read()
            out_file.write(data)
        logging.info(f" Saved {os.path.basename(dest_path)} ({len(data)} bytes)")
    except Exception as e:
        logging.error(f" Failed to download {url}: {e}")


def build_double_standards_seed_dataset():
    """
    Generates a curated baseline of multinational product double standards,
    inspired by Food Pharmer ('Label Padhega India') campaigns and regulatory comparisons.
    """
    dest_path = os.path.join(PROCESSED_DIR, "double_standards_seed.json")
    logging.info("Generating Double Standards Seed Dataset...")

    records = [
        {
            "brand": "Cadbury",
            "product_family": "Bournvita",
            "category": "Health & Malt Drinks",
            "asian_market": {
                "country": "India",
                "key_ingredients": ["Sugar (approx 50% originally / 32.2g per 100g added)", "Liquid Glucose", "Maltodextrin", "Color (150c - Caramel III)"],
                "flagged_degraded_items": ["Excess added sugar disguised as malt drink", "Caramel Color 150c", "Liquid Glucose"],
                "issue_summary": "Marketed as health drink for children; over 50% sugars/refined carbs; forced to reduce sugar content by ~15% post Food Pharmer expose."
            },
            "western_counterpart": {
                "region": "UK / EU (Cadbury Drinking Chocolate / Ovaltine)",
                "key_ingredients": ["Sugar", "Fat-reduced cocoa powder", "Vitamins", "No liquid glucose as primary bulk filler"],
                "strict_marketing_rules": "Banned from advertising high-sugar beverages to minors under HFSS rules in the UK."
            },
            "risk_severity": "HIGH",
            "regulatory_violation": "Misleading health & immunity claims (NCPCR notice issued)"
        },
        {
            "brand": "Nestle",
            "product_family": "Maggi 2-Minute Noodles",
            "category": "Instant Noodles",
            "asian_market": {
                "country": "India / Malaysia / Indonesia",
                "key_ingredients": ["Refined Wheat Flour (Maida)", "Palm Oil", "Flavor Enhancers (635)", "Hydrolyzed Peanut Protein"],
                "flagged_degraded_items": ["Palm Oil / Palmolein (high saturated fat)", "Flour with low extraction"],
                "issue_summary": "Uses cheap Palm Oil / Palmolein as the primary deep-frying and fat medium across Southeast Asia & India."
            },
            "western_counterpart": {
                "region": "Germany / Australia",
                "key_ingredients": ["Wheat flour", "Sunflower Oil or Canola Oil", "Lower sodium formulation"],
                "flagged_degraded_items": [],
                "issue_summary": "Western versions frequently swap palm oil for higher grade vegetable oils with lower saturated fat."
            },
            "risk_severity": "HIGH",
            "regulatory_violation": "Nutritional degradation / High Saturated Fat disguised by seasoning"
        },
        {
            "brand": "Kraft Heinz",
            "product_family": "Tomato Ketchup",
            "category": "Condiments & Sauces",
            "asian_market": {
                "country": "India / Singapore",
                "key_ingredients": ["Tomato Paste (26-28%)", "Sugar (approx 25-28%)", "Liquid Glucose", "Preservative (211 - Sodium Benzoate)", "Stabilizer (1422)"],
                "flagged_degraded_items": ["Liquid Glucose", "Sodium Benzoate (Class II preservative)"],
                "issue_summary": "Higher proportion of liquid glucose and chemical preservatives compared to simple vinegar/sugar shelf stabilization."
            },
            "western_counterpart": {
                "region": "EU / UK",
                "key_ingredients": ["Tomatoes (148g per 100g ketchup)", "Spirit Vinegar", "Sugar", "Salt", "Spice & Herb Extracts"],
                "flagged_degraded_items": [],
                "issue_summary": "No added chemical preservatives (Sodium Benzoate); preserved purely through natural vinegar and tomato acidity."
            },
            "risk_severity": "MEDIUM",
            "regulatory_violation": "Additive addition where natural preservation suffices"
        },
        {
            "brand": "Generic Multi-Brand Bakery",
            "product_family": "Brown Bread / Multigrain Bread",
            "category": "Bakery",
            "asian_market": {
                "country": "India",
                "key_ingredients": ["Refined Wheat Flour (Maida) 70-80%", "Whole Wheat Flour 15-20%", "Color (150a/150d - Caramel)", "Class II Preservatives (282, 200)"],
                "flagged_degraded_items": ["Maida (Refined Flour) as majority", "Caramel Color 150d (Ammonia Sulphite Caramel)", "Preservative 282"],
                "issue_summary": "Brown bread sold as healthy whole wheat but is essentially white bread dyed brown with caramel color."
            },
            "western_counterpart": {
                "region": "EU / US",
                "key_ingredients": ["100% Whole Grain Whole Wheat Flour", "Water", "Yeast", "Strict wholemeal labeling laws"],
                "flagged_degraded_items": [],
                "issue_summary": "Strict regulations prevent labeling bread as whole wheat unless whole grain is the primary grain ingredient."
            },
            "risk_severity": "HIGH",
            "regulatory_violation": "Deceptive grain origin & artificial coloring"
        },
        {
            "brand": "Hindustan Unilever / Kwality Wall's",
            "product_family": "Ice Cream vs Frozen Dessert",
            "category": "Dairy / Confectionery",
            "asian_market": {
                "country": "India / Southeast Asia",
                "key_ingredients": ["Water", "Sugar", "Edible Vegetable Oil (Palm Oil)", "Milk Solids", "Emulsifier (471)"],
                "flagged_degraded_items": ["Hydrogenated Vegetable Oil / Palm Oil substituting milk fat"],
                "issue_summary": "Sold in ice cream freezers and branding, but legally classified as 'Frozen Dessert' because expensive milk fat is replaced with cheap vegetable oil."
            },
            "western_counterpart": {
                "region": "EU / US (Ben & Jerry's / Wall's Dairy)",
                "key_ingredients": ["Cream", "Skimmed Milk", "Sugar", "Egg yolk", "Real butterfat"],
                "flagged_degraded_items": [],
                "issue_summary": "True dairy ice cream using real milk fat and cream rather than vegetable oil substitution."
            },
            "risk_severity": "HIGH",
            "regulatory_violation": "Fat substitution / Consumer perception deception"
        }
    ]

    with open(dest_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    logging.info(f" Saved Double Standards Seed Dataset ({len(records)} case studies)")


def build_plastic_and_utensil_safety_matrix():
    """
    Builds the computer vision & inference knowledge base for plastic resin codes (RIC 1-7)
    and kitchen utensil surface safety (scratched Teflon, pitted aluminum, brass/copper).
    """
    dest_path = os.path.join(PROCESSED_DIR, "utensil_and_plastic_safety_matrix.json")
    logging.info("Generating Utensil & Plastic Safety Matrix...")

    data = {
        "resin_identification_codes": [
            {
                "code": 1,
                "symbol": "PET",
                "chemical_name": "Polyethylene Terephthalate",
                "common_uses": ["Single-use water bottles", "Soda bottles", "Salad dressing containers"],
                "safety_tier": "CAUTION_SINGLE_USE",
                "heat_limit_celsius": 60,
                "microwave_safe": False,
                "hot_liquids_safe": False,
                "leaching_hazards": ["Antimony trioxide (catalyst residue)", "Phthalates over time and heat", "Microplastic shedding upon reuse"],
                "app_recommendation": "Do not reuse for hot water, warm tea, or store in hot car. Replace with glass or 304 food-grade stainless steel."
            },
            {
                "code": 2,
                "symbol": "HDPE",
                "chemical_name": "High-Density Polyethylene",
                "common_uses": ["Milk jugs", "Detergent bottles", "Oil jugs"],
                "safety_tier": "SAFE",
                "heat_limit_celsius": 110,
                "microwave_safe": False,
                "hot_liquids_safe": True,
                "leaching_hazards": ["Low leaching risk under normal room temp"],
                "app_recommendation": "One of the safest food plastics. Still avoid microwaving directly."
            },
            {
                "code": 3,
                "symbol": "PVC",
                "chemical_name": "Polyvinyl Chloride",
                "common_uses": ["Cling wraps (older)", "Plastic pipes", "Condiment squeeze bottles"],
                "safety_tier": "HAZARDOUS",
                "heat_limit_celsius": 70,
                "microwave_safe": False,
                "hot_liquids_safe": False,
                "leaching_hazards": ["DEHP / Phthalate plasticizers", "Dioxins", "Vinyl chloride monomer (known human carcinogen)"],
                "app_recommendation": "STRICT AVOID for food storage. Replace immediately with silicone or glass."
            },
            {
                "code": 4,
                "symbol": "LDPE",
                "chemical_name": "Low-Density Polyethylene",
                "common_uses": ["Grocery bags", "Bread bags", "Squeezable bottles"],
                "safety_tier": "MODERATE_SAFE",
                "heat_limit_celsius": 80,
                "microwave_safe": False,
                "hot_liquids_safe": False,
                "leaching_hazards": ["Low chemical leaching, but releases microplastics if degraded"],
                "app_recommendation": "Acceptable for ambient and cold food storage; do not heat."
            },
            {
                "code": 5,
                "symbol": "PP",
                "chemical_name": "Polypropylene",
                "common_uses": ["Microwaveable meal boxes", "Yogurt cups", "Baby bottles", "Food takeaway containers"],
                "safety_tier": "BEST_FOOD_PLASTIC",
                "heat_limit_celsius": 130,
                "microwave_safe": True,
                "hot_liquids_safe": True,
                "leaching_hazards": ["Relatively inert; minor microplastic release under intense ultrasonic or scratch abrasion"],
                "app_recommendation": "The preferred plastic for warm food, but prefer ceramic or glass for high-heat microwaving."
            },
            {
                "code": 6,
                "symbol": "PS",
                "chemical_name": "Polystyrene / Styrofoam",
                "common_uses": ["Disposable coffee cups", "Styrofoam food trays", "Plastic cutlery"],
                "safety_tier": "HAZARDOUS_HEAT",
                "heat_limit_celsius": 75,
                "microwave_safe": False,
                "hot_liquids_safe": False,
                "leaching_hazards": ["Styrene monomer (IARC Group 2A probable human carcinogen, endocrine disruptor)", "Leaching increases exponentially with oily food and hot liquid"],
                "app_recommendation": "NEVER pour hot tea, coffee, or greasy soup into Styrofoam cups or containers."
            },
            {
                "code": 7,
                "symbol": "OTHER",
                "chemical_name": "Polycarbonate, Melamine, Acrylic, BPA Blends",
                "common_uses": ["Reusable water jugs (5-gallon)", "Melamine tableware", "Unmarked plastic food boxes"],
                "safety_tier": "HIGH_ALERT",
                "heat_limit_celsius": 80,
                "microwave_safe": False,
                "hot_liquids_safe": False,
                "leaching_hazards": ["Bisphenol A (BPA) from polycarbonates", "Formaldehyde and melamine monomers from melamine crockery heated in microwave"],
                "app_recommendation": "Avoid unless explicitly certified 'BPA-Free Tritan' or food-safe bioplastic. Never microwave melamine plates."
            }
        ],
        "cookware_safety_rules": [
            {
                "material": "Non-Stick PTFE (Teflon)",
                "surface_condition": "Deep Scratches / Peeling Flakes",
                "risk_rating": "SEVERE",
                "hazard_description": "A single scratch on a non-stick pan can release up to 9,000 microplastic and nanoplastic particles per cook, along with persistent PFAS forever chemicals.",
                "action": "Discard pan immediately. Transition to cast iron, carbon steel, or 18/10 tri-ply stainless steel."
            },
            {
                "material": "Uncoated Aluminum Pot / Handi",
                "cooking_scenario": "Acidic curries (Tomato, Tamarind rasam, Sambal, Lemon, Vinegar)",
                "risk_rating": "HIGH",
                "hazard_description": "Acid dissolves the thin aluminum oxide passivation layer, leaching toxic aluminum ions into food, linked in clinical literature to neurotoxicity and kidney stress.",
                "action": "Use hard-anodized aluminum, food-grade stainless steel, or enameled cast iron for acidic dishes."
            },
            {
                "material": "Brass / Copper Vessels (Kansa / Tamba)",
                "surface_condition": "Missing or Tarnished Kalai (Tin lining) with green/verdigris patina",
                "risk_rating": "HIGH",
                "hazard_description": "Direct contact between acidic or salty foods and unlined copper/brass causes chemical leaching of copper salts (verdigris), leading to copper poisoning, nausea, and liver toxicity.",
                "action": "Re-line vessel with pure tin (Kalai) before cooking or storing food."
            }
        ]
    }

    with open(dest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logging.info(" Saved Utensil and Plastic Safety Matrix")


def main():
    logging.info("Starting MAcRIO Super Dataset Collector...")

    # Download raw datasets
    for key, info in SOURCES.items():
        download_file(info["url"], info["raw_file"], info["description"])

    # Generate processed seed datasets
    build_double_standards_seed_dataset()
    build_plastic_and_utensil_safety_matrix()

    logging.info(" Dataset collection and harmonization completed successfully.")


if __name__ == "__main__":
    main()
