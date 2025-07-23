import os
from PIL import Image

# Define the base screenshots path
base_path = "/Users/ag/Payatu/Selenium/screenshots"

# Supported image formats
image_extensions = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"]

# Function to convert images in a folder to a PDF
def images_to_pdf(folder_path):
    images = []
    for file in sorted(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and os.path.splitext(file)[1].lower() in image_extensions:
            try:
                img = Image.open(file_path).convert("RGB")
                images.append(img)
            except Exception as e:
                print(f"Error loading image {file_path}: {e}")
    
    if images:
        folder_name = os.path.basename(folder_path)
        output_path = os.path.join(folder_path, f"{folder_name} output.pdf")
        images[0].save(output_path, save_all=True, append_images=images[1:])
        print(f"Saved PDF in: {output_path}")
    else:
        print(f"No valid images found in: {folder_path}")

# Iterate through all folders in the base_path
for folder in sorted(os.listdir(base_path)):
    folder_path = os.path.join(base_path, folder)
    if os.path.isdir(folder_path):
        images_to_pdf(folder_path)