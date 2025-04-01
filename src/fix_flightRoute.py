import numpy as np
from scipy.ndimage import binary_dilation
from osgeo import gdal


def read_flight_route_from_tif(tif_path):
    """
    Read and extract flight route data from tif files.
    """

    # Open the file path
    dataset = gdal.Open(tif_path)

    # Get the data of the first band, then convert them into numpy arrays which are easy to be processed
    band = dataset.GetRasterBand(1)
    data = band.ReadAsArray()
    
    # Standarize the raster, set the background to value 0, the route to value 1
    data = np.where(data > 0, 1, 0) 
    
    return data, dataset

def fill_gaps_between_paths(image_data, structure_size=8):
    """
    Use binary dilation to connect flight routes
    """

    # binary dilation is a library that fill the gaps according to the structure size
    # The bigger the structure size is, the bigger gaps it can fill
    dilated_image = binary_dilation(image_data, structure=np.ones((structure_size, structure_size))).astype(np.uint8)
    return dilated_image

def save_filled_route_to_tif(input_tif, output_tif, filled_image, dataset):
    """
    Save the fixed route as a new tif file
    """
    driver = gdal.GetDriverByName('GTiff')
    
    # Get the size of file need to be processed
    raster_x_size = dataset.RasterXSize
    raster_y_size = dataset.RasterYSize

    # Expand W/B (1/0) data to (255/0). Easy for windows to identify
    filled_image = (filled_image * 255).astype(np.uint8)

    # Create the output tif file
    out_dataset = driver.Create(output_tif, raster_x_size, raster_y_size, 1, gdal.GDT_Byte)
    out_band = out_dataset.GetRasterBand(1)
    
    # Set the transform info
    out_dataset.SetGeoTransform(dataset.GetGeoTransform())

    # Set the projection info
    out_dataset.SetProjection(dataset.GetProjection())
    
    # Write in the fixed data
    out_band.WriteArray(filled_image)
    out_dataset.FlushCache()

    # Close the file
    out_dataset = None
    dataset = None

    print(f"Fixed data saved to {output_tif}")
    return













