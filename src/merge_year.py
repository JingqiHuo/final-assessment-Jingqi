import os
import glob
import rasterio
from rasterio.merge import merge
from osgeo import gdal

def task3_merge(year):
    # path to the folder containing tif files
    in_path = str('./output/' + year + '/')
    out_path = './task3'
    print(f"Merging files from {year}...")
    # get all the file names of tif file
    input_files = glob.glob(os.path.join(in_path, "*.tif"))
    
    # Check if can get the file names
    if not input_files:
        raise FileNotFoundError(f"tif files not found, please check if the path {in_path} is right")
    
    # read all tif files
    files_mosaic = [rasterio.open(f) for f in input_files]
    
    # Merge
    mosaic, out_trans = merge(files_mosaic)
    
    # Read and update metadata
    out_meta = files_mosaic[0].meta.copy()
    out_meta.update({"driver": "GTiff",
                     "height": mosaic.shape[1],
                     "width": mosaic.shape[2],
                     "transform": out_trans})
    
    # Output file
    out_name = str(year + "final.tif")
    out_file = os.path.join(out_path, out_name)
    
    # Save output file
    with rasterio.open(out_file, "w", **out_meta) as dest:
        dest.write(mosaic)
    
    # Close all the opened files
    for src in files_mosaic:
        src.close()
    
    # Reminder
    print(f"{year} data merge completed.")
    return