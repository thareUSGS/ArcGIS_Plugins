import arcpy
import urllib, os, glob, shutil, string

def find_char(shp, ch):
    index = 0 ; loc = 0
    for index in range(0,len(shp)): 
        if shp[index] == ch: 
            loc = index
    return loc + 1

### Created by Matt Balme and Susan Conway at the Open University. Provided "as is" with no guarentees as to correct functioning!
### Please update and modify as you feel fit - if you make it better, please post!
### Just download CTX jp2 from ASU site and their accompanying .scyl.isis.hdr and put in same folder.
### Put this file into that folder and double-click (you need python installed)
### Created by Balme June 2013, updated by Conway to support polar projections
### Trent Hare, August 2014, Minor string read updates, argparse, nodata, and changed to polar radius for polar files
def ctx_project():
    # this makes a list of the basenames of all the CTX jp2s
    jp2list = glob.glob('*jp2') # makes a list of all jp2s
    jp2list=[w.replace ('.jp2','') for w in jp2list] #deletes the ".jp2" bit from the list

    #for each basename, this looks at the appropriate header file and extracts the numbers to make a worldfile

    for basenames in jp2list: # sets u pa loop to do this for each basename in the jp2list
       # checks for both a polar and simp cyl header file and skips this file if doesn't exist
       if os.path.exists( basenames+'.scyl.isis.hdr') or os.path.exists( basenames+'.ps.isis.hdr'):
          # defines the correct pathnames depending on projection
          if os.path.exists( basenames+'.scyl.isis.hdr'):
             fileName=basenames+'.scyl.isis.hdr'
          else: # assume polar
             fileName=basenames+'.ps.isis.hdr'

          # loop over header to find parameters
          # split will find values after parameter name and before <meters>
          for line in open(fileName,'r'):
            if 'UpperLeftCornerY' in line:
               uly = float(((line.split('=')[1]).split('<')[0]).strip())
            if 'UpperLeftCornerX' in line:
               ulx = float(((line.split('=')[1]).split('<')[0]).strip())
            if 'PixelResolution' in line:
               pixres = float(((line.split('=')[1]).split('<')[0]).strip())
            if 'ProjectionName' in line:
               proj = (line.split('=')[1]).strip()
            if 'CenterLongitude' in line:
               clong = float((line.split('=')[1]).strip())
            if 'CenterLatitude' in line:
               clat = float((line.split('=')[1]).strip())
            if 'EquatorialRadius' in line:
               semiMajor = float(((line.split('=')[1]).split('<')[0]).strip())
            if 'PolarRadius' in line:
               semiMinor = float(((line.split('=')[1]).split('<')[0]).strip())

          #if clat empty then fill with 0
          try:
             clat
          except:
             clat=0
             
          if proj == "SimpleCylindrical":
             #pname = "Equirectangular"
             pname = "Equidistant_Cylindrical" #more typical in Arcmap but really the same
          elif clat == -90.0:
             pname="Stereographic_South_Pole"
          elif clat == 90.0:
             pname="Stereographic_North_Pole"
          else:
             print "Projection not currently supported. Exiting"
             sys.exit(1)

          world=[pixres, 0, 0,-pixres, ulx, uly] # makes a list called "world" that inlcudes these numbers (zeros are for rotation)
          with open(basenames+'.wld', 'w') as h: #makes a new file called basename.wld
             for item in world:
                print>>h, item # writes  the worldfile list to file
                #print(world) #displays worldfile values on screen
          h.closed
          print "writing " +basenames+'.jp2.aux.xml' + " in " + pname + " projection"
          # checks the projection and then makes an xml file
          if proj == "SimpleCylindrical":
             seq=["<PAMDataset>\n",
             "<SRS>PROJCS[&quot;Mars_Equidistant_Cylindrical_Clon180&quot;,GEOGCS[&quot;GCS_Mars_2000_Sphere&quot;,DATUM[&quot;D_Mars_2000_Sphere&quot;,SPHEROID[&quot;Mars_2000_Sphere&quot;," + 
             repr(semiMajor) + ",0.0]],PRIMEM[&quot;Reference_Longitude&quot;,0.0],UNIT[&quot;Degree&quot;,0.0174532925199433]],PROJECTION[&quot;" + 
             pname + "&quot;],PARAMETER[&quot;False_Easting&quot;,0.0],PARAMETER[&quot;False_Northing&quot;,0.0],PARAMETER[&quot;Central_Meridian&quot;," + 
             repr(clong) + "],PARAMETER[&quot;Standard_Parallel_1&quot;," + 
             repr(clat) + "],UNIT[&quot;Meter&quot;,1.0]]</SRS>\n",
             "<PAMRasterBand band=\"1\">\n",
             "<NoDataValue>0.0</NoDataValue>\n",
             "<Metadata domain=\"IMAGE_STRUCTURE\">\n",
             "<MDI key=\"COMPRESSION\">JP2000</MDI>\n",
             "</Metadata>\n",
             "</PAMRasterBand>\n",
             "</PAMDataset>\n"]
             with open(basenames+'.jp2.aux.xml','w') as xmlFile:
                xmlFile.writelines(seq)
             xmlFile.closed
          else:
             #assume Polar, also assuming ocentric lats which means we should use the SemiMinor as a sphere to emulate typical ographic lats, Trent
             seq=["<PAMDataset>\n",
             "<SRS>PROJCS[&quot;Mars_" + pname + "&quot;,GEOGCS[&quot;GCS_Mars_2000_PolarSphere&quot;,DATUM[&quot;D_Mars_2000_PolarSphere&quot;,SPHEROID[&quot;Mars_2000_PolarSphere&quot;," +
             repr(semiMinor) + ",0.0]],PRIMEM[&quot;Reference_Longitude&quot;,0.0],UNIT[&quot;Degree&quot;,0.0174532925199433]],PROJECTION[&quot;" +
             pname + "&quot;],PARAMETER[&quot;False_Easting&quot;,0.0],PARAMETER[&quot;False_Northing&quot;,0.0],PARAMETER[&quot;Central_Meridian&quot;," +
             repr(clong) + "],PARAMETER[&quot;Standard_Parallel_1&quot;," +
             repr(clat) + "],UNIT[&quot;Meter&quot;,1.0]]</SRS>\n",
             "<PAMRasterBand band=\"1\">\n",
             "<NoDataValue>0.0</NoDataValue>\n",
             "<Metadata domain=\"IMAGE_STRUCTURE\">\n",
             "<MDI key=\"COMPRESSION\">JP2000</MDI>\n",
             "</Metadata>\n",
             "</PAMRasterBand>\n",
             "</PAMDataset>\n"]
             with open(basenames+'.jp2.aux.xml','w') as xmlFile:
                xmlFile.writelines(seq)
       else:
          print "there is no accompanying ISIS header file for: " + basenames + ".jp2"

    return

