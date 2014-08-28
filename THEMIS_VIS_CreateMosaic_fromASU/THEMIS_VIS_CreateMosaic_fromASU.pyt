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
        self.description = "Download ISIS2 Cubes for TEHMIS VIS images from ASU"
 
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

        parameters = [in_features, edr_field, label_field, OutputPath]
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
            if urlExists > -1:
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

        #os.chdir(outputPath)
        #sysString = "running function ctx_project"
        #arcpy.AddMessage(sysString)
        #themisVis_project()
        #os.system(sysString)

