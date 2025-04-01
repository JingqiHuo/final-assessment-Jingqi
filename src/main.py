import rasterio
import glob
from batch_process import get_image_filenames,generate_tiff
from rasterio.merge import merge
from merge_2015 import task3_merge2015

if __name__=="__main__":
    #filepath_2009 = '/geos/netdata/oosa/assignment/lvis/2009/*.h5'
    #filepath_2015 = '/geos/netdata/oosa/assignment/lvis/2015/*.h5'
    #filelist_2009 = glob(filepath_2009)
    #filelist_2015 = glob(filepath_2015)
    #print(filelist_2009+filelist_2015)
    #print("Program paused. Press Enter to continue...")
    #input()  
    #testpath ='/geos/netdata/oosa/assignment/lvis/2015/ILVIS1B_AQ2015_1017_R1605_069264.h5'

    #generate_tiff()
    root ='./tifs'
    dirs = get_image_filenames(root)
    # Get the keys of the dictionary in insertion order
    keys = list(dirs.keys())
    # Delete the first two empty keys
    if len(keys) >= 2:
      del dirs[keys[0]]
      del dirs[keys[1]]
    temp = 0
    # Loop over the folders containing tiffs
    # dir_folder is the name of folder (same name with hdf5 file), means currently the program is working on 
    for dir_folder, dir_images in dirs.items():
        print(dir_folder)
        
        if( '2015' in dir_folder):
          root ='./tifs/2015/'
        else:
          root ='./tifs/2009/'
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

        # Write the mosaic to a new file
        output_file = f'./output/merged_output{dir_folder}.tif'
        with rasterio.open(output_file, 'w', **out_meta) as dest:
            dest.write(mosaic)

        # Optionally, display the merged DEM
        #show(mosaic, cmap='terrain')
        #plt.title("Merged TIFF Image")
        #plt.show()

        # Close all files
        for src in src_files_to_mosaic:
            src.close()
        root_path=temp
    task3_merge2015()