class Toolbox(object):
    def __init__(self):
        self.label =  "CTX Create Mosaic from ASU toolbox"
        self.alias  = "CTX_CreateMosaic"

        # List of tool classes associated with this toolbox
        self.tools = [CTX_CreateMosaic] 

class CTX_CreateMosaic(object):
    def __init__(self):
        self.label       = "CTX Create Mosaic from ASU toolbox"
        self.description = "Create a CTX Mosaic from ASU Jpeg2000 and ISIS headers "
 
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

##        # Ouput Completed Flag
##        CompleteFlag = arcpy.Parameter(
##            displayName="CompletedFlag",
##            name="CompletedFlag",
##            datatype="GPString",
##            parameterType="Derived",
##            direction="Output")

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
        ShrinkDistance.value = 500
        
        parameters = [in_features, edr_field, label_field, OutputPath, MosaicName, ShrinkDistance]
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
            ProductId = row[0].strip()
            LabelURL = row[1].strip()
            volumeName = LabelURL.split(r"/")[7]
            #arcpy.AddMessage(volumeName)
            show_msg =  "\nFeature (" + str(aCnt + 1) + "/" + str(theInCount) + ")"
            arcpy.AddMessage(show_msg)
            
            UrlPath = "http://image.mars.asu.edu/stream/" + ProductId + ".jp2?image=/mars/images/ctx/" + volumeName + "/prj_full/" + ProductId + ".jp2"
            #show_msg =  UrlPath
            #arcpy.AddMessage(show_msg)
            
            HdrUrl = "http://image.mars.asu.edu/stream/" + ProductId + ".scyl.isis.hdr?image=/mars/images/ctx/" + volumeName + "/stage/" + ProductId + ".scyl.isis.hdr"
            #arcpy.AddMessage(HdrUrl)

            # Extraction of image name from full path
            ch = "/" # separator character - separate image and html path
            #UrlPath = dataLink[:rozd-1] # html path
            rozd = find_char(UrlPath,ch)
            outputImage = UrlPath[rozd:] # name of ISIS image without html path
            rozd = find_char(HdrUrl,ch)
            outputHeader = HdrUrl[rozd:] # name of ISIS label without html path

            outputImage = os.path.join(outputPath,outputImage)
            outputHdr = os.path.join(outputPath,outputHeader)

            site = urllib.urlopen(HdrUrl)
            meta = site.info()
            #arcpy.AddMessage(str(meta))
            urlExists = str(meta).find("Age: 0")
            if urlExists < 0:
                show_msg = "URL does not exist, cannot download: " + HdrUrl
                arcpy.AddMessage(show_msg)
                aCnt = aCnt + 1
                continue

            #download ISIS Header
            try:
                show_msg = "Header URL:  " + HdrUrl
                arcpy.AddMessage(show_msg)
                show_msg = "Downloading Header to:  " + outputHeader + " please wait..."
                arcpy.AddMessage(show_msg)
                h = urllib.urlretrieve(HdrUrl, outputHdr)
            except:
                show_msg = "ISIS Header URL does not exist, cannot download: " + outputHeader + " URL: " + HdrUrl
                arcpy.AddMessage(show_msg)

            #download Jp2 Image
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
                     show_msg = "WebSite issues for Jp2, cannot download: " + outputImage + " URL: " + UrlPath
                     arcpy.AddMessage(show_msg)
            aCnt = aCnt + 1
                

        os.chdir(outputPath)
        sysString = "running function ctx_project"
        arcpy.AddMessage(sysString)
        ##Define auxillary files for CTX jpeg2000s
        ctx_project()
        #os.system(sysString)
        #arcpy.SetParameterAsText(4, "true")

        ##############################
        ## Start Mosaic Creation
        ##############################
        if outputMosaicName:

            #Define Coordinate system
            Coordsystem = 'PROJCS["Mars2000 Equidistant Cylindrical clon180",GEOGCS["GCS_Mars_2000_Sphere",DATUM["D_Mars_2000_Sphere",SPHEROID["Mars_2000_Sphere_IAU_IAG",3396190.0,0.0]],PRIMEM["Reference_Meridian",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Equidistant_Cylindrical"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",180.0],PARAMETER["Standard_Parallel_1",0.0],UNIT["Meter",1.0]]'
            mosaicgdb = os.path.join(outputPath,outputMosaicName + ".gdb")

            # Process: Create File GDB
            arcpy.CreateFileGDB_management(outputPath, outputMosaicName + ".gdb")
            arcpy.AddMessage("Create File GDB")

            # Process: Create Mosaic Dataset
            arcpy.CreateMosaicDataset_management(mosaicgdb, outputMosaicName, Coordsystem, "1", "8_BIT_UNSIGNED", "NONE", "")
            arcpy.AddMessage("Created Mosaic Dataset")

            # Process: Add Rasters To Mosaic Dataset
            theMosaic = mosaicgdb +"\\"+ outputMosaicName
            arcpy.AddMessage("Adding Rasters To Mosaic Dataset")
            arcpy.AddRastersToMosaicDataset_management(theMosaic, "Raster Dataset", outputPath, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "0", "1500", "", "*.jp2", "NO_SUBFOLDERS", "EXCLUDE_DUPLICATES", "NO_PYRAMIDS", "CALCULATE_STATISTICS", "NO_THUMBNAILS", "", "NO_FORCE_SPATIAL_REFERENCE")

            # Process: Define Mosaic Dataset NoData
            arcpy.DefineMosaicDatasetNoData_management(theMosaic, "1", "BAND_1 0", "", "", "NO_COMPOSITE_NODATA")

            # Process: Set Mosaic Dataset Properties
            arcpy.SetMosaicDatasetProperties_management(theMosaic, "4100", "15000", "None;LZ77;JPEG;LERC", "None", "75", "0", "BILINEAR", "CLIP", "FOOTPRINTS_MAY_CONTAIN_NODATA", "CLIP", "NOT_APPLY", "", "NONE", "Center;NorthWest;LockRaster;ByAttribute;Nadir;Viewpoint;Seamline;None", "Seamline", "", "", "ASCENDING", "BLEND", "10", "600", "300", "1000", "0.8", "", "FULL", "", "DISABLED", "", "", "", "", "20", "1000", "GENERIC", "1")

            # Process: BuildFootprints_1
            arcpy.BuildFootprints_management(theMosaic, "", "RADIOMETRY", "1", "255", "10", "0", "NO_MAINTAIN_EDGES", "SKIP_DERIVED_IMAGES", "NO_BOUNDARY", "2000", "100", "NONE", "", "20", "0.05")

            # Process: BuildFootprints_2
            if not ShrinkDist.isdigit():
                ShrinkDist = "0"
            arcpy.AddMessage("Building Footprints")
            arcpy.BuildFootprints_management(theMosaic, "", "NONE", "1", "254", "10", ShrinkDist, "NO_MAINTAIN_EDGES", "SKIP_DERIVED_IMAGES", "UPDATE_BOUNDARY", "2000", "100", "NONE", "", "20", "0.05")

            # Process: Calculate statistics
            arcpy.AddMessage("Calculate statistics")
            arcpy.CalculateStatistics_management(theMosaic, "", "", "0", "OVERWRITE")

            # Process: Build Overviews
            #arcpy.AddMessage("Build Overviews")
            #arcpy.BuildOverviews_management(theMosaic, "", "DEFINE_MISSING_TILES", "NO_GENERATE_OVERVIEWS", "#", "#")

            arcpy.AddMessage("Mosaic created. Process complete.")
        else:
            arcpy.AddMessage("No Mosaic Name specified, skipping mosaic creation. Process complete.")
        
