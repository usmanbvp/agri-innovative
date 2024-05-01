from PIL import Image
import os

def resize_images(folder_path, new_width, new_height):
    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        # Check if the file is an image (you may need to add more file extensions)
        if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
            # Open the image
            image_path = os.path.join(folder_path, filename)
            img = Image.open(image_path)
            
            # Resize the image
            resized_img = img.resize((new_width, new_height))
            
            # Save the resized image, overwriting the original file
            resized_img.save(image_path)
            print(f"Resized {filename} to {new_width}x{new_height}")

# Path to the folder containing images
folder_path = "static/images/fertilizer_images"

# New dimensions
new_width = 250
new_height = 300

# Resize images
resize_images(folder_path, new_width, new_height)
