#
# ----------------------------------------------------------------------------------
# Functions
      
# usage: "file.nc", "tasmax", "sumsT", 366, 53
def ProcessNetCDFFile(ncFile, var, sumsparam, times, projs): # Creates raster files from NetCDF files and calculates sums, sumsqs, mean, and variance

    # Print some statistics about parameters passed to the function
    print "\n" + "---------------------------------"
    print "Processing NetCDF files..."
    print "File name is " + ncFile

    sums = ""
    mean = ""

    if sumsparam == "sumsT":
        sums = arcpy.env.workspace + os.sep + sumsparam + ".img"

    if sumsparam == "sumsqsT":
        sums = arcpy.env.workspace + os.sep + sumsparam + ".img"
        mean = arcpy.env.workspace + os.sep  + "Mean.img"
 
    firstRun = True  # when true the sumsT raster will be a copy of the first slice
    
    for t in range(0, times):

        for p in projs:

            try:
                    
                layerName = var + "_T" + str(t) + "P" + str(p)
                print "layer name : " + layerName
                
                # Process: Make NetCDF Raster Layer...
                arcpy.MakeNetCDFRasterLayer_md(ncFile, var, "lon", "lat", layerName, "", "projection " + str(p) + "; time " + str(t), "BY_INDEX")

                tempRaster = arcpy.env.workspace + os.sep + "temp_T" + str(t) + "_P" + str(p) + "_CopyRaster.img" 
                print "I am going to make " + tempRaster
                    
                
                if sumsparam == "sumsT":
                    
                    # Calculating sums...            
                    print "Calculating sums..."
                    if ((t == 0) and (firstRun == True)):
                        rast = Raster(layerName)
                        if (arcpy.Exists(sums)):
                            arcpy.Delete_management(sums)
                    else:
                        arcpy.CopyRaster_management(sums, tempRaster)
                        rast = Raster(layerName) + Raster(tempRaster)
                    
                    rast.save(sums)
                
                    
                if sumsparam == "sumsqsT":

                    print "Calculating squared sums..."
                    if ((t == 0) and (firstRun == True)):
                        rast2 = (Raster(layerName) - Raster(mean)) * (Raster(layerName) - Raster(mean))
                        if (arcpy.Exists(sums)):
                            arcpy.Delete_management(sums)
                    else:
                        arcpy.CopyRaster_management(sums, tempRaster)
                        rast2 = (Raster(layerName) - Raster(mean)) * (Raster(layerName) - Raster(mean)) + Raster(tempRaster)
                        
                    rast2.save(sums)

            except Exception, e:

                print e
                continue

            finally:
                
                firstRun = False

                # Do cleanup
                DeleteSingleFile(layerName)
                DeleteSingleFile(tempRaster)
                

def CalculateMean(Times, Projs):
                    
     print "---------------------------------------------------"
     print "I am going to begin calculating the mean..."
                    
     sumsT = arcpy.env.workspace + os.sep + "sumsT.img"
     mean = arcpy.env.workspace + os.sep + "Mean.img"

     temp = Raster(sumsT) / (Times * len(Projs))
     temp.save(mean)

     print "The raster has been saved as " + mean

def CalculateVariance(Times, Projs):

     print "---------------------------------------------------"
     print "I am going to begin calculating the variance..."
                    
     sumsqsT = arcpy.env.workspace + os.sep + "sumsqsT.img"
     var = arcpy.env.workspace + os.sep + "Var.img"

     temp = Raster(sumsqsT) / (Times * len(Projs))
     temp.save(var)

     print "The raster has been saved as " + var

def CalculateStandardDeviation():

     print "---------------------------------------------------"
     print "I am going to begin calculating the standard deviation..."
                    
     var = arcpy.env.workspace + os.sep + "Var.img"
     std = arcpy.env.workspace + os.sep + "Std.img"

     temp = SquareRoot(Raster(var))
     temp.save(std)

     print "The raster has been saved as " + std

