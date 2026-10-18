#!/usr/bin/env python3
"""
MAcRIO Singapore Hawker Signatures & Fast Food Chains Knowledge Base
Generates:
1. `singapore_hawker_signature_dishes.json`: Signature SG hawker dishes & drinks with macros,
   Nutri-Grade, health ratings (A-F & X), and safer local twists.
2. `fast_food_chains_nutrition.json`: Key menu items for McDonald's, Burger King, Starbucks, KFC,
   with cross-border double standards and A-F/X ratings.
"""

import json
import os

HAWKER_DISHES = [
    {
        "dish_name": "Hainanese Chicken Rice (Steamed)",
        "aliases": ["Chicken Rice", "Bai Ji Fan"],
        "category": "Hawker Main",
        "standard_portion": "1 plate (~350g)",
        "calories_kcal": 610,
        "carbohydrates_g": 72.0,
        "protein_g": 28.0,
        "fat_g": 24.0,
        "saturated_fat_g": 7.0,
        "sodium_mg": 980,
        "grade": "B",
        "grade_reasoning": "High protein, but rice is infused with chicken fat and sesame oil; high sodium in chilli/ginger sauce.",
        "safer_twist": "Ask for breast meat without skin, request less rice or plain steamed rice, go light on dark sweet sauce."
    },
    {
        "dish_name": "IJOOZ Fresh Squeezed Orange Juice",
        "aliases": ["IJOOZ", "Fresh Orange Juice Vending Machine"],
        "category": "Vending & Drinks",
        "standard_portion": "1 cup (280ml, ~4 freshly pressed oranges)",
        "calories_kcal": 115,
        "carbohydrates_g": 26.0,
        "protein_g": 2.0,
        "fat_g": 0.4,
        "saturated_fat_g": 0.0,
        "sugar_g": 22.0,
        "sodium_mg": 5,
        "nutri_grade": "C",
        "grade": "C",
        "grade_reasoning": "100% natural pure orange juice without added preservatives or cane sugar. However, because juicing removes dietary pulp/fiber, sugar concentration (>7.5g/100ml) causes rapid blood glucose spikes, earning Nutri-Grade C under SFA/HPB guidelines.",
        "safer_twist": "Drink slowly after a protein/fiber meal, or opt for whole fruit to retain digestive pectin and fiber."
    },
    {
        "dish_name": "Char Kway Teow",
        "aliases": ["Fried Kway Teow", "CKT"],
        "category": "Hawker Main",
        "standard_portion": "1 plate (~380g)",
        "calories_kcal": 745,
        "carbohydrates_g": 84.0,
        "protein_g": 22.0,
        "fat_g": 38.0,
        "saturated_fat_g": 14.5,
        "sodium_mg": 1450,
        "grade": "E",
        "grade_reasoning": "High glycemic flat rice noodles stir-fried in pork lard, sweet dark soy sauce, lap cheong (preserved sausage with nitrites), and cockles. Very high saturated fat and sodium.",
        "safer_twist": "Ask for less oil, no pork lard (chu yew char), less sweet black sauce, and extra bean sprouts for fiber."
    },
    {
        "dish_name": "Katong Laksa",
        "aliases": ["Nyonya Laksa", "Curry Laksa"],
        "category": "Hawker Soup & Noodles",
        "standard_portion": "1 bowl (~450g with soup)",
        "calories_kcal": 590,
        "carbohydrates_g": 62.0,
        "protein_g": 21.0,
        "fat_g": 32.0,
        "saturated_fat_g": 18.0,
        "sodium_mg": 1650,
        "grade": "D",
        "grade_reasoning": "Rich coconut milk broth delivers nearly an entire day's recommended limit of saturated fat (18g). Very high sodium.",
        "safer_twist": "Enjoy the noodles, prawns, and fishcake, but avoid drinking the rich coconut milk soup to the bottom."
    },
    {
        "dish_name": "Fish Soup Bee Hoon (Sliced Fish, Clear Soup)",
        "aliases": ["Sliced Fish Soup", "Yu Pian Tang"],
        "category": "Hawker Soup & Noodles",
        "standard_portion": "1 bowl (~400g)",
        "calories_kcal": 350,
        "carbohydrates_g": 45.0,
        "protein_g": 26.0,
        "fat_g": 6.0,
        "saturated_fat_g": 1.2,
        "sodium_mg": 820,
        "grade": "A",
        "grade_reasoning": "One of the cleanest hawker meals in Singapore. Lean protein (Batang / snakehead fish slices), bittergourd, choy sum, and clear broth.",
        "safer_twist": "Choose clear soup instead of evaporated milk soup; choose sliced fresh fish over deep-fried battered fish."
    },
    {
        "dish_name": "Roti Prata (2 Plain Pieces) with Curry",
        "aliases": ["Roti Canai", "Prata"],
        "category": "Indian-Muslim Hawker",
        "standard_portion": "2 pieces with small bowl dhal/curry (~200g)",
        "calories_kcal": 490,
        "carbohydrates_g": 58.0,
        "protein_g": 10.0,
        "fat_g": 26.0,
        "saturated_fat_g": 11.0,
        "sodium_mg": 780,
        "grade": "D",
        "grade_reasoning": "Made from refined flour stretched with ghee/margarine (potential industrial trans fat or high saturated palm fat), pan-fried.",
        "safer_twist": "Order Chapati or Tosai (Thosai) instead, which are made with wholemeal flour/fermented lentil batter with minimal oil."
    },
    {
        "dish_name": "Nasi Lemak with Fried Chicken Wing",
        "aliases": ["Nasi Lemak"],
        "category": "Malay / Hawker Classic",
        "standard_portion": "1 set (~380g)",
        "calories_kcal": 680,
        "carbohydrates_g": 72.0,
        "protein_g": 24.0,
        "fat_g": 36.0,
        "saturated_fat_g": 15.0,
        "sodium_mg": 1150,
        "grade": "D",
        "grade_reasoning": "Rice cooked in rich coconut milk and pandan; deep-fried chicken wing; sweet oily sambal chilli.",
        "safer_twist": "Swap fried chicken wing for boiled egg or grilled fish; ask for less sambal."
    },
    {
        "dish_name": "Kaya Toast with 2 Soft-Boiled Eggs & Kopi-O Kosong",
        "aliases": ["Traditional Singapore Breakfast"],
        "category": "Breakfast & Coffee Shop",
        "standard_portion": "2 thin toasts with kaya + butter, 2 eggs, 1 black coffee",
        "calories_kcal": 360,
        "carbohydrates_g": 40.0,
        "protein_g": 15.0,
        "fat_g": 16.0,
        "saturated_fat_g": 7.5,
        "sodium_mg": 380,
        "grade": "B",
        "grade_reasoning": "Eggs provide high-quality bioavailable protein and choline. Toast has refined sugar (kaya jam) and butter slab.",
        "safer_twist": "Order Kopi-O Kosong (zero sugar, zero milk) or Teh-C Siew Dai (less sugar with evaporated milk instead of condensed milk); ask for less butter."
    },
    {
        "dish_name": "Chendol",
        "aliases": ["Cendol"],
        "category": "Hawker Dessert",
        "standard_portion": "1 bowl (~250g)",
        "calories_kcal": 390,
        "carbohydrates_g": 62.0,
        "protein_g": 3.0,
        "fat_g": 16.0,
        "saturated_fat_g": 12.0,
        "sodium_mg": 110,
        "grade": "E",
        "grade_reasoning": "Concentrated saturated fat from coconut milk combined with heavy Gula Melaka (palm sugar syrup). Fast blood sugar surge.",
        "safer_twist": "Request less coconut milk and half Gula Melaka syrup, or choose Fresh Fruit Slices."
    },
    {
        "dish_name": "Sugarcane Juice with Lemon",
        "aliases": ["Fresh Sugarcane"],
        "category": "Hawker Drinks",
        "standard_portion": "1 large cup (400ml)",
        "calories_kcal": 190,
        "carbohydrates_g": 48.0,
        "sugar_g": 46.0,
        "protein_g": 0.5,
        "fat_g": 0.1,
        "sodium_mg": 15,
        "nutri_grade": "D",
        "grade": "D",
        "grade_reasoning": "Contains ~11 teaspoons of free sugar in liquid form with negligible fiber. Extreme glycemic index.",
        "safer_twist": "Drink Fresh Coconut Water (Nutri-Grade B) or Watermelon Juice with no added syrup."
    }
]

