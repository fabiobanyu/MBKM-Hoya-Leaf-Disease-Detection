import os
import requests
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_image(i, output_dir):
    url = f"https://picsum.photos/500/500?random={i}"
    file_path = os.path.join(output_dir, f"neg_{i}.jpg")
    if os.path.exists(file_path):
        return True
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        pass
    return False

def main():
    output_dir = r"D:\KP\Dataset_Dan_Gambar\negative_pool"
    os.makedirs(output_dir, exist_ok=True)
    
    target_count = 350
    valid_ids = range(1, target_count + 100)
    
    print(f"Downloading {target_count} high-res negative images to {output_dir}...")
    
    success_count = 0
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(download_image, img_id, output_dir): img_id for img_id in valid_ids}
        for future in as_completed(futures):
            if future.result():
                success_count += 1
                if success_count % 50 == 0:
                    print(f"Downloaded {success_count}/{target_count} images...")
            if success_count >= target_count:
                print("Target reached. Cancelling remaining tasks.")
                break
                
    print(f"Finished downloading {success_count} images.")

if __name__ == '__main__':
    main()
