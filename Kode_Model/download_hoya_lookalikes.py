# Fast Downloader for Houseplant Hard Negatives (iNaturalist API)
import os
import sys
import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

OUTPUT_DIR = r"D:\KP\Dataset_Dan_Gambar\negative_leaves"

TARGET_SPECIES = [
    {"name": "Crassula ovata", "query": "Crassula ovata", "count": 30},
    {"name": "Dischidia", "query": "Dischidia", "count": 30},
    {"name": "Peperomia obtusifolia", "query": "Peperomia obtusifolia", "count": 30},
    {"name": "Stephanotis floribunda", "query": "Stephanotis floribunda", "count": 30},
    {"name": "Zamioculcas zamiifolia", "query": "Zamioculcas zamiifolia", "count": 30},
]

headers = {'User-Agent': 'Mozilla/5.0'}

def fetch_image_urls():
    download_tasks = []
    for sp in TARGET_SPECIES:
        name = sp["name"]
        query = sp["query"]
        target = sp["count"]
        clean_name = name.replace(" ", "_")
        
        url = f"https://api.inaturalist.org/v1/observations?q={urllib.parse.quote(query)}&photos=true&per_page={target}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                results = data.get("results", [])
                
                count = 0
                for obs in results:
                    photos = obs.get("photos", [])
                    if photos:
                        p = photos[0]
                        p_url = p.get("url", "").replace("square.jpg", "medium.jpg")
                        if p_url:
                            pid = p.get("id", count)
                            dest = os.path.join(OUTPUT_DIR, f"lookalike_{clean_name}_{pid}.jpg")
                            download_tasks.append((p_url, dest))
                            count += 1
                            if count >= target:
                                break
        except Exception as e:
            print(f"Error fetching {name}: {e}")
            
    return download_tasks

def download_one(task):
    url, dest = task
    if os.path.exists(dest):
        return True
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp, open(dest, 'wb') as f:
            f.write(resp.read())
        return True
    except Exception:
        return False

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Fetching image metadata from iNaturalist...")
    tasks = fetch_image_urls()
    print(f"Total images queued for download: {len(tasks)}")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(download_one, tasks))
        
    success = sum(1 for r in results if r)
    print(f"Downloaded {success}/{len(tasks)} houseplant lookalike images into {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
