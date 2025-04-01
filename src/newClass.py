from pyproj import Proj, transform
from matplotlib import pyplot as plt
from processLVIS import lvisGround
from handleTiff import writeTiff





# A class inherited from lvisData, adding new methods to reproject,
#  preview waves and write them into .tif files
class plotLVIS(lvisGround):
  '''A class, ineriting from lvisData
     and add a plotting method'''


  def reprojectLVIS(self,outEPSG):
    '''A method to reproject the footprint coordinates'''
    # set projections
    inProj=Proj("epsg:4326")
    outProj=Proj("epsg:"+str(outEPSG))
    # reproject data
    self.x,self.y=transform(inProj, outProj, self.lat, self.lon)
    
  def reprojectBounds(self,outEPSG):
    '''A method to reproject the file bounds'''
    # set projections
    inProj=Proj("epsg:4326")
    outProj=Proj("epsg:"+str(outEPSG))
    # reproject data
    self.bounds[0,2],self.bounds[1,3]=transform(inProj, outProj, self.bounds[0,2], self.bounds[1,3])

  def inspectWaves(self):
    '''A method to preview the waves data in a single graph'''
    plt.plot(self.waves,self.z)
    plt.show()

  def plotWaves(self,outRoot="waveform",step=1):
    '''A method to plot all waveforms'''
    # this needs completing
    for i in range(0,self.nWaves,step):
      self.plotWave(i,outRoot=outRoot)
  
   
  def plotWave(self,i,outRoot="waveform"):
    ''''A method to plot a single waveform'''
    outName=outRoot+"."+str(i)+".png"
    plt.plot(self.waves[i],self.z[i])
    plt.xlabel("Waveform return")
    plt.ylabel("Elevation (m)")
    plt.savefig(outName)
    plt.close()
    print("Graph to",outName)

  def writeDEM(self,res,outName):
    '''Write LVIS ground elevation data to a geotiff'''

    # call function from tiffExample.py
    writeTiff(self.zG,self.x,self.y,res,filename=outName,epsg=3031)
    return