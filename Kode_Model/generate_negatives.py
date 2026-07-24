import os
import random
from PIL import Image, ImageDraw, ImageFont

def generate_random_sharp_image(output_path, width=224, height=224):
    # Random solid background
    bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw random sharp geometric shapes
    for _ in range(random.randint(5, 20)):
        shape_type = random.choice(['rect', 'circle', 'line', 'polygon'])
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        x0, y0 = random.randint(0, width), random.randint(0, height)
        x1, y1 = random.randint(0, width), random.randint(0, height)
        
        # Ensure coordinates are in correct order for bounding box
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        
        if shape_type == 'rect':
            draw.rectangle([x0, y0, x1, y1], fill=color, outline=(0,0,0), width=2)
        elif shape_type == 'circle':
            draw.ellipse([x0, y0, x1, y1], fill=color, outline=(255,255,255), width=2)
        elif shape_type == 'line':
            draw.line([x0, y0, x1, y1], fill=color, width=random.randint(1, 10))
        elif shape_type == 'polygon':
            points = [(random.randint(0, width), random.randint(0, height)) for _ in range(3, 6)]
            draw.polygon(points, fill=color)

    # Optionally draw some random grids (like UI)
    if random.random() > 0.5:
        for i in range(0, width, random.randint(20, 50)):
            draw.line([(i, 0), (i, height)], fill=(128,128,128), width=1)
        for i in range(0, height, random.randint(20, 50)):
            draw.line([(0, i), (width, i)], fill=(128,128,128), width=1)
            
    img.save(output_path)

def main():
    output_dir = r"D:\KP\Dataset_Dan_Gambar\negative_pool"
    os.makedirs(output_dir, exist_ok=True)
    
    target_count = 350
    print(f"Generating {target_count} random sharp geometric images to {output_dir}...")
    
    for i in range(target_count):
        file_path = os.path.join(output_dir, f"neg_gen_{i}.jpg")
        generate_random_sharp_image(file_path, width=224, height=224)
        if (i+1) % 50 == 0:
            print(f"Generated {i+1}/{target_count} images...")
            
    print("Finished generating all images.")

if __name__ == '__main__':
    main()
