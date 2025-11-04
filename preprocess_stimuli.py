from PIL import Image
import os

input_folder = "images_original/"
output_folder = "images_resized/"

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith((".png", ".jpg", ".bmp")):
        img = Image.open(os.path.join(input_folder, filename))
        img_resized = img.resize((300, 200))  # h200，w300
        new_filename = f"{filename}.jpg"
        img_resized.save(os.path.join(output_folder, new_filename))
        print(f"Resized: {new_filename}")