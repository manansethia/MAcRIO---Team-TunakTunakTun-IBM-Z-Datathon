# MAcRIO — Master Memory & Technical Architecture Bible

> **File:** `memory.md`  
> **Status:** Living Master Specification & Engineering Logbook  
> **Target Architecture:** IBM LinuxONE `s390x` (Ubuntu 24.04 LTS, Telum AI Accelerator, Hyper Protect Virtual Servers)  
> **Client Platform:** Android & iOS (Cross-Platform / Native with AR Overlay & Screen Accessibility Blob)  
> **Last Updated:** October 2026  

---

## 1. Executive Vision & Problem Statement

**MAcRIO** is an AI and Data-assisted health, safety, and nutritional transparency platform engineered natively for **IBM LinuxONE (s390x)**. It bridges three massive health gaps in Southeast Asia (Singapore, Malaysia, Indonesia) and India:

1. **Multinational Double Standards:** Multinational food corporations sell everyday items in Asian, African, and Latin American markets with degraded, cheaper ingredients (e.g., low-grade palm oil/palmolein, high-fructose corn syrup, artificial food dyes like Tartrazine/Sunset Yellow, banned preservatives like potassium bromate or titanium dioxide E171) compared to identical brand versions sold in the US, Canada, and EU.
2. **Western Macro App Blindspot:** Existing diet trackers (MyFitnessPal, etc.) are built for Western diets and fail to understand regional street foods, hawker centres, local grocery brands, and local languages (Malay, Indonesian, Hindi, Tamil, Mandarin).
3. **Kitchenware, Container & Utensil Leaching:** Consumers lack intuitive tools to detect toxic food plastics (Resin Identification Codes #1–#7), scratched non-stick Teflon (PTFE) cookware releasing PFAS/microplastics, and unpassivated aluminum pots leaching toxins into acidic curries.

---

## 2. The MAcRIO Super Dataset: Multi-Source Architecture

The MAcRIO database aggregates global, regional, governmental, restaurant, and community datasets into a unified PostgreSQL schema on IBM LinuxONE:

```
                                  ┌──────────────────────────────────────────┐
                                  │           MAcRIO SUPER DATASET           │
                                  └────────────────────┬─────────────────────┘
                                                       │
         ┌──────────────────┬──────────────────────────┼──────────────────────────┬──────────────────┐
         │                  │                          │                          │                  │
┌────────┴────────┐┌────────┴────────┐        ┌────────┴────────┐        ┌────────┴────────┐┌────────┴────────┐
│ Packaged Foods  ││  Hawker & Street│        │ Fast Food Chains│        │   Regulatory    ││ Utensil & Resin │
│   & Barcodes    ││  Food & Drinks  │        │   & Cosmetics   │        │ Additive Matrix ││ CV Image Sets   │
├─────────────────┤├─────────────────┤        ├─────────────────┤        ├─────────────────┤├─────────────────┤
│• OpenFoodFacts  ││• SG HPB FoodID  │        │• Nutritionix API│        │• EU EFSA Banned ││• RIC 1-7 Codes  │
│  (3.01M target) ││• Data.gov.sg HCS│        │• Fast Food DB   │        │• US FDA Status  ││• Scratched PTFE │
│• GS1 Singapore  ││• SFA Hygiene    │        │  (McD, BK, KFC) │        │• SG SFA Limits  ││• Acidic Alum.   │
│  (888... prefix)││• India (IFCT)   │        │• Open Beauty    │        │• India FSSAI    ││• Styrofoam Heat │
│• USDA FDC (US)  ││• Indo (TKPI)    │        │  Facts (Cosmetics)│      │• Yuka 4-Tier    ││• Kalai Brass    │
└─────────────────┘└─────────────────┘        └─────────────────┘        └─────────────────┘└─────────────────┘
```

### Layer 1: Packaged Foods & Barcode Repositories
1. **Open Food Facts (OFF Global Dump):**
   * Processed on LinuxONE: **3,010,023 target market products** extracted from 4.81M global rows into `/home/linux1/macrio/datasets/processed/target_markets_products.jsonl.gz` (211 MB compressed).
   * Contains **11,932 products explicitly sold in Singapore** and **5,538 GS1 Singapore (`888...`) national barcodes** across 3,364 local brands (NTUC FairPrice, Pokka, Yeo's, Tiger, Gardenia, etc.).
2. **USDA FoodData Central (FDC):**
   * Gold standard US nutritional and ingredient formulation baseline (350,000+ branded products) to contrast against Asian SKUs for double-standard detection.
3. **Data.gov.sg Health Promotion Board (HPB) HCS Database:**
   * Downloaded directly on server: `/home/linux1/macrio/datasets/processed/singapore_hcs_products.json` (**4,387 official Singapore Healthier Choice Symbol products**).

### Layer 2: Singapore Hawker Centre Signatures & Regional Street Foods
1. **Singapore Hawker Signatures & Drinks Knowledge Base (`singapore_hawker_signature_dishes.json`):**
   * **Hainanese Chicken Rice (Steamed):** 610 kcal, 28g protein, 24g fat, 980mg sodium. Grade: **B**. Twist: Request breast meat without skin, less chicken-fat rice.
   * **IJOOZ Fresh Squeezed Orange Juice:** 115 kcal, 22g fruit sugar, 0g sat fat. Grade: **C** (Nutri-Grade C). 100% natural pure orange juice without added cane sugar, but high natural sugar concentration (>7.5g/100ml) causes rapid glycemic index spike.
   * **Char Kway Teow:** 745 kcal, 38g fat (14.5g sat fat), 1,450mg sodium. Grade: **E**. Fried in pork lard with sweet dark soy sauce and lap cheong.
   * **Katong Laksa:** 590 kcal, 32g fat (18g sat fat), 1,650mg sodium. Grade: **D**. Rich coconut milk broth delivering full daily saturated fat limit.
   * **Fish Soup Bee Hoon (Clear Soup):** 350 kcal, 26g protein, 6g fat, 820mg sodium. Grade: **A** (Benchmark clean hawker meal).
   * **Roti Prata with Curry:** 490 kcal, 26g fat (11g sat fat). Grade: **D**. Refined dough pan-fried with margarine/ghee. Swap: Tosai/Chapati.
   * **Nasi Lemak:** 680 kcal, 36g fat (15g sat fat). Grade: **D**.
   * **Kaya Toast with Eggs & Kopi-O Kosong:** 360 kcal, 15g protein. Grade: **B**.
   * **Chendol:** 390 kcal, 16g fat, 62g sugar. Grade: **E**. Heavy coconut milk and Gula Melaka syrup.
   * **Sugarcane Juice with Lemon:** 190 kcal, 46g sugar. Grade: **D** (Nutri-Grade D). Liquid sugar bomb.
2. **Regional Food Tables:**
   * **India:** ICMR-NIN IFCT 2017 (528 foods, 151 nutrient parameters, 12 regional Indian languages).
   * **Indonesia:** Kemenkes TKPI 2020 (838 traditional foods with macros).

### Layer 3: Fast Food Chains & Personal Care (Cosmetics)
1. **Fast Food Chains Database (`fast_food_chains_nutrition.json` & Nutritionix API):**
   * **McDonald's:** French Fries fried in Palm Olein blend in Singapore/Asia (Grade D, 4.5g sat fat) vs. cold-pressed high-oleic sunflower/rapeseed in the UK/EU (Grade C, 1.8g sat fat).
   * **Burger King:** Whopper flame-broiled beef; mayonnaise palm oil substitution in Asia.
   * **Starbucks:** Caramel Macchiato with ~7 teaspoons of liquid sugar (Nutri-Grade C, Grade C). Swap: Americano with oat milk (Nutri-Grade A).
   * **KFC:** Original Recipe Chicken deep-fried in palm oil in Asia (Grade E, 13g sat fat) vs. high-oleic rapeseed oil in the UK (Grade D, 6.5g sat fat).
2. **Open Beauty Facts (OBF):**
   * Cosmetics, personal care, shampoos, soaps, sunscreens.
   * Chemical screening: Endocrine disruptors, parabens (propylparaben), phthalates, formaldehyde-releasers (DMDM hydantoin), and PFAS.

### Layer 4: Regulatory Watchlists & Double Standards Matrix
* **EFSA (EU) vs FDA (US) vs FSSAI (India) vs SFA (Singapore):**
  * *Titanium Dioxide (E171):* Banned in EU since 2022 (genotoxicity); legal in US, India, ASEAN.
  * *Azo Dyes (E102, E110, E122, E129):* Mandatory warning in EU (*"May have an adverse effect on activity and attention in children"*); unrestricted in Asia.
  * *Potassium Bromate (E924) & Azodicarbonamide (E927a):* Banned in EU, UK, Canada, India; legal in US.
  * *Palm Oil vs Sunflower / Butter:* Automatic disparity deduction when palm oil replaces higher-grade oils.

---

## 3. Computer Vision & AI Models Architecture

### Model 1: Hawker Centre Cleanliness & Food Safety AI
* **Input:** Video stream / photo of hawker stall counter, preparation area, and floor.
* **Outputs:**
  * Cleanliness Score (0–100%).
  * SFA Hygiene Grade Cross-Verification (Validates displayed SFA Grade A/B/C/D against live stall conditions).
  * Food Handling Compliance: Bare-hand contact with cooked food, raw and cooked food cross-contamination risks, ambient temperature holding violations.
  * Pest & Debris Alerts.

### Model 2: Container, Cookware & Utensil Safety AI
* **Input:** Photo of kitchenware, pans, plastic takeaway containers, or cups.
* **Outputs:**
  * **Resin Identification Code (RIC 1–7):**
    * `#1 PET`: Flag single-use; warn against warm water/tea reuse (antimony & microplastic shedding).
    * `#3 PVC`: Strict toxic alert (phthalates, dioxins, vinyl chloride).
    * `#5 PP`: Best food-grade microwave plastic; heat tolerant to 130°C.
    * `#6 PS (Styrofoam)`: **HAZARDOUS HEAT ALERT**. Leaches styrene monomer (IARC Group 2A probable carcinogen) when exposed to hot soups (laksa, noodles) or hot tea/coffee.
    * `#7 OTHER`: High alert for BPA (polycarbonate) and formaldehyde (melamine tableware under microwave heat).
  * **Cookware Surface Wear:**
    * *Scratched Teflon (PTFE):* Deep scratches trigger SEVERE alert (up to 9,000 microplastic/nanoplastic particles released per cook, PFAS forever chemicals).
    * *Uncoated Aluminum Pots:* Detects pitting; warns against cooking acidic curries (tomato, tamarind rasam, sambal, vinegar) which leach neurotoxic aluminum ions.
    * *Unlined Copper/Brass (Kansa/Tamba):* Detects tarnished Kalai (tin lining) and green verdigris patina (copper salt toxicity).

### Model 3: Signature Singaporean Dishes & Drinks Recognition
* **Architecture:** MobileNetV4 / YOLOv10 fine-tuned on Singaporean hawker food imagery.
* **Classes:** Hainanese Chicken Rice (steamed vs roasted), IJOOZ Orange Juice, Katong Laksa, Char Kway Teow, Nasi Lemak, Roti Prata, Fish Soup Bee Hoon, Bak Kut Teh, Kaya Toast & Eggs, Hokkien Mee, Chendol, Sugarcane Juice.
* **Inference Output:** Bounding box, dish classification confidence, estimated portion size, calorific breakdown, macronutrients (P/C/F), sodium content, and healthier swap recommendations.

---

## 4. Groundbreaking Mobile UX Features

### Feature 1: AR Live Menu & Food Hoarding Scanner (Google Lens Style)
* **How It Works:** Point the phone camera at a restaurant printed menu, hawker stall signboard, or food hoarding.
* **On-Device OCR & Text Bounding:** Detects text bounding boxes for each dish name and price.
* **Real-Time Grading Scale: A, B, C, D, E, F, and X:**
  * **A (Green):** Pristine, nutrient-dense, clean protein, low sodium, healthy fats (e.g., Fish Soup Bee Hoon Clear, Pokka Green Tea No Sugar).
  * **B (Light Green):** Balanced meal, moderate carbs/sodium (e.g., Steamed Chicken Rice breast, Kaya Toast with Eggs).
  * **C (Yellow):** Moderate free sugar or saturated fat (e.g., Milo, IJOOZ Orange Juice, Yeo's Chrysanthemum Tea).
  * **D (Orange):** High saturated fat, high sodium, heavy refined carbs (e.g., Maggi Curry Noodles, Katong Laksa, Roti Prata, Whopper).
  * **E (Red):** Extreme ultra-processed, deep-fried in reused palm oil, excessive chemical additives (e.g., Char Kway Teow, Indomie Mi Goreng, Chendol).
  * **F (Dark Red):** Severe nutritional degradation, banned or heavily restricted food dyes (e.g., Tartrazine E102 / Sunset Yellow E110 without warning).
  * **X (Black Skull / Biohazard):** **TOXIC / HAZARDOUS WARNING**. Used when food is served in heated Styrofoam (#6 PS), cooked on flaking Teflon, or contains prohibited toxic additives.
* **AR Sticky Font-Matching Overlay:**
  * Renders a glowing AR badge pill directly beside each dish name on the live camera preview.
  * The AR badge dynamically matches the detected font height, slant, and baseline of the text on the physical menu!

### Feature 2: Mobile Floating Assistant ("The Hover Blob")
* **Concept:** A non-intrusive floating accessibility widget (like Facebook Messenger Chat Heads) that stays on screen.
* **Third-Party App Integration:** When the user opens food delivery apps (**GrabFood, Foodpanda, Deliveroo**) or fast food apps (**McDonald's SG, KFC SG**):
* **One-Tap Screen Scan:** User taps the floating blob $\to$ it captures the active screen $\to$ executes OCR on the menu items listed on screen $\to$ overlays calorific values, A–X grades, and healthier swap recommendations directly on top of GrabFood/Foodpanda!
* **Daily Meal Logging & Meal Planning:** Users can add scanned items to their daily meal log with one tap, tracking daily protein, sugar, and saturated fat limits.

---

## 5. Crowdsourcing & Two-Stage Verification Pipeline

When a user scans a barcode or product that is not currently in the offline database:

```
[User Scans Missing Product]
           │
           ▼
[Captures 4 Photos: Barcode, Front, Ingredients Text, Nutrition Panel]
           │
           ▼
[Staged in `pending_submissions` Table on LinuxONE]
           │
           ▼
[Stage 1: IBM Telum AI OCR & Plausibility Audit]
• Validates EAN-13 check digit
• Extracts OCR text from ingredients & nutrition panel
• Checks for hallucinated or conflicting calorie math (4-4-9 rule)
           │
           ▼
[Stage 2: Verification Queue]
• Admin approval dashboard OR multi-user consensus verification (3 independent user confirmations)
           │
           ▼
[Promoted to Live `products` Table in `macrio_db`]
```

---

## 6. Current System State & Active Milestones

* [x] **LinuxONE Mainframe Connected:** Ubuntu 24.04 s390x (`tunaktunaktun-macrio-ibm-z-datathon` at `148.100.108.86`).
* [x] **Global ETL Completed:** 3,010,023 target market products extracted from 4.81M rows (211 MB compressed in `/home/linux1/macrio/datasets/processed/target_markets_products.jsonl.gz`).
* [x] **Database Initialized & Bulk Ingestion Completed on LinuxONE:**
  * **Database:** `macrio_db` running natively on PostgreSQL with TLSv1.3 encryption.
  * **`products` Table:** **3,009,990 products** loaded in 132 seconds (~22,700 rows/sec) with B-tree index on `barcode` for sub-5ms lookups.
  * **`singapore_hawker_dishes` Table:** Seeded with 10 signature dishes/drinks with Trigram GiST index for instant fuzzy menu matching.
  * **`prime_supermarket_proof` Table:** 10 verified real-world shelf items (Milo, Maggi Curry Noodles, Nutella, Oreo, etc.) with real Singapore EAN-13 barcodes.
  * **`fast_food_items` Table:** McDonald's, Burger King, Starbucks, KFC cross-border disparity audits.
  * **`utensil_safety_rules` Table:** RIC #1–#7 and cookware degradation toxicity rules.
  * **`pending_submissions` Table:** Crowdsourced missing product staging & verification queue.
* [x] **FastAPI Core Backend Live & Verified on LinuxONE (Port 8000):**
  * **Uvicorn Daemon:** Running on `http://0.0.0.0:8000` (`PID: 35434`).
  * **Interactive Swagger UI:** Accessible on local browser via SSH tunnel at **`http://localhost:8000/docs`**.
  * **Endpoints Live & Tested:**
    * `GET /health`: Verified database connection and row counts.
    * `GET /api/v1/scan/barcode/{code}`: Tested with Milo (`8888082001016`) $\to$ returns full double-standard breakdown, Nutri-Grade C, and cleaner swap.
    * `POST /api/v1/menu/ocr-grade`: Tested with Chicken Rice, Laksa, Fish Soup, IJOOZ, CKT $\to$ outputs **A, B, C, D, E** letter grades and AR sticky badge specs.
    * `GET /api/v1/hawker/dishes`: Returns all Singapore hawker dishes and nutrition.
    * `GET /api/v1/utensils/safety/{code}`: Tested with `RIC_6` $\to$ flags Styrofoam heat leaching hazard.
    * `POST /api/v1/submit/product`: Successfully staged new crowdsourced product submission.
* [x] **Web Demo Upgrade & Mobile QR Connect (Completed):**
  * **Design System Aligned with `profkwanminlee.github.io`**:
    * Palette: `#0d0e11` obsidian background, `#14151a` dark card, `#1b1d23` card hover, `#1e2026`/`#2a2c34` subtle borders, `#e0dcc7` champagne gold accent.
    * Typography: `Plus Jakarta Sans` for clean, minimal structure; `JetBrains Mono` for hardware badges, barcodes, and macro tags.
    * Non-generative, simple, academic-grade engineering aesthetics (zero neon AI fluff).
  * **Semantic Grading Colors (A to X)**:
    * Grade A: `#00C853` (Pristine / Clean / Benchmark)
    * Grade B: `#64DD17` (Healthier Choice / Low Saturated Fat)
    * Grade C: `#FFD600` (Moderate Sugar / Refined Fillers)
    * Grade D: `#FF9100` (High Saturated Fat / Palm Olein Degraded)
    * Grade E: `#FF3D00` (Chemical Burden / Multiple Preservatives)
    * Grade F: `#D50000` (Severe Disparity / Banned Additives)
    * Grade X: `#14151a` with `#E53935` border and skull hazard badge (Cookware / Utensil Leaching Toxicity)
  * **Interactive Scannable Shelf & Generator**:
    * Prime Supermarket shelf cards render high-contrast GS1 EAN-13 barcodes with instant toggle to 2D QR codes for phone camera scanning.
    * Added dedicated **Barcode & QR Generator Tab** to test any product barcode from the 3M database.
    * Added **In-Browser Camera Scanner Tab** (`Html5Qrcode`) for live laptop webcam or phone camera barcode scanning.
    * Added **Mobile Connect Modal**: Generates high-contrast QR code for `http://10.91.78.253:8080` (with editable IP input) so the user can scan the screen with their phone camera and immediately open the demo on mobile.
* [x] **Universal FMCG & Global Barcode Integration (Completed):**
  * **Addressed User Gap**: User tested common physical Indian ready-to-eat mixes, traditional sweets, jams, and noodles which previously showed "not found" due to missing universal barcodes and strict exact barcode matching.
  * **Multi-Tiered Barcode Resolver Engine**:
    * Implemented `normalize_barcode_variants()` to automatically handle unpadded barcodes, 12-digit UPC-A, 13-digit EAN-13, and 14-digit GTIN-14.
    * **Tier 1 (Instant Local Database)**: Checks curated `universal_fmcg_catalog` $\to$ `prime_supermarket_proof` $\to$ `products` (3,009,990 rows).
    * **Tier 2 (Live Global API Fallback & Auto-Cache)**: If a barcode is missing from local DB, automatically queries the live Open Food Facts global API (`https://world.openfoodfacts.org/api/v2/product/{code}.json`), extracts ingredients/nutrients/additives, executes the double-standard audit in memory, and **auto-caches into PostgreSQL on LinuxONE** so subsequent queries are sub-5ms.
    * **Tier 3 (Crowdsourced AI Staging Queue)**: If still not found, provides 1-click submission directly into `pending_submissions` for IBM Telum AI verification.
  * **Created `universal_fmcg_catalog` Table in PostgreSQL**:
    * **Ready-to-Eat Mixes & Curries**: MTR Minute Meals Paneer Butter Masala (`8901042957319`), MTR Dal Makhani (`8901042957517`), MTR Rava Idli Mix (`8901042954516`), Gits Gulab Jamun Mix (`8901155101111`), Gits Dosa Mix (`8901155103320`), Gits Palak Paneer (`8901155410312`).
    * **Traditional Sweets & Desserts**: Haldiram's Gulab Jamun (`8904004405910`), Haldiram's Rasgulla (`8904004405934`), Haldiram's Soan Papdi (`8904063202819`), Amul Gulab Jamun (`6568465511096`), Bikaji Rasgulla (`8906004450011`).
    * **Jams, Spreads & Ketchups**: Kissan Mixed Fruit Jam (`8901030922787`), Kissan Squeeze Jam (`8901030831690`), Kissan Fresh Tomato Ketchup (`8901030534898`), Mapro Mixed Fruit Jam (`8901044200284`), Maggi Hot & Sweet Chilli Sauce (`8901058117783`), Nutella (`8000500179864`).
    * **Instant Noodles**: Maggi 2-Minute Masala Noodles India (`8901058851298`), Maggi Veg Atta (`8901058022223`), Maggi Chicken Cuppa (`8901058890624`), Ching's Secret Schezwan (`8901595852504`), Wai Wai Masala (`8906010060013`), Nissin Top Ramen Chicken (`8901014002542`), Indomie Mi Goreng (`8998866200226`).
    * **Biscuits, Snacks & Cooking Fats**: Parle-G (`8901719101037`), Britannia Good Day (`8901063012219`), Kurkure (`8901491101019`), Bournvita (`8901233010022`), Amul Pure Cow Ghee (`8901262030663`).
  * **Unified Smart Search API (`GET /api/v1/search/products?q=...`)**:
    * Added btree text index on `lower(product_name)` on LinuxONE PostgreSQL.
    * Users can search either by numerical barcode OR by product/brand names (`MTR`, `Gulab Jamun`, `Kissan Jam`, `Maggi`, `Amul`, etc.), returning instant scannable results in <15ms.
  * **Interactive Web Demo Upgrade**:
    * Added Category Filter Pills on the main shelf tab (Ready-to-Eat Mixes, Sweets, Jams, Noodles, Snacks, Singapore Retail).
    * Enhanced high-contrast EAN-13 barcode & QR generation for universal items.
    * Displays Cookware & Packaging Leaching warnings (e.g. Styrofoam #6 styrene hazards for hot instant noodles; tin corrosion warning for open sweet cans; retort pouch boiling warnings).
* [x] **Android Mobile Application Experience & Personalized Contraindication Engine (Completed):**
  * **Brand & Aesthetic Mandate Delivered**:
    * Zero developer clutter: Eliminated all "Server online" tech badges and status counters.
    * **Palette**: Crisp White (`#FFFFFF`) and warm sunny off-white / light cream-yellow (`#FFFDF5`, `#FEF9E7`, `#FFF6D8`) background canvas; deep black (`#0F0D0C`) and very very dark brown (`#1A1412`) text.
    * **Typography**: `Plus Jakarta Sans` exclusively with **thick bold weights** (`700`, `800`), bold letter-spacing, and high contrast.
  * **Screen 1: Clean Sign-In & Onboarding**:
    * One-tap Continue with Google, Phone Number, and Email.
    * Quick 1-click test profiles: **Alex Tan** (Hypertension · Peanuts · BP Meds) and **Sarah Lim** (Diabetes · Gluten · Metformin).
  * **Interactive Conversational AI Onboarding**:
    * Replaced rigid static form with an interactive step-by-step AI Clinical Assistant dialogue.
    * Guides the user through: 1. Name & Age, 2. Dietary Rules (custom write-in + chips), 3. Allergies (custom write-in + chips), 4. Chronic Conditions (Hypertension, Diabetes, GERD, etc.), 5. Daily Medications (ACE/ARB, Statins, Metformin), 6. Avoided Additives (Palm oil, MSG, TBHQ).
    * Curates the profile and saves it locally in `localStorage`.
  * **5-Tab Native Mobile App Architecture with Bottom Navigation Bar**:
    * Pinned bottom navigation bar:
      1. **Home**: Search bar, prominent **Scan Product Barcode** CTA, **Scan Ingredients OCR** CTA, **Recent Scans** history preview, Cookware and Hawker shortcuts. Removed hardcoded header pills and random sample shelf.
      2. **Scan**: Dedicated Camera Viewfinder (barcode & OCR modes) + manual barcode input.
      3. **AI Assistant**: Personalized Clinical Nutritionist AI chat interface tailored to the user's medications and conditions.
      4. **History**: Full offline chronological log of all scanned products with colored Nutri-Grade badges, fit verdict, and timestamp.
      5. **Settings**: View/edit clinical profile, trigger AI re-setup, manage on-device offline engine.
  * **Scan Result Bottom Sheet (100% Emoji-Free & Systematic Colored Ratings)**:
    * **Colored Nutri-Grade Ratings**: Grade A (`#00C853`), Grade B (`#64DD17`), Grade C (`#FFD600`), Grade D (`#FF9100`), Grade E (`#FF3D00`), Grade F (`#D50000`), Grade X (`#991B1B`).
    * **Top Highlighted Section: NOT A FIT FOR YOU**: Itemized clinical alerts detailing exact allergen triggers, chronic condition hazards (e.g. sodium expanding blood volume for hypertension), and drug blunting mechanisms.
    * **Good Ingredients Section**: Wholesome real nutrients with biological benefits.
    * **Bad Ingredients Section**: Flagged additives (palm oil, liquid glucose, TBHQ, sodium benzoate, caramel IV, azo dyes) with clinical hazard reasons.
    * **Full Ingredients Formula**: Dedicated card displaying complete ingredients text with bad ingredients highlighted, plus a **Read Aloud** button using Web Speech Synthesis API to read ingredients aloud to the user.
    * **Cross-Border Recipe Disparity**: Western vs. Asian recipe comparison.
    * **Cleaner Swap & Packaging Safety**: Contextual cleaner swap recommendations tailored to specific food categories (e.g. pure raw organic cacao whisked in milk with cinnamon and dates for malt drinks) replacing generic "choose certified" messages.
    * **Zero Developer Jargon**: Stripped all developer preference and status cards ("On-Device Offline Engine", "100% Offline Capable") from consumer views.
    * **Clinical Safety Hard Blocker**: If a product has missing or empty ingredient stubs (< 10 chars), the system marks it as `UNVERIFIED FORMULA` and prompts for back-of-pack OCR scanning, never declaring it safe.
    * **Formula Interval Highlighter**: Safe interval-based highlighting with zero tag nesting: Red bold badges for saved allergens (`.formula-badge.allergen`), amber badges for harmful additives (`.formula-badge.additive`), and green badges for wholesome ingredients (`.formula-badge.good`).
    * **Sticky Bottom Navigation Bar Stability**:
      * Pinned bottom navbar (`z-index: 1000`) with zero scrolling or jumping.
      * Auto-hides when bottom sheet result popup (`z-index: 2001`) or camera viewfinder opens via `.sheet-open` class.
      * Includes `visualViewport` resize listener and `focusin`/`focusout` handlers to prevent navbar from popping up when mobile virtual keyboard is displayed.
      * Added `padding-bottom: 96px;` to `.tab-body` so all content scrolls freely above the fixed navbar.
    * **Hardware-Accelerated Fast Barcode Scanner**:
      * Configured `Html5Qrcode` with explicit `formatsToSupport: [EAN_13, UPC_A, EAN_8, UPC_E, CODE_128, QR_CODE]` to stop lagging on mobile by eliminating unnecessary 2D symbologies.
      * Increased scanning rate to `fps: 20` with native `BarcodeDetector` support and 1.333 horizontal aspect ratio.
      * Added debounced scan lock (`isScanningLocked`) with haptic feedback to prevent request flooding.
  * **IBM Telum AI Model on LinuxONE (`s390x`)**:
    * Trained and deployed a scikit-learn TF-IDF + LogisticRegression model on 100,000 labeled products on the IBM Telum processor: `/home/linux1/macrio/models/macrio_telum_nutrigrade_ai.joblib`.
    * Dedicated backend inference endpoint: `POST /api/v1/ai/audit` classifies formulations into Nutri-Grades A, B, C, D, E with class probabilities in < 1ms.
    * Client weights exported at `GET /api/v1/ai/weights` (359 KB) for on-device inference.
    * Integrated into the app's **AI** tab: "IBM Telum On-Chip Formula Auditor" allows typing or pasting any ingredient list to get an instant AI audit.
* [ ] **Next Active Milestones:**
  * Native Android APK packaging (Capacitor / Android Studio wrapper).
  * On-device OCR Camera stream for live AR overlay.
