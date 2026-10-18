# MAcRIO — Instructions & Developer Information

## 1. Project Overview
* **Name:** MAcRIO (Cross-Border Food Scanner & Utensil Safety Platform)
* **Target Architecture:** IBM LinuxONE `s390x` (Ubuntu 24.04 LTS)
* **Backend:** Python (FastAPI), PostgreSQL, Docker (`linux/s390x`)
* **Hardware Acceleration:** IBM Telum on-chip AI processor
* **Privacy:** IBM Hyper Protect Virtual Servers (HPVS)
* **Client Apps:** Android & iOS

---

## 2. Server Access Setup
To allow the AI assistant and developer tools to connect to your LinuxONE instance:
1. Open [server_login.txt](file:///Users/manan/Documents/TunakTunakTun_MAcRIO_IBMZ/server_login.txt).
2. Paste your connection details in one of the following formats:
   ```text
   ssh -i /path/to/key.pem ubuntu@<IP_ADDRESS> -p 22
   ```
   or:
   ```text
   Host: <IP_OR_HOSTNAME>
   Port: 22
   User: ubuntu
   Password: <PASSWORD>
   KeyPath: /path/to/id_rsa
   ```

---

## 3. Super Dataset Compilation Workflow

The MAcRIO database aggregates five key layers into a single queryable PostgreSQL database on IBM LinuxONE:

### A. Packaged Foods & Barcodes (Global vs Regional)
* **Open Food Facts Global Dump:** Currently downloading as `cts.jsonl.gz` (`openfoodfacts-products.jsonl.gz`, ~14GB compressed).
* **Streaming Parser:** Filter by country tags (`en:india`, `en:singapore`, `en:malaysia`, `en:indonesia`, `en:united-states`, `en:european-union`) to reduce memory footprint and extract target barcodes and ingredients.
* **Kaggle BigBasket Dataset:** Indian packaged goods baseline (~27.5k items).
* **USDA FoodData Central:** US nutritional and ingredient baseline (350k branded products).

### B. Regional Street Food & Macro Datasets
* **India:** ICMR-NIN IFCT 2017 (`@ifct2017/compositions` / Kaggle `ifct2017`).
* **Singapore:** HPB SG FoodID (Health Promotion Board Singapore).
* **Malaysia:** MyFCD (Malaysian Food Composition Database) & `myFood11`.
* **Indonesia:** TKPI (Tabel Komposisi Pangan Indonesia / Panganku).

### C. Influencer & Cleaner Swaps
* **Food Pharmer ("Label Padhega India" by Revant Himatsingka):**
  * Palm oil substitutions (Maggi, biscuits, snacks).
  * High sugar & maltodextrin (Bournvita, health drinks).
  * Caramel color / disguised refined flour (Brown breads).
  * Curated Clean Brands Directory (`foodpharmer.health/brands`).
* **TruthIn App:** Indian consumer packaged food rating framework.
* **Yuka Additive Hazard Framework:** 4-tier risk classification (Green, Yellow, Orange, Red) for 400+ E-number additives.

### D. Regulatory Additives & Banned Ingredients Matrix
* **EFSA (EU):** Banned Titanium Dioxide (E171), compulsory warning on Azo dyes (E102, E110, E122, E129).
* **FDA (US):** Status on BVO, Potassium Bromate, and High Fructose Corn Syrup.
* **FSSAI (India):** Mandatory front-of-pack labeling rules and additive limits.
* **SFA (Singapore):** Nutri-Grade (A to D) beverage regulations and sodium reduction guidelines.

### E. Utensil & Plastic Safety Computer Vision
* **Resin Identification Codes (RIC 1 to 7):** Kaggle *Plastic Recycling Codes* dataset + Roboflow YOLO models.
* **Cookware Degradation:** Scratched non-stick PTFE (Teflon) and pitted aluminum cookware classification.

---

## 4. Key References & Documentation
* [MAcRIO Solution & Architecture Overview PDF](file:///Users/manan/Documents/TunakTunakTun_MAcRIO_IBMZ/MAcRIO%20Solution%20&%20Architecture%20Overview.pdf)
* [MAcRIO Memory & Thinking Logbook](file:///Users/manan/Documents/TunakTunakTun_MAcRIO_IBMZ/memory.md)
* [Server Login Details](file:///Users/manan/Documents/TunakTunakTun_MAcRIO_IBMZ/server_login.txt)