FAST_FOOD_CHAINS = [
    {
        "chain": "McDonald's",
        "item_name": "French Fries (Medium)",
        "singapore_asia_sku": {
            "frying_medium": "Palm Olein / Hydrogenated Vegetable Oil Blend",
            "calories_kcal": 340,
            "saturated_fat_g": 4.5,
            "additives": ["Dextrose", "Sodium Acid Pyrophosphate (450)", "Antifoaming Agent (900a)"],
            "grade": "D"
        },
        "western_sku": {
            "region": "United Kingdom / EU",
            "frying_medium": "High-Oleic Sunflower and Rapeseed Oil",
            "saturated_fat_g": 1.8,
            "grade": "C"
        },
        "double_standard_verdict": "DEGRADED_OIL",
        "disparity_summary": "Uses high saturated fat Palm Olein blend in Asian outlets; UK/EU uses cold-pressed high-oleic sunflower/rapeseed oil with less than half the saturated fat."
    },
    {
        "chain": "McDonald's",
        "item_name": "Big Mac",
        "singapore_asia_sku": {
            "calories_kcal": 510,
            "protein_g": 26.0,
            "saturated_fat_g": 10.0,
            "sodium_mg": 920,
            "grade": "D"
        },
        "western_sku": {
            "region": "United States",
            "calories_kcal": 590,
            "protein_g": 25.0,
            "saturated_fat_g": 11.0,
            "sodium_mg": 1050,
            "grade": "D"
        },
        "double_standard_verdict": "SIMILAR",
        "disparity_summary": "Comparable beef formulation; Singapore portion size is slightly smaller resulting in slightly lower sodium."
    },
    {
        "chain": "Burger King",
        "item_name": "Whopper",
        "singapore_asia_sku": {
            "calories_kcal": 640,
            "protein_g": 28.0,
            "saturated_fat_g": 12.0,
            "sodium_mg": 1020,
            "grade": "D"
        },
        "western_sku": {
            "region": "United States",
            "calories_kcal": 670,
            "sodium_mg": 1200,
            "grade": "D"
        },
        "double_standard_verdict": "SLIGHT_DISPARITY",
        "disparity_summary": "Flame-broiled beef patty; Singapore mayonnaise uses vegetable/palm oil blend vs soybean oil in US."
    },
    {
        "chain": "Starbucks",
        "item_name": "Caramel Macchiato (Tall / Whole Milk)",
        "singapore_asia_sku": {
            "calories_kcal": 210,
            "sugar_g": 28.0,
            "nutri_grade": "C",
            "grade": "C",
            "syrup_ingredients": ["Sugar", "Water", "Natural and Artificial Flavors", "Preservative: Potassium Sorbate (202)", "Citric Acid (330)"]
        },
        "western_sku": {
            "region": "United States",
            "calories_kcal": 200,
            "sugar_g": 25.0,
            "grade": "C"
        },
        "double_standard_verdict": "HIGH_SUGAR_BURDEN",
        "disparity_summary": "Contains ~7 teaspoons of liquid sugar; Nutri-Grade C under Singapore regulations. Recommends swap to Americano with a splash of oat milk (Nutri-Grade A)."
    },
    {
        "chain": "KFC",
        "item_name": "Original Recipe Chicken (1 Drumstick + 1 Thigh)",
        "singapore_asia_sku": {
            "frying_medium": "Palm Oil / Palmolein",
            "calories_kcal": 540,
            "saturated_fat_g": 13.0,
            "sodium_mg": 1380,
            "grade": "E"
        },
        "western_sku": {
            "region": "United Kingdom",
            "frying_medium": "High-Oleic Rapeseed Oil",
            "saturated_fat_g": 6.5,
            "grade": "D"
        },
        "double_standard_verdict": "SEVERE_OIL_DEGRADATION",
        "disparity_summary": "Asian KFC relies on deep frying in palm oil (doubling saturated fat content) compared to high-oleic rapeseed oil in the UK."
    }
]


def main():
    target_dir = "/home/linux1/macrio/datasets/processed"
    if not os.path.exists(target_dir):
        target_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datasets", "processed")
    os.makedirs(target_dir, exist_ok=True)

    hawker_file = os.path.join(target_dir, "singapore_hawker_signature_dishes.json")
    with open(hawker_file, "w", encoding="utf-8") as f:
        json.dump(HAWKER_DISHES, f, indent=2, ensure_ascii=False)
    print(f"[✓] Successfully wrote {len(HAWKER_DISHES)} Singapore hawker signature dishes to {hawker_file}")

    chains_file = os.path.join(target_dir, "fast_food_chains_nutrition.json")
    with open(chains_file, "w", encoding="utf-8") as f:
        json.dump(FAST_FOOD_CHAINS, f, indent=2, ensure_ascii=False)
    print(f"[✓] Successfully wrote {len(FAST_FOOD_CHAINS)} fast food chain items to {chains_file}")


if __name__ == "__main__":
    main()
