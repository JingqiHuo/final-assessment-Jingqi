from pathlib import Path
import click
import os
from glob import glob
from newClass import plotLVIS
import numpy as np
 
def get_image_filenames(directory):
    images_in_folders = {}
    # Use rglob to find all directories and subdirectories
    for subfolder in Path(directory).rglob('*'):
        if subfolder.is_dir():
            image_files = [f.name for f in subfolder.iterdir() if f.is_file()]
            images_in_folders[subfolder.name] = image_files
    return images_in_folders

@click.command()
@click.option('--file-path', 'file_path', required=True, help='Path to the files to process.')
def generate_tiff(file_path):
  # Loop over the filelists and construct paths
    filelist = glob(file_path)
    if '2015' in filelist[0]:
      out_root_pr ='./tifs/2015/'
    else:
      out_root_pr ='./tifs/2009/'
    for filename in filelist:
        
        # Extract the file name without the extension
        file_name = os.path.splitext(os.path.basename(filename))[0]

        # Define the new directory path
        out_root = os.path.join(out_root_pr, file_name)
        out_root = out_root + '/'
        print(out_root)
        # Create the new directory if it doesn't exist
        os.makedirs(out_root, exist_ok=True)

        print('Processing: ' + str(filename))
        
        
        # create instance of class with "onlyBounds" flag
        b=plotLVIS(filename,onlyBounds=True)

        # set a step size
        step=(b.bounds[2]-b.bounds[0])/5

        # below, (x0,y0) is the bottom left corner of our tile
        #   (x1,y1) is the top right corner of our tile

        # loop over spatial subsets
        for x0 in np.arange(b.bounds[0],b.bounds[2],step):  # loop over x tiles
          x1=x0+step   # the right side of the tile
          for y0 in np.arange(b.bounds[1],b.bounds[3],step):  # loop over y tiles
            y1=y0+step  # the top of the tile

            # print the bounds to screen as a sanity check
            print("Tile between",x0,y0,"to",x1,y1)

            # read in all data within our spatial subset
            lvis=plotLVIS(filename,minX=x0,minY=y0,maxX=x1,maxY=y1,setElev=True)
            # check that it contains some data
            if(lvis.nWaves==0):
              continue

            # plot up some waveforms
            #lvis.plotWaves(step=int(lvis.nWaves/100),outRoot=outRoot+".x."+str(x0)+".y."+str(y0))  # this will print 100 waveforms
            
            # updating the filename as it goes
            # to make a DEM as a geotiff
            lvis.reprojectLVIS(3031) # reproject the data to local UTM zone
            lvis.estimateGround()    # find ground elevations
            outName = f"{out_root}lvisDEM.x.{x0}.y.{y0}.tif"  # set output filename
            lvis.writeDEM(30,outName)                         # write data to a DEM at 30 m resolution