import cv2
import numpy as np
import rasterio
from rasterio.transform import from_origin
import os

def read_and_preprocess_tiff(tiff_path):
    """ Read tif file and convert it into an 8-bit image """

    # Raise error
    if not os.path.exists(tiff_path):
        raise FileNotFoundError(f"File not found: {tiff_path}")

    # Read the first wave band
    with rasterio.open(tiff_path) as dataset:
        image = dataset.read(1) 
    
    # Standarize and convert into 8-bit
    image_8bit = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    return image_8bit

def connect_nearest_contours(img):
    """ Connect the routes' contours """

    # Convert to rgb in order to draw lines
    img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)  

    # Convert pixels into 0(black) and 1(white)
    _, th = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY)

    # Morphological expansion, easier to draw the lines
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19))
    morph = cv2.morphologyEx(th, cv2.MORPH_DILATE, kernel)

    # Detect the boundries
    cnts, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Loop over every boundry, calculate the endpoints
    points = []
    for c in cnts:
        left = tuple(c[c[:, :, 0].argmin()][0])
        right = tuple(c[c[:, :, 0].argmax()][0])
        top = tuple(c[c[:, :, 1].argmin()][0])
        bottom = tuple(c[c[:, :, 1].argmax()][0])
        points.append({"left": left, "right": right, "top": top, "bottom": bottom})

    # For drawing the filling lines
    line_thickness = 15  # 15 for default

    # Connect the closest endpoints
    for i in range(len(points)):
        min_dist = float("inf")
        best_pair = None

        for j in range(i + 1, len(points)):
            for pt1 in points[i].values():
                for pt2 in points[j].values():
                    dist = np.linalg.norm(np.array(pt1) - np.array(pt2))
                    if dist < min_dist:
                        min_dist = dist
                        best_pair = (pt1, pt2)

        # Draw the shortest line
        if best_pair:
            cv2.line(img_color, best_pair[0], best_pair[1], (255, 255, 255), thickness=line_thickness)

    # Convert back to grayscale (single channel) for saving as TIFF
    img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

    return img_gray

def save_as_tiff(image, output_path, reference_tiff_path):
    """ Save as a tif file """
    with rasterio.open(reference_tiff_path) as dataset:
        # Get tif file's metadata
        profile = dataset.profile
    
    # Ensure the output file is in an 8-bit format
    image = image.astype(np.uint8)

    # Write into a new tif file using rasterio
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(image, 1)  # Write the first band


















