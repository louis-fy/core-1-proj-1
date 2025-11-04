import os
import random
from PIL import Image

INPUT_FOLDER = "images_original/"

OUTPUT_FOLDER = "masks/"

IMAGE_WIDTH = 300
IMAGE_HEIGHT = 200
SQUARE_SIZE = 10

NUM_MASKS_TO_CREATE = 16

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
source_files = [f for f in os.listdir(INPUT_FOLDER) 
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]

for i in range(NUM_MASKS_TO_CREATE):
    try:
        source_filename = random.choice(source_files)
        source_path = os.path.join(INPUT_FOLDER, source_filename)
        img = Image.open(source_path)

        img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT)).convert("RGB")

        squares_list = []

        for y in range(0, IMAGE_HEIGHT, SQUARE_SIZE):  # 0, 10, 20, ... 190
            for x in range(0, IMAGE_WIDTH, SQUARE_SIZE): # 0, 10, 20, ... 290
                
                box = (x, y, x + SQUARE_SIZE, y + SQUARE_SIZE)
                square = img.crop(box)
                squares_list.append(square)
        
        random.shuffle(squares_list)
   
        mask_image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT))
        
    
        square_index = 0
        for y in range(0, IMAGE_HEIGHT, SQUARE_SIZE):
            for x in range(0, IMAGE_WIDTH, SQUARE_SIZE):
                paste_position = (x, y)
                mask_image.paste(squares_list[square_index], paste_position)
                square_index += 1

        mask_filename = f"mask_{i+1:02d}.jpg"
        mask_path = os.path.join(OUTPUT_FOLDER, mask_filename)
        mask_image.save(mask_path, "JPEG", quality=95)
  