#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
import os
import sys

def svg_to_ico():
    try:
        # First, check if app_icon.ico already exists
        icon_path = os.path.join('static', 'app_icon.ico')
        svg_path = os.path.join('static', 'app_icon.svg')
        
        if os.path.exists(icon_path):
            print(f"Icon file already exists at {icon_path}")
            return icon_path
        
        # We need to have a PNG interim format since PIL can't read SVG directly
        png_path = os.path.join('static', 'app_icon.png')
        
        if not os.path.exists(png_path):
            print("ERROR: A PNG version of the icon is required for conversion.")
            print("Please convert your SVG to PNG manually using an image editor")
            print(f"and save it as {png_path}")
            return None
        
        # Size sequence for multi-size icon
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img = Image.open(png_path)
        
        # Create a multi-size icon
        icon_images = []
        for size in sizes:
            # Resize the image with high quality
            resized_img = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized_img)
        
        # Save as ICO
        icon_images[0].save(
            icon_path,
            format='ICO',
            sizes=[(img.width, img.height) for img in icon_images],
            append_images=icon_images[1:]
        )
        
        print(f"Icon successfully converted and saved to {icon_path}")
        return icon_path
        
    except Exception as e:
        print(f"Error converting icon: {str(e)}")
        return None

if __name__ == "__main__":
    svg_to_ico() 