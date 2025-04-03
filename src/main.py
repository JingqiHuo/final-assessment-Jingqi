import rasterio
import glob
from batch_process import get_image_filenames,generate_tiff
from rasterio.merge import merge
from merge_year import task3_merge
import matplotlib.pyplot as plt
from Connect_route import save_as_tiff,read_and_preprocess_tiff,connect_nearest_contours
from volume_analysis import volume_analysis


if __name__=="__main__":
   
    # Extract tif files from raw data
    #generate_tiff()
    #generate_tiff()
    root ='./tifs'
    dirs = get_image_filenames(root)
    # Get the keys of the dictionary in insertion order
    keys = list(dirs.keys())
    # Delete the first two empty keys
    if len(keys) >= 2:
      del dirs[keys[0]]
      del dirs[keys[1]]

    # This code chunk is used to merge tif files from every single hdf5 file
    # Loop over the folders containing tif files
    # dir_folder is the name of folder (same name with hdf5 file), means currently the program is working on 
    for dir_folder, dir_images in dirs.items():
        print(dir_folder)
        
        if( '2015' in dir_folder):
          root ='./tifs/2015/'
          year = 2015
        else:
          root ='./tifs/2009/'
          year = 2009
        tif_path = str(root + dir_folder + '/*.tif')
        tif_files = glob.glob(tif_path)

        # Open each file and add them to a list
        src_files_to_mosaic = [rasterio.open(fp) for fp in tif_files]

        # Merge the files
        mosaic, out_trans = merge(src_files_to_mosaic)

        # Copy the metadata from one of the source files
        out_meta = src_files_to_mosaic[0].meta.copy()

        # Update the metadata with new dimensions, transform, and CRS
        out_meta.update({
            "driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_trans,
            "crs": src_files_to_mosaic[0].crs
        })

        # Write the image to a new file
        output_file = f'./output/{year}/merged_output{dir_folder}.tif'
        with rasterio.open(output_file, 'w', **out_meta) as dest:
            dest.write(mosaic)
        print(f'Data saved to {output_file}')

        # Close all files
        for src in src_files_to_mosaic:
            src.close()
        

    input("\nPress enter to process task 3 and 4...\n")
    # Fill the gaps between flight lines
    i = ['2009','2015']
    for year in i: 

      # Process the all files in one year into a single file
      task3_merge(year)

      # Call the gap filling methods
      print(f"Filling gaps in {year} data...")
      tiff_path = f"./task3/{year}final.tif"
      img_8bit = read_and_preprocess_tiff(tiff_path)
      result_img = connect_nearest_contours(img_8bit)

      # Display the results
      #cv2.imshow("Connected Flight Routes", result_img)
      #cv2.waitKey(0)
      #cv2.destroyAllWindows()

      # Save as the result after connecting as a tif file
      print(f"Saving connected data from{year}...")
      output_tiff_path = f"./connected_route/connected{year}.tif"
      save_as_tiff(result_img, output_tiff_path, tiff_path)
      print(f"{year} data saved to {output_tiff_path}")


    input("\nPress enter to process task 5...\n")
    # Analyzing glacier volume variation       
    output_path = "./task5/elevation_change.tif"
    dem_paths = glob.glob("./connected_route/*.tif")
    # Analyzing glacier volume variation
    print("Analyzing glacier volume variation...")
    # Call the resampling method, ensuring two DEMs are in the same size and computable
    volume_analysis.resample_raster(dem_paths[1], dem_paths[0], "./task5/DEM2015_resampled.tif")
    # Create an object for analysis
    analyzer = volume_analysis(dem_paths[0], "./task5/DEM2015_resampled.tif")
    # Calculate and return the infleunce of glacier melt
    analyzer.report_results()
    # Generate the elevation variation file
    analyzer.save_elevation_difference_tiff(output_path)