import arcpy
import urllib, os, glob, shutil, string

def find_char(shp, ch):
    index = 0 ; loc = 0
    for index in range(0,len(shp)): 
        if shp[index] == ch: 
            loc = index
    return loc + 1

class Toolbox(object):
    def __init__(self):
        self.label =  "THEMIS VIS Mosaic from ASU toolbox"
        self.alias  = "ThemisVis_CreateMosaic"

        # List of tool classes associated with this toolbox
        self.tools = [ThemisVis_CreateMosaic] 

class ThemisVis_CreateMosaic(object):
    def __init__(self):
        self.label       = "THEMIS VIS Mosaic from ASU toolbox"
        self.description = "Download ISIS2 Cubes for THEMIS VIS images from ASU and create and Mosiac Datatype (optional)"
 
    def getParameterInfo(self):
        #Define parameter definitions

        # Input Features parameter
        in_features = arcpy.Parameter(
            displayName="Input Features",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        in_features.filter.list = ["Polygon"]

        # EDR Field parameter
        edr_field = arcpy.Parameter(
            displayName="Product ID Field",
            name="ProductId",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        edr_field.value = "ProductId"
        
        # Target Field parameter
        label_field = arcpy.Parameter(
            displayName="Label URL Field",
            name="LabelURL",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        label_field.value = "LabelURL"

        # Ouput Path parameter
        OutputPath = arcpy.Parameter(
            displayName="Output Path",
            name="OutputPath",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")
        OutputPath.value = ""

        # Ouput Mosaic Name
        MosaicName = arcpy.Parameter(
            displayName="Mosaic Name",
            name="MosaicName",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        MosaicName.value = ""

        # Mosaic Footprint Shrink Distance
        ShrinkDistance = arcpy.Parameter(
            displayName="Footprint Shrink Distance (m)",
            name="ShrinkDistance",
            datatype="GPLong",
            parameterType="Optional",
            direction="Input")
        ShrinkDistance.value = 0


        parameters = [in_features, edr_field, label_field, OutputPath,MosaicName,ShrinkDistance]
        return parameters

    def isLicensed(self): #optional
        return True

    def updateParameters(self, parameters): #optional
        if parameters[0].altered:
            parameters[1].value = arcpy.ValidateFieldName(parameters[1].value, parameters[0].value)
            parameters[2].value = arcpy.ValidateFieldName(parameters[2].value, parameters[0].value)
        return

    def updateMessages(self, parameters): #optional
        return

    def execute(self, parameters, messages):
        inFeatures  = parameters[0].valueAsText
        edr_fieldName = parameters[1].valueAsText
        label_fieldName = parameters[2].valueAsText
        outputPath = parameters[3].valueAsText
        outputMosaicName = parameters[4].valueAsText
        ShrinkDist = parameters[5].valueAsText

        try:
            desc = arcpy.Describe(inFeatures)
            theInCount = len(desc.fidSet.split(";"))
        except:
            print('\nError: This tool must run from a layer loaded in ArcMap. Please run again but select layer from pulldown not using the folder button\n')
            messages.addErrorMessage('\nThis tool must run from a layer loaded in ArcMap. Please run again but select layer from pulldown not using the folder button\n')
            raise arcpy.ExecuteError

        if (desc.fidSet == ''):
            print('\nno features selected. Select a feature and rerun\n')
            messages.addErrorMessage('\nno features selected. Select a feature and rerun\n')
            raise arcpy.ExecuteError
        else:
            print('%s INPUT features selected' % str(theInCount))
            arcpy.AddMessage('%s INPUT features selected' % str(theInCount))

        theCount = int(arcpy.GetCount_management(inFeatures).getOutput(0))
        if (theCount > 500):
            print('\nOnly 500 features allowed to be selected. Please select less images and rerun\n')
            messages.addErrorMessage('\nOnly 500 features allowed to be selected. Please select less images and rerun\n')
            raise arcpy.ExecuteError

        cursor = arcpy.da.SearchCursor(inFeatures, [edr_fieldName, label_fieldName])

        aCnt = 0
        fileCnt = 0
        show_msg = "-"*60 ; arcpy.AddMessage(show_msg)

        for row in cursor:
            ProductId = row[0].strip().replace("RDR","LOC")
            LabelURL = row[1].strip()
            archiveName = LabelURL.split(r"/")[5].replace("r0","g0")
            volumeName = LabelURL.split(r"/")[6].replace("rdr","geo")
            #arcpy.AddMessage(volumeName)
            show_msg =  "\nFeature (" + str(aCnt + 1) + "/" + str(theInCount) + ")"
            arcpy.AddMessage(show_msg)
            
            UrlPath = "http://viewer.mars.asu.edu/mars/readonly/themis/pds/geometry/" + archiveName + "/" + volumeName + "/" + ProductId + ".CUB"
            #arcpy.AddMessage(UrlPath)
            
            outputImage = os.path.join(outputPath,ProductId + ".CUB")

            site = urllib.urlopen(UrlPath)
            meta = site.info()
            #arcpy.AddMessage(str(meta))
            urlExists = str(meta).find("Age: 0")
            if urlExists < 0:
                show_msg = "URL does not exist, cannot download: " + UrlPath
                arcpy.AddMessage(show_msg)
                aCnt = aCnt + 1
                continue

            #download ISIS2 Image
            if arcpy.Exists(outputImage):
                show_msg = "\nFile already exists, skipping: " + outputImage
                arcpy.AddMessage(show_msg)
            else:
                show_msg = "URL:  " + UrlPath
                arcpy.AddMessage(show_msg)
                show_msg = "Downloading file to:  " + outputImage + " please wait..."
                arcpy.AddMessage(show_msg)
                try:
                    h = urllib.urlretrieve(UrlPath, outputImage)
                except:
                     show_msg = "WebSite issues for ISIS2 Image, cannot download: " + outputImage + " URL: " + UrlPath
                     arcpy.AddMessage(show_msg)
            aCnt = aCnt + 1                

        ##############################
        ## Start Mosaic Creation
        ##############################
        if outputMosaicName != "":

            #Define Coordinate system
            Coordsystem = 'PROJCS["Mars2000 Equidistant Cylindrical clon0",GEOGCS["GCS_Mars_2000_Sphere",DATUM["D_Mars_2000_Sphere",SPHEROID["Mars_2000_Sphere_IAU_IAG",3396190.0,0.0]],PRIMEM["Reference_Meridian",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Equidistant_Cylindrical"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],PARAMETER["Standard_Parallel_1",0.0],UNIT["Meter",1.0]]'
            mosaicgdb = os.path.join(outputPath,outputMosaicName + ".gdb")

            # Process: Create File GDB
            arcpy.CreateFileGDB_management(outputPath, outputMosaicName + ".gdb")
            arcpy.AddMessage("Create File GDB")

            # Process: Create Mosaic Dataset
            arcpy.CreateMosaicDataset_management(mosaicgdb, outputMosaicName, Coordsystem, "1", "16_BIT_SIGNED", "NONE", "")
            arcpy.AddMessage("Created Mosaic Dataset")

            # Process: Add Rasters To Mosaic Dataset
            theMosaic = mosaicgdb +"\\"+ outputMosaicName
            arcpy.AddMessage("Adding Rasters To Mosaic Dataset")
            arcpy.AddRastersToMosaicDataset_management(theMosaic, "Raster Dataset", outputPath, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "0", "1500", "", "*.CUB", "NO_SUBFOLDERS", "EXCLUDE_DUPLICATES", "NO_PYRAMIDS", "CALCULATE_STATISTICS", "NO_THUMBNAILS", "", "NO_FORCE_SPATIAL_REFERENCE")

            # Process: Define Mosaic Dataset NoData
            arcpy.DefineMosaicDatasetNoData_management(theMosaic, "1", "BAND_1 -32768", "", "", "")

            # Process: Set Mosaic Dataset Properties
            arcpy.SetMosaicDatasetProperties_management(theMosaic, "", "", "None;LZ77;LERC", "LERC", "75", "0", "BILINEAR", "CLIP", "FOOTPRINTS_MAY_CONTAIN_NODATA", "CLIP", "NOT_APPLY", "", "NONE", "Center;NorthWest;LockRaster;ByAttribute;Nadir;Viewpoint;Seamline;None", "Seamline", "", "", "ASCENDING", "BLEND", "10", "600", "300", "1000", "0.8", "", "FULL", "", "DISABLED", "", "", "", "", "20", "1000", "GENERIC", "1")

            # Process: BuildFootprints_1
            arcpy.BuildFootprints_management(theMosaic, "", "RADIOMETRY", "", "", "100", "0", "NO_MAINTAIN_EDGES", "SKIP_DERIVED_IMAGES", "NO_BOUNDARY", "2000", "100", "NONE", "", "20", "0.05")

            # Process: BuildFootprints_2
            if not ShrinkDist.isdigit():
                ShrinkDist = "0"
            arcpy.AddMessage("Building Footprints")
            arcpy.BuildFootprints_management(theMosaic, "", "NONE", "", "", "100", ShrinkDist, "NO_MAINTAIN_EDGES", "SKIP_DERIVED_IMAGES", "UPDATE_BOUNDARY", "2000", "100", "NONE", "", "20", "0.05")

            # Process: Calculate statistics
            arcpy.AddMessage("Calculate statistics")
            arcpy.CalculateStatistics_management(theMosaic, "", "", "-32768", "OVERWRITE")

            # Process: Build Overviews
            arcpy.AddMessage("Build Overviews")
            arcpy.BuildOverviews_management(theMosaic, "", "DEFINE_MISSING_TILES", "NO_GENERATE_OVERVIEWS", "#", "#")
