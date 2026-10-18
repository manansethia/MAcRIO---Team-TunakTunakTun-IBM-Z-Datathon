import psycopg2
import json

DB_CONFIG = {
    'dbname': 'macrio_db',
    'user': 'macrio',
    'password': 'macrio_secret',
    'host': 'localhost',
    'port': 5432
}

UNIVERSAL_ITEMS = [
    # --- 1. INDIAN READY-TO-EAT MIXES & CURRIES ---
    {
        "barcode": "8901042957319",
        "product_name": "MTR Minute Meals Paneer Butter Masala",
        "brand": "MTR",
        "category": "Ready-to-Eat Mixes & Curries",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "C",
        "verdict": "MODERATE_DISPARITY",
        "ingredients_summary": "Paneer (cottage cheese), refined sunflower oil, cream, butter, tomato paste, cashew nut, onion, spices.",
        "western_formula_comparison": "Retort pouch sterilization avoids Class II preservatives, but commercial retail uses high dairy/refined fat blend (>7.8g sat fat/100g) vs lighter olive/sunflower formulations in European exports.",
        "disparity_summary": "Retort shelf-stable without synthetic chemicals, but carries heavy saturated fat and sodium load (>650mg/100g).",
        "utensil_toxicity_warning": "DO NOT boil multi-layer retort pouch in water above 100°C for extended periods. Cut open and transfer contents to stainless steel or ceramic dish before heating.",
        "healthier_swap": "MTR Yellow Dal Tadka (Nutri-Grade B) or freshly prepared paneer bhurji with cold-pressed mustard oil."
    },
    {
        "barcode": "8901042957517",
        "product_name": "MTR Minute Meals Dal Makhani",
        "brand": "MTR",
        "category": "Ready-to-Eat Mixes & Curries",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "C",
        "verdict": "MODERATE_DISPARITY",
        "ingredients_summary": "Black gram lentils, kidney beans, butter, fresh cream, refined vegetable oil, ginger, garlic, tomatoes.",
        "western_formula_comparison": "High dairy butter and cream content (>6.2g saturated fat per 100g) yielding Singapore Nutri-Grade C.",
        "disparity_summary": "Authentic taste through high dairy fat; no synthetic preservatives due to retort pouch sterilization.",
        "utensil_toxicity_warning": "Transfer to stainless steel saucepan to heat; do not microwave inside the metallic aluminum-lined pouch.",
        "healthier_swap": "Gits Ready to Eat Dal Tadka or home-cooked black dal with low-fat Greek yogurt."
    },
    {
        "barcode": "8901042954516",
        "product_name": "MTR Rava Idli Instant Breakfast Mix",
        "brand": "MTR",
        "category": "Ready-to-Eat Mixes & Curries",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "C",
        "verdict": "DEGRADED_RECIPE",
        "ingredients_summary": "Semolina (sooji 80%), interesterified palm fat, bengal gram dal, cashew nut, mustard seeds, ginger, raising agent (E500ii).",
        "western_formula_comparison": "Uses cheap interesterified Palm Fat as fat stabilizer to extend semolina shelf life. Traditional South Indian preparation uses zero palm fat.",
        "disparity_summary": "Contains hidden palm fat filler (>8g fat per 100g mix) compared to pure whole grain cereal.",
        "utensil_toxicity_warning": "Steam in food-grade #304 stainless steel idli plates; avoid greasing with non-stick spray on scratched aluminum pans.",
        "healthier_swap": "Traditional naturally fermented wet rice and urad dal batter (Nutri-Grade A, zero palm oil)."
    },
    {
        "barcode": "8901155101111",
        "product_name": "Gits Gulab Jamun Instant Dessert Mix",
        "brand": "Gits",
        "category": "Ready-to-Eat Mixes & Curries",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "D",
        "verdict": "DEGRADED_RECIPE",
        "ingredients_summary": "Refined wheat flour (maida), skimmed milk powder, hydrogenated vegetable oil (palm oil fraction), raising agents (E500ii, E330).",
        "western_formula_comparison": "Contains hydrogenated/fractionated palm fat to simulate khoya texture. Absorbs massive sugar syrup (>45g sugar/100g finished dessert).",
        "disparity_summary": "High glycemic load; hydrogenated vegetable fat carrier replaces traditional pure milk solids (khoya).",
        "utensil_toxicity_warning": "Deep-fry in heavy cast iron or tri-ply stainless steel kadai; never fry in scratched Teflon non-stick pans at >180°C (PFAS release).",
        "healthier_swap": "Air-fry dough balls and soak in light jaggery/cardamom syrup or baked cottage cheese rasgulla."
    },
    {
        "barcode": "8901155103320",
        "product_name": "Gits Dosai / Crispy Dosa Instant Mix",
        "brand": "Gits",
        "category": "Ready-to-Eat Mixes & Curries",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "B",
        "verdict": "CLEAN_FORMULA",
        "ingredients_summary": "Rice flour, urad dal flour, salt, acidity regulator (E296 malic acid), raising agent (E500ii).",
        "western_formula_comparison": "Clean label cereal formulation without palm fat or artificial coloring. Benchmark healthy instant mix.",
        "disparity_summary": "Minimal additives, low baseline fat before pan-cooking.",
        "utensil_toxicity_warning": "Cook on pre-seasoned cast iron tawa rather than scratched non-stick pans to avoid microplastic ingestion.",
        "healthier_swap": "Already benchmark clean choice. Pair with fresh mint-coriander coconut chutney."
    },
    {
        "barcode": "8901155410312",
        "product_name": "Gits Ready to Eat Palak Paneer",
        "brand": "Gits",
        "category": "Ready-to-Eat Mixes & Curries",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "B",
        "verdict": "CLEAN_FORMULA",
        "ingredients_summary": "Spinach puree (50%), cottage cheese (paneer), tomato, onion, refined sunflower oil, dairy cream, spices.",
        "western_formula_comparison": "Uses cold-processed spinach and sunflower oil with no palm olein. Sterilized purely via thermal retort.",
        "disparity_summary": "Nutrient-dense spinach base with decent protein (7.2g/100g) and clean label.",
        "utensil_toxicity_warning": "Do not microwave in metallic retort pouch.",
        "healthier_swap": "Benchmark clean ready-to-eat option."
    },

    # --- 2. INDIAN SWEETS & CONFECTIONERY ---
    {
        "barcode": "8904004405910",
        "product_name": "Haldiram's Gulab Jamun (Canned Tin)",
        "brand": "Haldiram's",
        "category": "Traditional Sweets",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "D",
        "verdict": "HIGH_SUGAR_BURDEN",
        "ingredients_summary": "Sugar syrup (55%), Khoa (condensed milk solids), chhana (cottage cheese), maida, rose water, cardamom.",
        "western_formula_comparison": "Extremely high sucrose density (>48g sugar per 100g), exceeding Singapore HPB Grade D ceiling.",
        "disparity_summary": "Traditional authentic recipe with pure dairy, but excessive refined sugar syrup creates extreme blood glucose spikes.",
        "utensil_toxicity_warning": "CRITICAL CAN HAZARD: Once opened, NEVER store leftover jamuns in the original metal can. Oxygen dissolves the inner tin lining into acidic syrup. Transfer immediately to glass or ceramic container!",
        "healthier_swap": "Drain and squeeze out 70% of sugar syrup before consuming, or choose fresh homemade Chenna Poda."
    },
    {
        "barcode": "8904004405934",
        "product_name": "Haldiram's Rasgulla (Canned Tin)",
        "brand": "Haldiram's",
        "category": "Traditional Sweets",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "D",
        "verdict": "HIGH_SUGAR_BURDEN",
        "ingredients_summary": "Sugar syrup, chhana (cottage cheese 35%), purified water, rose water.",
        "western_formula_comparison": "Pure milk protein curd base, but submerged in 50% cane sugar solution. Grade D under Singapore Nutri-Grade.",
        "disparity_summary": "Clean dairy protein balls degraded by heavy refined sucrose soaking medium.",
        "utensil_toxicity_warning": "Do not store open tin in refrigerator. Transfer to airtight glass tupperware.",
        "healthier_swap": "Squeeze out sugar syrup and rinse lightly in warm cardamom water before eating."
    },
    {
        "barcode": "8904063202819",
        "product_name": "Haldiram's Soan Papdi Flaky Sweet",
        "brand": "Haldiram's",
        "category": "Traditional Sweets",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "E",
        "verdict": "DEGRADED_RECIPE",
        "ingredients_summary": "Sugar, refined wheat flour, gram flour (besan), clarified butter (Desi Ghee) & Hydrogenated Vegetable Oil (Vanaspati), almonds, pistachios.",
        "western_formula_comparison": "Combines pure ghee with cheaper partially hydrogenated vegetable fat (Vanaspati) to cut costs and stiffen flakes. Vanaspati contains harmful industrial trans-fatty acids.",
        "disparity_summary": "Vanaspati hydrogenated oil substitution creates cardiovascular risk; high sugar + refined flour.",
        "utensil_toxicity_warning": "Store in dry cool container away from direct sunlight.",
        "healthier_swap": "Haldiram's Pure Desi Ghee Soan Papdi (Special Export Pack with zero Vanaspati) or roasted almond katli."
    },
    {
        "barcode": "6568465511096",
        "product_name": "Amul Gulab Jamun (Canned Tin)",
        "brand": "Amul",
        "category": "Traditional Sweets",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "D",
        "verdict": "CLEAN_FAT_HIGH_SUGAR",
        "ingredients_summary": "Khoa, sugar, water, maida, cardamom. 100% pure Amul dairy milk solids (zero palm fat or vanaspati).",
        "western_formula_comparison": "Gold standard dairy purity in India with 100% milk fat, but earns Nutri-Grade D due to high sugar syrup content (>45g/100g).",
        "disparity_summary": "No vegetable fat substitution; pure dairy heritage formulation, high sugar penalty.",
        "utensil_toxicity_warning": "Transfer to glass bowl immediately after breaking tin seal.",
        "healthier_swap": "Amul Shrikhand (Nutri-Grade C) or drained cottage cheese with fresh berries."
    },
    {
        "barcode": "8906004450011",
        "product_name": "Bikaji Bikaneri Bhujia & Rasgulla",
        "brand": "Bikaji",
        "category": "Traditional Sweets & Snacks",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "D",
        "verdict": "MODERATE_DISPARITY",
        "ingredients_summary": "Moth flour, gram flour, groundnut oil, salt, spices. High sodium and deep-fried savory profile.",
        "western_formula_comparison": "Traditional Bikaner recipe using groundnut/palmolein oil blend.",
        "disparity_summary": "High saturated fat and high sodium (>780mg/100g).",
        "utensil_toxicity_warning": "Consume directly; avoid heating in plastic packaging.",
        "healthier_swap": "Roasted makhana (foxnuts) seasoned with black pepper and pink rock salt."
    },

    # --- 3. JAMS, SPREADS & KETCHUPS ---
    {
        "barcode": "8901030922787",
        "product_name": "Kissan Mixed Fruit Jam",
        "brand": "Kissan",
        "category": "Jams & Spreads",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "D",
        "verdict": "CHEMICAL_ADDITIVE_BURDEN",
        "ingredients_summary": "Sugar, mixed fruit pulp (45%), thickener (Pectin E440), acidity regulator (Citric Acid E330), preservative (Sodium Benzoate E211), synthetic food colors (Carmoisine E122, Tartrazine E102, Sunset Yellow E110).",
        "western_formula_comparison": "CLASSIC DOUBLE STANDARD: Asian formulation adds synthetic chemical preservative Sodium Benzoate (E211) and THREE azo dyes (E122, E102, E110). In the EU, these azo dyes legally require the statutory label: 'May have an adverse effect on activity and attention in children'. European jams preserve naturally with fruit pectin, lemon juice, and fruit pigments with zero synthetic dyes!",
        "disparity_summary": "Excessive cane sugar (>65%), Class II chemical preservative (E211), and 3 synthetic azo dyes restricted in child nutrition standards abroad.",
        "utensil_toxicity_warning": "Always use clean, dry stainless steel spoon; water contamination causes mold growth in non-benzoate sections.",
        "healthier_swap": "St. Dalfour 100% Fruit Spread (Nutri-Grade B, zero cane sugar, sweetened exclusively with vineyard grape juice, zero artificial colors)."
    },
    {
        "barcode": "8901030831690",
        "product_name": "Kissan Mixed Fruit Jam (Squeeze Bottle)",
        "brand": "Kissan",
        "category": "Jams & Spreads",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "D",
        "verdict": "CHEMICAL_ADDITIVE_BURDEN",
        "ingredients_summary": "Sugar, mixed fruit pulp (45%), pectin, citric acid, sodium benzoate (E211), synthetic azo dyes (E122, E102, E110).",
        "western_formula_comparison": "Identical chemical additive package. Squeeze pack adds plasticizer contact.",
        "disparity_summary": "High sugar, E211 preservative, multiple banned/restricted azo food colorants.",
        "utensil_toxicity_warning": "Plastic squeeze pouch is #7 resin blend; do not leave inside hot car or under tropical sunlight.",
        "healthier_swap": "Mashed fresh strawberries with chia seeds and raw honey."
    },
    {
        "barcode": "8901030534898",
        "product_name": "Kissan Fresh Tomato Ketchup",
        "brand": "Kissan",
        "category": "Sauces & Condiments",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "C",
        "verdict": "ADDITIVE_DEGRADATION",
        "ingredients_summary": "Tomato paste (26%), water, sugar, salt, acidity regulator (Acetic Acid E260), thickeners (E1422, E415), preservative (Sodium Benzoate E211), onion powder, garlic powder.",
        "western_formula_comparison": "European ketchup recipes (e.g. German/UK Heinz) use natural vinegar preservation without Sodium Benzoate (E211). Indian version adds E211 preservative and modified starches to thicken lower tomato solid content.",
        "disparity_summary": "Diluted tomato solids stabilized with starch thickeners and synthetic benzoate preservative.",
        "utensil_toxicity_warning": "Glass bottle is safe; store refrigerated after opening.",
        "healthier_swap": "Organic tomato passata seasoned with oregano and balsamic vinegar."
    },
    {
        "barcode": "8901044200284",
        "product_name": "Mapro Mixed Fruit Jam",
        "brand": "Mapro",
        "category": "Jams & Spreads",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "C",
        "verdict": "MODERATE_DISPARITY",
        "ingredients_summary": "Fruit pulp (strawberry, mulberry, raspberry, papaya 48%), sugar, pectin, citric acid, preservative (E211).",
        "western_formula_comparison": "Higher real fruit content than mass market brands, but still relies on Sodium Benzoate (E211) and refined sugar.",
        "disparity_summary": "Berry-rich base, but penalised by Class II preservative and added sucrose.",
        "utensil_toxicity_warning": "Keep refrigerated; handle with clean metal cutlery.",
        "healthier_swap": "Whole fruit preserves with zero refined sugar."
    },
    {
        "barcode": "8901058117783",
        "product_name": "Maggi Hot & Sweet Tomato Chilli Sauce",
        "brand": "Maggi",
        "category": "Sauces & Condiments",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "C",
        "verdict": "MODERATE_DISPARITY",
        "ingredients_summary": "Tomato paste, sugar, red chilli puree (5%), vinegar, thickener (1422), preservative (211).",
        "western_formula_comparison": "Indian signature spicy ketchup formulation. Uses chemical preservative (E211) and liquid glucose.",
        "disparity_summary": "Contains ~27% sugar and chemical preservative Sodium Benzoate.",
        "utensil_toxicity_warning": "High acidity; avoid storing in reactive unlined metal dishes.",
        "healthier_swap": "Fresh tomato chutney tempered with mustard seeds and curry leaves."
    },

    # --- 4. INSTANT NOODLES ---
    {
        "barcode": "8901058851298",
        "product_name": "Maggi 2-Minute Masala Noodles (India SKU)",
        "brand": "Maggi",
        "category": "Instant Noodles",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "D",
        "verdict": "SEVERE_DEGRADATION",
        "ingredients_summary": "Noodle Cake: Refined wheat flour (Maida), Palm Oil, Mineral (Calcium Carbonate), Thickeners (412, 508), Acidity Regulators (501i, 500i). Tastemaker: Hydrolysed peanut protein, mixed spices (coriander, turmeric, chilli, cumin, fenugreek, clove, nutmeg), onion powder, sugar, palm oil, flavour enhancer (635), acidity regulator (330).",
        "western_formula_comparison": "FLAGRANT DOUBLE STANDARD: In European Maggi noodles, sunflower oil or rapeseed oil is used with zero added palm fat. The Indian formulation fries the noodle cake in cheap Palm Oil (>13g fat, 6.5g saturated fat per 70g cake) and contains massive sodium (>950mg per pack, almost 50% daily allowance).",
        "disparity_summary": "Deep-fried in Palm Olein with ultra-processed flavor enhancer Disodium 5'-ribonucleotides (635) and high sodium.",
        "utensil_toxicity_warning": "LEACHING RISK: Never cook or pour boiling water directly into Styrofoam (#6 PS) or flimsy plastic containers. High noodle palm oil heat extracts carcinogenic styrene monomer. Always cook in a stainless steel pot and eat from ceramic/glass bowls!",
        "healthier_swap": "Non-fried brown rice ramen or millets noodles cooked with fresh vegetables and homemade vegetable broth."
    },
    {
        "barcode": "8901058022223",
        "product_name": "Maggi Veg Atta Noodles (Whole Wheat)",
        "brand": "Maggi",
        "category": "Instant Noodles",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "C",
        "verdict": "MODERATE_DISPARITY",
        "ingredients_summary": "Whole wheat flour (Atta 85%), palm oil, salt, dehydrated vegetables (green peas, carrot), spices, flavor enhancer (635).",
        "western_formula_comparison": "Substitutes maida with whole wheat atta (higher dietary fiber 4.5g), but still deep-fries the cake in Palm Oil.",
        "disparity_summary": "Whole grain improvement, but saturated palm oil frying fat remains unchanged.",
        "utensil_toxicity_warning": "Boil in stainless steel saucepan.",
        "healthier_swap": "Air-dried Hakka whole wheat noodles cooked in olive oil."
    },
    {
        "barcode": "8901058890624",
        "product_name": "Maggi Chicken Cuppa Noodles",
        "brand": "Maggi",
        "category": "Instant Noodles",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "D",
        "verdict": "SEVERE_DEGRADATION",
        "ingredients_summary": "Noodle cake: Refined wheat flour, palm oil, salt. Seasoning: Dehydrated chicken bits (3%), chicken fat, flavor enhancers (627, 631).",
        "western_formula_comparison": "Sold in direct contact with disposable heated cup. High saturated fat and sodium load (>1120mg).",
        "disparity_summary": "Palm oil fried noodle cake in single-use plastic/paper composite cup.",
        "utensil_toxicity_warning": "CUP HAZARD: Pouring boiling water into PE-lined paper cup releases up to 25,000 microplastic particles into the broth in 15 minutes! Transfer dry noodles to a ceramic mug before pouring boiling water.",
        "healthier_swap": "Fresh shredded chicken with soba noodles and homemade chicken bone broth."
    },
    {
        "barcode": "8901595852504",
        "product_name": "Ching's Secret Schezwan Instant Noodles",
        "brand": "Ching's Secret",
        "category": "Instant Noodles",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "D",
        "verdict": "CHEMICAL_ADDITIVE_BURDEN",
        "ingredients_summary": "Wheat flour, refined palm oil, salt, chili, garlic, Sichuan pepper, flavor enhancer (Monosodium Glutamate E621), preservative (TBHQ E319).",
        "western_formula_comparison": "Uses synthetic chemical antioxidant TBHQ (E319) in palm frying oil, which is strictly capped and restricted in sensitive overseas food codes.",
        "disparity_summary": "TBHQ preservative, MSG flavor enhancer, and high palm oil saturated fat burden.",
        "utensil_toxicity_warning": "Do not stir-fry seasoning pack directly in high-heat aluminum wok (acidic chili reacts with uncoated aluminum).",
        "healthier_swap": "Organic soba noodles tossed with fresh garlic, chili flakes, and sesame oil."
    },
    {
        "barcode": "8906010060013",
        "product_name": "Wai Wai Ready to Eat Masala Noodles",
        "brand": "Wai Wai",
        "category": "Instant Noodles",
        "origin_market": "Nepal / India / Universal",
        "nutri_grade": "E",
        "verdict": "CHEMICAL_ADDITIVE_BURDEN",
        "ingredients_summary": "Pre-cooked brown noodles fried in palm oil, onion, garlic, flavor enhancer (MSG E621, 627, 631), chili powder, fried onion oil pouch.",
        "western_formula_comparison": "Heavy seasoning load; consumed often raw/uncooked directly from packet, exposing lining to concentrated palm fat and high sodium (>1200mg/pack).",
        "disparity_summary": "Extreme sodium, artificial flavor enhancers (621/627/631), and deep-fried palm cake.",
        "utensil_toxicity_warning": "Never microwave the seasoning oil packet directly in its plastic film.",
        "healthier_swap": "Rice vermicelli noodles in mild ginger-vegetable broth."
    },
    {
        "barcode": "8901014002542",
        "product_name": "Nissin Top Ramen Chicken Instant Noodles",
        "brand": "Nissin",
        "category": "Instant Noodles",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "D",
        "verdict": "MODERATE_DISPARITY",
        "ingredients_summary": "Refined wheat flour, edible vegetable oil (palm), iodised salt, chicken seasoning, flavor enhancers (627, 631).",
        "western_formula_comparison": "Palm oil fried noodles, high sodium density.",
        "disparity_summary": "Typical FMCG instant noodle profile with saturated fat and synthetic nucleotides.",
        "utensil_toxicity_warning": "Always prepare in stainless steel / glassware.",
        "healthier_swap": "Traditional Japanese soba with poached egg."
    },

    # --- 5. BISCUITS, SNACKS & BEVERAGES ---
    {
        "barcode": "8901719101037",
        "product_name": "Parle-G Original Glucose Biscuits",
        "brand": "Parle",
        "category": "Biscuits & Cookies",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "D",
        "verdict": "DEGRADED_RECIPE",
        "ingredients_summary": "Wheat flour (maida), sugar, refined palm oil, invert sugar syrup, raising agents (503ii, 500ii), milk solids, artificial vanilla flavouring.",
        "western_formula_comparison": "World's top selling biscuit uses cheap Palm Oil as the sole fat shortening and contains >26g added refined sugar per 100g, earning Nutri-Grade D in Singapore.",
        "disparity_summary": "Refined flour + Palm Oil + Invert Syrup; disguised as 'healthy energy' glucose biscuit.",
        "utensil_toxicity_warning": "Ambient dry food; package is LDPE #4 recyclable.",
        "healthier_swap": "Whole wheat Scottish oatcakes or Parle-G Oats & Berries."
    },
    {
        "barcode": "8901063012219",
        "product_name": "Britannia Good Day Butter Cookies",
        "brand": "Britannia",
        "category": "Biscuits & Cookies",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "D",
        "verdict": "DEGRADED_RECIPE",
        "ingredients_summary": "Refined wheat flour, sugar, refined palm oil, butter (approx 2%), invert syrup, milk solids, artificial butter flavour.",
        "western_formula_comparison": "DECEPTIVE LABELLING: Marketed prominently as 'Butter Cookies', but laboratory ingredient audit shows it contains predominantly cheap Palm Oil with barely 2% actual dairy butter! European butter cookies (Danish butter cookies) legally require 100% butter fat with zero palm oil substitution.",
        "disparity_summary": "98% palm oil shortening substituted for advertised dairy butter.",
        "utensil_toxicity_warning": "Keep in airtight tin away from humidity.",
        "healthier_swap": "Authentic shortbread cookies made with 100% pure butter and zero vegetable shortening."
    },
    {
        "barcode": "8901491101019",
        "product_name": "Kurkure Masala Munch Crunchy Snack",
        "brand": "PepsiCo India",
        "category": "Savory Snacks",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "D",
        "verdict": "DEGRADED_RECIPE",
        "ingredients_summary": "Rice meal, edible vegetable oil (palmolein), corn meal, gram meal, spices and condiments, citric acid, tartaric acid.",
        "western_formula_comparison": "Deep-fried in Palmolein oil; high saturated fat (>10g/100g) and sodium (~850mg/100g). Western Cheetos utilize sunflower/corn oil blends.",
        "disparity_summary": "Palmolein oil frying medium and high sodium seasoning profile.",
        "utensil_toxicity_warning": "High temperature extrusion; foil pouch is composite plastic/metal.",
        "healthier_swap": "Roasted lotus seeds (Makhana) or baked whole wheat crisps."
    },
    {
        "barcode": "8901233010022",
        "product_name": "Cadbury Bournvita Chocolate Health Drink",
        "brand": "Cadbury / Mondelez",
        "category": "Health Food Drinks",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "D",
        "verdict": "DEGRADED_RECIPE",
        "ingredients_summary": "Cereal extract (barley, malted barley), sugar (approx 32g added sugar per 100g), cocoa solids, milk solids, liquid glucose, caramel colour (150c), minerals, vitamins.",
        "western_formula_comparison": "MAJOR SCANDAL IN ASIAN NUTRITION: Aggressively advertised to Indian parents as a height and brain growth enhancer for school children, despite containing over 32% refined added sugar and liquid glucose, earning Nutri-Grade D in Singapore. Forced by Indian government to reduce sugar claim in 2023.",
        "disparity_summary": "32% sugar disguised as health food, with artificial caramel III (150c) ammonia-process colorant.",
        "utensil_toxicity_warning": "Do not boil powder into boiling milk inside plastic sippers; mix in glass or stainless steel tumblers.",
        "healthier_swap": "Raw unsweetened organic cocoa powder stirred into whole milk with half a teaspoon of raw honey (Nutri-Grade B)."
    },
    {
        "barcode": "8901262030663",
        "product_name": "Amul Pure Cow Ghee (Tin)",
        "brand": "Amul",
        "category": "Cooking Fats & Oils",
        "origin_market": "India / Universal Retail",
        "nutri_grade": "B",
        "verdict": "BENCHMARK_CLEAN_LABEL",
        "ingredients_summary": "100% pure clarified cow milk fat. Zero palm oil, zero synthetic antioxidants (zero BHA/BHT).",
        "western_formula_comparison": "Gold standard traditional Indian cooking fat. Unlike refined seed oils or palm olein, pure ghee has a smoke point of 250°C and does not break down into toxic acrolein or polar compounds when used for frying.",
        "disparity_summary": "Pristine pure fat; zero palm oil, zero chemical additives.",
        "utensil_toxicity_warning": "Safe with all cookware including cast iron, copper-bottomed stainless steel, and clay pots.",
        "healthier_swap": "Already the gold standard traditional cooking medium."
    }
]