def CalculateSums(ncFile, Var, Params, SumsParams, Times, Projs):

    print "---------------------------------------------------"
    print "I am going to begin calculating means and variances.."

    sumsT = arcpy.env.workspace + os.sep + SumsParams[0] + ".img"
    sumsqsT = arcpy.env.workspace + os.sep + SumsParams[1] + ".img"
    
    for j in range(0, len(Params)): # Params loop
            
        try:
            # Find stats raster
            #raster = Vars[i]+Params[j]+"Name"+str(k)+".img"
            raster = arcpy.env.workspace + os.sep + Params[j] + ".img"
                                      
            print "Processing raster " + raster + "..."
            
            # Build expression
            #dirPath = arcpy.env.workspace
            temp = None # temp raster to hold the computed results
            
            if Params[j] == "Mean":
                print "Calculating mean for " + raster
                #inExpress = dirPath + os.sep + "sumsT.img / " + str(Times * len(Projs))
                #print inExpress
                temp = Raster(sumsT) / (Times * len(Projs))
                
            if Params[j] == "Var":
                print "Calculating variance for " + raster
                #inExpress = "(" + dirPath + os.sep + "sumsqsT.img - (" + dirPath + os.sep + "sumsT.img * " + dirPath + os.sep + "sumsT.img)) / " + str(Times * len(Projs))
                #print inExpress
                temp = (Raster(sumsqsT) - (Raster(sumsT) * Raster(sumsT))) / (Times * len(Projs))
                
            if Params[j] == "Std":
                print "Calculating standard deviation for " + raster
                #inExpress = math.sqrt("(" + dirPath + os.sep + "sumsqsT.img - (" + dirPath + os.sep + "sumsT.img * " + dirPath + os.sep + "sumsT.img)) / " + str(Times * len(Projs)))
                #print inExpress
                temp = SquareRoot(Raster(sumsqsT) - (Raster(sumsT) * Raster(sumsT)) / (Times * len(Projs)))
                    
            # Calculate raster
            #arcpy.SingleOutputMapAlgebra_sa(inExpress, "Temp")
            #arcpy.CopyRaster_management("Temp", raster)
            temp.save(raster)

            print "The raster has been saved as " + raster
            
            #DeleteSingleFile("Temp")
            #DeleteMultipleFiles("g_g*.*")
        except:
            print arcpy.GetMessages(2)


def MakeScenarioDirectories(dirs):

    print "\n" + "-----------------------------------------------------------------------"
    for i in range(0, len(dirs)):
        
        d = arcpy.env.workspace + os.sep + dirs[i]
        print "Checking scenario directory " + d
        
        if not os.path.exists(d): 
            os.makedirs(d)



def CopyNetCDFFilesToSubdirs(ncdfFiles, dirs):

    print "\n" + "-----------------------------------------------------------------"
    print "Copying NetCDF files to subdirectories"

    for i in range(0, len(ncdfFiles)):
        
        f = ncdfFiles[i]
    
        for s in range(0, len(dirs)):
            shutil.copy2(f, arcpy.env.workspace + os.sep + dirs[s])
            

def DeleteSingleFile(f): # Deletes single file
    try:        
        if arcpy.Exists(f):
            arcpy.Delete_management(f)
    except:
        print "Error deleting file " + f

def DeleteMultipleFiles(mask): # Delets multiple files by mask sach as 'g_g_g*.*'

    print "Cleaning directory " + arcpy.env.workspace
    
    filesToDelete = []
    fileToDelete = arcpy.ListFiles(mask) #filesToDelete = [file for file in os.listdir(gp.workspace) if fnmatch(file, mask)]


    if filesToDelete is not None:
        for d in range(0, len(filesToDelete)):
            if arcpy.Exists(filesToDelete[d]):
                arcpy.Delete_management(filesToDelete[d]) # removes g_g_g*.*.aux file
                arcpy.Delete_management(filesToDelete[d].split('.')[0]) # removes g_g_g* directory

# ------------------------------------------------------------------------------------------
# Main Function

# import modules
import arcpy, os, shutil
from fnmatch import fnmatch
from arcpy.sa import *
import math


# set properties of GP object
rootDir = r"C:\OTS\CLIMATE\TMAX20002"
tempDir = r"C:\Temp\Temp_Output"
arcpy.env.workspace = rootDir # change for each year. Also, redefined later for subdirectory paths
arcpy.env.scratchworkspace = tempDir
arcpy.env.overwriteOutput = True

print arcpy.CheckExtension("spatial")
if arcpy.CheckExtension("spatial") == "Available":
    arcpy.CheckOutExtension("spatial")
else:
    raise "LicenseError"

# Add required toolboxes if gp object is created using win32com extension
#gp.AddToolbox("C:\Program Files (x86)\ArcGIS\ArcToolBox\Toolboxes\Multidimension Tools.tbx")
#gp.AddToolbox("C:\Program Files (x86)\ArcGIS\ArcToolBox\Toolboxes\Data Management Tools.tbx")

