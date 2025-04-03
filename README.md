# OOSA Assignment 2025

This contains the files needed for the 2025 OOSA assignment. The raw LVIS data can be downloaded from [here](https://lvis.gsfc.nasa.gov/Data/Data_Download.html), but files over the Pine Island Glacier have been provided on the teaching drive.  We will be using files from [Operation IceBridge](https://www.nasa.gov/mission_pages/icebridge/index.html), which bridged the gap between ICESat and ICESat-2 using aircraft.

## Kickstart this program
First of all, navigate to the directory src.
```
cd src
python task1.py --file-path "/geos/netdata/oosa/assignment/lvis/2015/*.h5"
python task1.py --file-path "/geos/netdata/oosa/assignment/lvis/2009/*.h5"
python main.py
```

## lvisClass.py

A class to handle LVIS data. This class reads in LVIS data from a HDF5 file, stores it within the class. It also contains methods to convert from the compressed elevation format and return attributes as numpy arrays. Note that LVIS data is stored in WGS84 (EPSG:4326).

The class is:

**lvisData**

The data is stored as the variables:

    waves:   Lidar waveforms as a 2D numpy array
    lon:     Longitude as a 1D numpy array
    lat:     Latitude as a 1D numpy array
    nWaves:  Number of waveforms in this file as an integer
    nBins:   Number of bins per waveform as an integer
    lZN:     Elevation of the bottom waveform bin
    lZ0:     Elevation of the top waveform bin
    lfid:    LVIS flight ID integer
    shotN:   LVIS shot number for this flight


The data should be read as:

    from lvisClass import lvisData
    lvis=lvisData(filename)


There is an optional spatial subsetter for when dealing with large datasets.

    lvis=lvisData(filename,minX=x0,minY=y0,maxX=x1,maxX=x1)

Where (x0,y0) is the bottom left coordinate of the area of interest and (x1,y1) is the top right.

To help choose the bounds, the bounds only can be read from the file, to save time and RAM:

    lvisData(filename,onlyBounds=True)


The elevations can be set on reading:

    lvis=lvisData(filename,seteElev=True)

Or later by calling the method:

    lvis.setElevations()

This will add the attribute:

    lvis.z:    # 2D numpy array of elevations of each waveform bin


The class includes the methods:

* setElevations(): converts the compressed elevations in to arrays of elevation, z.
* getOneWave(ind): returns one waveform as an array
* dumpCoords():    returns all coordinates as two numpy arrays
* dumpBounds():    returns the minX,minY,maxX,maxY


### Using the class in code

    # import and read bounds
    from lvisClass import lvisData
    bounds=lvisData(filename,onlyBounds=True)
      
    # set bounds
    x0=bounds[0]
    y0=bounds[1]
    x1=(bounds[2]-minX)/2+minX
    y1=(bounds[3]-minY)/2+minY
     
    # read data
    lvis=lvisData(filename,minX=x0,minY=y0,maxX=x1,maxY=y1)
    lvis.setElevations()

This will find the data's bounds, read the bottom left quarter of it in to RAM, then set the elevation arrays. The data is now ready to be processed


## processLVIS.py

Includes a class with methods to process LVIS data. This inherits from **lvisData** in *lvisClass.py*. The initialiser is not overwritten and expects an LVIS HDF5 filename. The following methods are added:

* estimateGround():    Processes the waveforms and z arrays set above to populate self.zG
* reproject():         Reprojects horizontal coordinates
* findStats():         Used by estimateGround()
* denoise(thresh):     Used by estimateGround()

Some parameters are provided, but in all cases the defaults should be suitable. Further information on the signal processing steps and variable names can be found in [this](https://www.sciencedirect.com/science/article/pii/S0034425716304205) paper.


### Using the class in code

    from processLVIS import lvisGround
    lvis=lvisGround(filename)
    lvis.setElevations()
    lvis.estimateGround()

Note that the estimateGround() method can take a long time. It is recommended to perform time tests with a subset of data before applying to a complete file. This will produce an array of ground elevations contained in:

    lvis.zG


## lvisExample.py

Contains an example of how to call processLVIS.py on a 15th of a dataset. Intended for testing only. It could form the centre of a batch loop. It is a simple script with no options.

## task1.py

Contains 3 lines of code, is used to extract data from hdf5 files. Need to be run twice because the particularity of command parse.

## handleTiff.py

Examples of how to write and read a geotiff embedded within a class. This script read a pixels divided by customized resolution (30 in this program), will be run in a for loop in function generate_tiff() and in Class plotLVIS to generate all the fragments of an hdf5 file.

* writeTiff(data):     writes raster data to a geotiff (*data* class needs modifying)

Note that geotiffs read the y axis from the top, so be careful when unpacking or packing data, otherwise the z axis will be flipped.

## newClass.py

A new class inherited from lvisData, including several new methods. 

* reprojectBounds(self,outEPSG):    reprojects bounds to a new projection based on the numeric input by users
* inspectWaves(self):    previews the wave data in a single graph
* plotWaves(self,outRoot="waveform",step=1):    loops over and plot all waveforms
* plotWave(self,i,outroot="waveform"):    saves waveforms as images but not preview

Note: Methods related to wave plotting will be used in extracting the geotiffs from hdf5 files in batch_process.py. But due to the large amount of images to show and no need for intermediate products, it will be commented not to run in batch_process, line 66.

## batch_process.py

Contains methods that will be used in the first step, reading and exporting data from hdf5 files as geotiffs. The click library is used to parse the command line, avoiding hardcode.

* get_image_filenames(directory):    loops over all the directories to get the list of directory names

* generate_tiff(file_path):    reads and finds all the hdf5 files given the year, and writes them into folders aligning to their coordinates and the hdf5 files referring to. It will also create folders for every batch of tif images automatically. It will go through x and y tiles in the preset step so that it divide an hdf5 files into several part and plot them respectively.

## main.py

Main program, contains the code chunks to integrate the geotiffs of every hdf5 file into a complete one. Then, it will merge the complete data referring to their year into one tif file. And fill the and connect gaps between flight lines within the merged geotiffs. Finally, it will analyze the ice volume variation.

## merge_year.py

Merges comgplete geotiffs into one in every 2009 and 2015 respectively. The results will be saved to 'src/task3' named with '2009/2015final.tif'.

* task3_merge(year):    merges the files and save them as a new file. First it will get all the tiles from the same year and merge them by manipulating mosaics. By merging the files，the size and transformer information need to be updated in metadata, to keep them same as the original one. Then it will construct the path for output and save the file.

## Connect_route.py

Uses a different method to read tif files, containing converting tif to 8-bit image，which can be processed by OpenCV. OpenCV is a powerful library to do the morphological fixing, especially suitable for connect the gaps between flight lines which requires edge detection, morphological expansion and endpoints calculation and connection. But OpenCV can only process the image format like png and jpg, which means it will lose some information like transformer and projection. So, these data will be stored in profile, used for creating the fixed new tif files.

* read_and_preprocess_tiff(tiff_path):    reads tif files as a format of 8-bit.

* connect_nearest_contours(img):    passes the 8-bit image in and does the morphological expansion, then detects the boundries and calculate the endpoints. Connects the endpoints of flight lines.
  
* save_as_tiff(image, output_path, reference_tiff_path):    Saves new tif files and write into the profile data saved.
Note: In the line 49, the thickness of the line might influence the results of ice volume analysis by influencing the area of white pixels.

 ## volume_analysis.py

 Contains a class for analysis, initializing by passing in two DEMs for analysis.

 * read_tiff(self, tiff_path):    This another geotiff reading method with no 8bit-convert but with a tranform and profile storage.

 * resample_raster(dem1_in, dem2_ref_in, dem1_out):    Resamples the dem1_in into the same size and transform as the reference DEM, dem2_ref_in. And save as dem1_out. This is essential because the final result after filling the gaps of data from 2009 and 2015 are in different size, which is impossible to directly carry out the calculation.

 * compute_elevation_change(self):    Calculates the variation of elevation. And get rid of nodata areas.

 * compute_volume_change(self):    Calculates the volume and sea level variation.

 * save_elevation_difference_tiff(self,out_path):    It is a different geotiff-saving method from the connect_route's, will update the data type of raster data and make it be able to save as a goetiff.

 * report_results(self):    prints results, including volume variation and sea level variation.