def populate():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS universal_fmcg_catalog (
        barcode VARCHAR(32) PRIMARY KEY,
        product_name TEXT NOT NULL,
        brand TEXT NOT NULL,
        category TEXT NOT NULL,
        origin_market TEXT,
        nutri_grade VARCHAR(4),
        verdict VARCHAR(32),
        ingredients_summary TEXT,
        western_formula_comparison TEXT,
        disparity_summary TEXT,
        utensil_toxicity_warning TEXT,
        healthier_swap TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    for item in UNIVERSAL_ITEMS:
        cur.execute("""
        INSERT INTO universal_fmcg_catalog (
            barcode, product_name, brand, category, origin_market, nutri_grade,
            verdict, ingredients_summary, western_formula_comparison,
            disparity_summary, utensil_toxicity_warning, healthier_swap
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (barcode) DO UPDATE SET
            product_name = EXCLUDED.product_name,
            brand = EXCLUDED.brand,
            category = EXCLUDED.category,
            nutri_grade = EXCLUDED.nutri_grade,
            verdict = EXCLUDED.verdict,
            ingredients_summary = EXCLUDED.ingredients_summary,
            western_formula_comparison = EXCLUDED.western_formula_comparison,
            disparity_summary = EXCLUDED.disparity_summary,
            utensil_toxicity_warning = EXCLUDED.utensil_toxicity_warning,
            healthier_swap = EXCLUDED.healthier_swap;
        """, (
            item["barcode"], item["product_name"], item["brand"], item["category"],
            item["origin_market"], item["nutri_grade"], item["verdict"],
            item["ingredients_summary"], item["western_formula_comparison"],
            item["disparity_summary"], item["utensil_toxicity_warning"],
            item["healthier_swap"]
        ))

        # Also ensure these items are in the main products table!
        cur.execute("""
        INSERT INTO products (
            barcode, product_name, brands, ingredients_text,
            nutriscore_grade, target_countries, additives_tags, source
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (barcode) DO UPDATE SET
            product_name = EXCLUDED.product_name,
            brands = EXCLUDED.brands,
            ingredients_text = EXCLUDED.ingredients_text;
        """, (
            item["barcode"], item["product_name"], item["brand"],
            item["ingredients_summary"], item["nutri_grade"].lower(),
            ["en:india", "en:universal"], [], "universal_fmcg_catalog"
        ))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Successfully populated {len(UNIVERSAL_ITEMS)} universal FMCG items into universal_fmcg_catalog!")

if __name__ == '__main__':
    populate()
