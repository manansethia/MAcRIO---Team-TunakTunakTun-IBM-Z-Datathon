"""
Update Image URLs for Universal Catalog, Prime Supermarket items, and Singapore Hawker Dishes
in PostgreSQL on IBM LinuxONE s390x.
"""
import psycopg2

DB_CONFIG = {
    "dbname": "macrio_db",
    "user": "macrio",
    "password": "macrio_secret",
    "host": "localhost",
    "port": 5432
}

UNIVERSAL_IMAGES = {
    "8901042957319": "https://images.openfoodfacts.org/images/products/890/104/295/7319/front_en.26.400.jpg",
    "8901042957517": "https://images.openfoodfacts.org/images/products/890/104/295/7517/front_en.4.400.jpg",
    "8901042954516": "https://images.openfoodfacts.org/images/products/890/104/295/4516/front_en.11.400.jpg",
    "8901155101111": "https://images.openfoodfacts.org/images/products/890/115/510/1111/front_en.18.400.jpg",
    "8901155103320": "https://images.openfoodfacts.org/images/products/890/115/510/3320/front_en.15.400.jpg",
    "8901155410312": "https://images.openfoodfacts.org/images/products/890/115/541/0312/front_en.10.400.jpg",
    "8904004405910": "https://images.openfoodfacts.org/images/products/890/400/440/5910/front_en.12.400.jpg",
    "8904004405934": "https://images.openfoodfacts.org/images/products/890/400/440/5934/front_en.12.400.jpg",
    "8904063202819": "https://images.openfoodfacts.org/images/products/890/406/320/2819/front_en.15.400.jpg",
    "6568465511096": "https://images.openfoodfacts.org/images/products/656/846/551/1096/front_en.5.400.jpg",
    "8906004450011": "https://images.openfoodfacts.org/images/products/890/600/445/0011/front_en.10.400.jpg",
    "8901719101037": "https://images.openfoodfacts.org/images/products/890/171/910/1037/front_en.30.400.jpg",
    "8901030922787": "https://images.openfoodfacts.org/images/products/890/103/092/2787/front_en.3.400.jpg",
    "8901030831690": "https://images.openfoodfacts.org/images/products/890/103/083/1690/front_en.6.400.jpg",
    "8901030534898": "https://images.openfoodfacts.org/images/products/890/103/053/4898/front_en.4.400.jpg",
    "8901044200284": "https://images.openfoodfacts.org/images/products/890/104/420/0284/front_en.8.400.jpg",
    "8901058117783": "https://images.openfoodfacts.org/images/products/890/105/811/7783/front_en.10.400.jpg",
    "8901058851298": "https://images.openfoodfacts.org/images/products/890/105/885/1298/front_en.15.400.jpg",
    "8901058022223": "https://images.openfoodfacts.org/images/products/890/105/802/2223/front_en.12.400.jpg",
    "8901058890624": "https://images.openfoodfacts.org/images/products/890/105/889/0624/front_en.10.400.jpg",
    "8901595852504": "https://images.openfoodfacts.org/images/products/890/159/585/2504/front_en.10.400.jpg",
    "8906010060013": "https://images.openfoodfacts.org/images/products/890/601/006/0013/front_en.12.400.jpg",
    "8901014002542": "https://images.openfoodfacts.org/images/products/890/101/400/2542/front_en.10.400.jpg",
    "8901063012219": "https://images.openfoodfacts.org/images/products/890/106/301/2219/front_en.15.400.jpg",
    "8901491101019": "https://images.openfoodfacts.org/images/products/890/149/110/1019/front_en.18.400.jpg",
    "8901233010022": "https://images.openfoodfacts.org/images/products/890/123/301/0022/front_en.10.400.jpg",
    "8901262030663": "https://images.openfoodfacts.org/images/products/890/126/203/0663/front_en.14.400.jpg"
}

PRIME_IMAGES = {
    "8888082001016": "https://images.openfoodfacts.org/images/products/888/808/200/1016/front_en.15.400.jpg",
    "8888082218001": "https://images.openfoodfacts.org/images/products/888/808/221/8001/front_en.15.400.jpg",
    "8000500179864": "https://images.openfoodfacts.org/images/products/800/050/017/9864/front_en.80.400.jpg",
    "7622210080614": "https://images.openfoodfacts.org/images/products/762/221/008/0614/front_en.75.400.jpg",
    "8888001000014": "https://images.openfoodfacts.org/images/products/888/800/100/0014/front_en.20.400.jpg",
    "8998866200226": "https://images.openfoodfacts.org/images/products/899/886/620/0226/front_en.100.400.jpg",
    "9300657005184": "https://images.openfoodfacts.org/images/products/930/065/700/5184/front_en.30.400.jpg",
    "7622210283206": "https://images.openfoodfacts.org/images/products/762/221/028/3206/front_en.45.400.jpg",
    "8888196112110": "https://images.openfoodfacts.org/images/products/888/819/611/2110/front_en.15.400.jpg",
    "8888004010010": "https://images.openfoodfacts.org/images/products/888/800/401/0010/front_en.10.400.jpg"
}

HAWKER_IMAGES = {
    "Hainanese Chicken Rice": "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=600&auto=format&fit=crop&q=80",
    "Katong Laksa": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=600&auto=format&fit=crop&q=80",
    "Char Kway Teow": "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=600&auto=format&fit=crop&q=80",
    "Traditional Kaya Toast Set": "https://images.unsplash.com/photo-1525351484163-7529414344d8?w=600&auto=format&fit=crop&q=80",
    "Fried Hokkien Prawn Mee": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=600&auto=format&fit=crop&q=80",
    "IJOOZ Fresh Squeezed Orange Juice": "https://images.unsplash.com/photo-1613478223719-2ab802602423?w=600&auto=format&fit=crop&q=80",
    "Bak Kut Teh (Pork Rib Soup)": "https://images.unsplash.com/photo-1547592180-85f173990554?w=600&auto=format&fit=crop&q=80",
    "Roti Prata with Fish Curry": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&auto=format&fit=crop&q=80",
    "Mee Goreng Mamak": "https://images.unsplash.com/photo-1612927601601-6638404737ce?w=600&auto=format&fit=crop&q=80",
    "Fried Carrot Cake (Chai Tow Kway)": "https://images.unsplash.com/photo-1541544741938-0af808871cc0?w=600&auto=format&fit=crop&q=80"
}

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    print("Updating universal_fmcg_catalog image URLs...")
    for barcode, img in UNIVERSAL_IMAGES.items():
        cur.execute("UPDATE universal_fmcg_catalog SET image_url = %s WHERE barcode = %s;", (img, barcode))

    print("Updating prime_supermarket_proof image URLs...")
    for barcode, img in PRIME_IMAGES.items():
        cur.execute("UPDATE prime_supermarket_proof SET image_url = %s WHERE barcode_ean13 = %s;", (img, barcode))

    print("Updating singapore_hawker_dishes image URLs...")
    for dish, img in HAWKER_IMAGES.items():
        cur.execute("UPDATE singapore_hawker_dishes SET image_url = %s WHERE dish_name = %s;", (img, dish))

    conn.commit()
    cur.close()
    conn.close()
    print("Database image URLs successfully populated!")

if __name__ == "__main__":
    main()
