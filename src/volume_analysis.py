import rasterio
import numpy as np
import os
from rasterio.warp import Resampling


class volume_analysis:
    def __init__(self, dem_path_1, dem_path_2):
        """Initialize, loading two DEM files"""
        self.dem_path_1 = dem_path_1
        self.dem_path_2 = dem_path_2
        self.dem1, self.transform, self.profile = self.read_tiff(dem_path_1)
        self.dem2, _, _ = self.read_tiff(dem_path_2)

    def read_tiff(self, tiff_path):
        """Read geotiff data and return arrays, transform and metadata"""

        # Debugging
        if not os.path.exists(tiff_path):
            raise FileNotFoundError(f"File not found: {tiff_path}")

        with rasterio.open(tiff_path) as dataset:
            dem_data = dataset.read(1).astype(np.float32)  # Read the first band
            transform = dataset.transform  # Get the geo-transform
            profile = dataset.profile  # Get the metadata
        return dem_data, transform, profile

    def resample_raster(dem1_in, dem2_ref_in, dem1_out):
        """Resample two DEMs to the same resolution and size in order to process calculation"""
        print("Resampling DEMs...")
        with rasterio.open(dem2_ref_in) as ref:
            ref_profile = ref.profile
            ref_transform = ref.transform
            ref_height = ref.height
            ref_width = ref.width

        with rasterio.open(dem1_in) as src:
            data = src.read(
                out_shape=(src.count, ref_height, ref_width),
                resampling=Resampling.bilinear
            )

            # Update metadata
            profile = src.profile
            profile.update({
                "height": ref_height,
                "width": ref_width,
                "transform": ref_transform
            })

            # Save as new file
            with rasterio.open(dem1_out, 'w', **profile) as dst:
                dst.write(data)
    
    def compute_elevation_change(self):
        """Calculate the variation of elevation"""
        # Get the sharing zones between two DEMs, ignoring nodata zones
        
        mask = (self.dem1 != self.profile["nodata"]) & (self.dem2 != self.profile["nodata"])
        elevation_diff = np.where(mask, self.dem2 - self.dem1, 0)  # Calculate the variation
        return elevation_diff

    def compute_volume_change(self):
        """Calculate the varriation of volume"""
        elevation_diff = self.compute_elevation_change()

        # Calculate the zones area
        pixel_width = abs(self.transform.a)  # Width
        pixel_height = abs(self.transform.e)  # Height
        pixel_area = pixel_width * pixel_height  # Area of each pixel(square meter)

        # Calculate the total volume variation (Variation of elevation x area of pixels)
        volume_change = np.sum(elevation_diff) * pixel_area  # Cubic meter
        Sea_level_change = (-100)*volume_change/3.6e14 # Centimeter
        return volume_change, Sea_level_change

    def save_elevation_difference_tiff(self, output_path):
        """Save the geotiff file indicating variation of elevation"""

        print('Saving variation results...')
        elevation_diff = self.compute_elevation_change()

        # Updata metadata
        self.profile.update(dtype=rasterio.float32, count=1)

        # Save as tif file
        with rasterio.open(output_path, 'w', **self.profile) as dst:
            dst.write(elevation_diff, 1)
        
        print(f"Variation image saved to: {output_path}")

    def report_results(self):
        """Print results of analysis"""
        volume_change, Sea_level_change = self.compute_volume_change()
        print(f"Total volume variation: {volume_change:.2f} m\u00B3")
        print(f"Estimated sea level variation: {Sea_level_change:.2f} cm")
        return volume_change