try:

    # make a list of ncdf files from the specified directory
    # http://mail.python.org/pipermail/python-list/2007-September/098842.html
    ncdfFiles = []
    ncdfFiles = arcpy.ListFiles("*.nc")

    # Create a NetCDF object to get access to properties of the NetCDF class
    Prop = arcpy.CreateObject("NetCDFFileProperties", ncdfFiles[0])

    # get time and projection numbers
    Times = Prop.getDimensionSize("time")
    Projs = Prop.getDimensionSize("projection")


    # Create lists
    Vars = ["tasmax"] # different for tmax and tmin files
    Params = ["Mean", "Var", "Std"]
    SumsParams = ["sumsT", "sumsqsT"] # stats rasters
    ScenDirs = ["A1B", "A2", "B1"] # directory names for each scenario
    AllProjsInd = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52]
    A1BProjsInd = [0,1,2,9,12,15,18,21,22,27,28,29,38,39,40,41,42]
    A2ProjsInd = [3,4,5,10,13,16,19,23,24,30,31,32,36,43,44,45,46,47]
    B1ProjsInd = [6,7,8,11,14,17,20,25,26,33,34,35,37,48,49,50,51,52]

    # Overwrite for debug only. Comment out this little block when running for real
    #Times = 4
    #Projs = 4
    #AllProjsInd = [0,1,2,3]
    #A1BProjsInd = [0,1,2]
    #A2ProjsInd = [3]
    #B1ProjsInd = []

    # 1) First, process files in the main directory
    #for i in range(0, len(ncdfFiles)):
        
    fileName = ncdfFiles[0]
    ncdfFiles[0] = arcpy.env.workspace + os.sep + fileName
    print "\n" + "----------------------------------------------"
    print "Processing file ", ncdfFiles[0]

    # make sums rasters
    ProcessNetCDFFile(ncdfFiles[0], Vars[0], SumsParams[0], Times, AllProjsInd) # go calculate sums, sumssqs, means, and variances

    # Calculate mean
    CalculateMean(Times, AllProjsInd)

    # make squared sums rasters
    ProcessNetCDFFile(ncdfFiles[0], Vars[0], SumsParams[1], Times, AllProjsInd)

    # calculate variance
    CalculateVariance(Times, AllProjsInd)

    # calculate standard deviation
    CalculateStandardDeviation()
            
    # Calculate mean and variance final rasters
    #CalculateSums(ncdfFiles[0], Vars[0], Params, SumsParams, Times, AllProjsInd)

    # 2) Do clean up
    #DeleteMultipleFiles("g_g*.*")
    
    # 3) Make scenario directories 
    MakeScenarioDirectories(ScenDirs)

    # Move NET CDF files to subdirectories
    #CopyNetCDFFilesToSubdirs(ncdfFiles, ScenDirs)
                     
    # 4) Process files in each scenario directory
    for d in range(0, len(ScenDirs)):

        print "\n" + "--------------------------------------------"
        print "I am goint to process files in subdir " + ScenDirs[d]
        
        # redefine workspace
        arcpy.env.workspace = rootDir + os.sep + ScenDirs[d]
                         
##        ncdfFilesSuDir = []
##        ncdfFilesSuDir = arcpy.ListFiles("*.nc") #[file for file in os.listdir(gp.workspace) if fnmatch(file, '*.nc')]
##                         
##        fileName = ncdfFilesSuDir[0]
##        ncdfFilesSuDir[0] = arcpy.env.workspace + os.sep + fileName
                     
        print "Processing file ", ncdfFiles[0]

        # process netCDf files
        projList = [] # list of projections is different for each scenario
        
        if d == 0:
            projList = A1BProjsInd
        elif d == 1:
            projList = A2ProjsInd
        elif d == 2:
            projList = B1ProjsInd

        # make sums rasters
        ProcessNetCDFFile(ncdfFiles[0], Vars[0], SumsParams[0], Times, projList)

        # Calculate mean
        CalculateMean(Times, projList)

        # make squared sums rasters
        ProcessNetCDFFile(ncdfFiles[0], Vars[0], SumsParams[1], Times, projList)
                
        # calculate variance
        CalculateVariance(Times, projList)

        # calculate standard deviation
        CalculateStandardDeviation()

        # Do clean up
        #DeleteMultipleFiles("g_g*.*")
        

    print "Success."
    arcpy.CheckInExtension("spatial")
    
except:
    print arcpy.GetMessages()
    print "I do not think it worked"
    arcpy.GetMessages()
    arcpy.CheckInExtension("spatial")
