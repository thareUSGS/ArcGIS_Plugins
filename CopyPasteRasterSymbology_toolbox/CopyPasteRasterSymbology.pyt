import arcpy
from arcpy import env

class Toolbox(object):
    def __init__(self):
        """Copy and Paste Raster Symbology toolbox"""
        self.label = "Copy Symbology Toolbox"
        self.alias = "Copy Symbology"

        # List of tool classes associated with this toolbox
        self.tools = [CopyPasteFeatureSymbology, CopyPasteRasterSymbology]

class CopyPasteRasterSymbology(object):
    def __init__(self):
        """Copy and Paste Raster Symbology"""
        self.label = "Raster: Copy and Paste Symbology"
        self.description = "Copy the symbology from a single image to one or more other images"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Input Features parameter
        in_layer = arcpy.Parameter(
            displayName="Input Image Layer to Copy SYmbology From",
            name="in_layer",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")
            
        # Derived Output Features parameter
        out_layers = arcpy.Parameter(
            displayName="Output Image Layers (drag and drop many here)",
            name="out_layers",
            datatype="GPRasterLayer",
            parameterType="Required",
            multiValue="True",
            direction="Input")

        # Allow rename to correct for spaces - need to figure out how to rename first
        #spaces = arcpy.Parameter(
        #    displayName="Allow program to rename files to replaced spaces with underscores",
        #    name="spaces",
        #    datatype="Boolean",
        #    parameterType="Optional",
        #    multiValue="False",
        #    direction="Input")

        parameters = [in_layer, out_layers]
        #parameters = [in_layer, out_layers, spaces]
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        env.addOutputToMap = True
        env.workspace = 'in_memory'
        env.overwriteOutput = 1
        mxd = arcpy.mapping.MapDocument("CURRENT")
        dataFrame = mxd.activeDataFrame
        
        inImage  = parameters[0].valueAsText
        outImages  = parameters[1].valueAsText.split(";")
        #spaces = parameters[2].valueAsText
        #arcpy.AddMessage(spaces)
        
        for outImage in outImages:
            #if (spaces == 'true'):
            #    if (" " in outImage):
            #        outImageUnderscores = outImage.replace(" ","_")
            #        #outImage.name = str(outImageUnderscores)
            #        outImage = outImageUnderscores
            if (" " in outImage):
               arcpy.AddWarning('*** Warning: Cannot apply to files with spaces in the name. Skipping: %s' % outImage)
               arcpy.AddWarning('*** Recommendation: rename group name or layer name with underscores.')
            else:
               arcpy.ApplySymbologyFromLayer_management(outImage, inImage)
               arcpy.AddMessage('--- New symbology applied to: %s' % outImage)
               
            '''Uncomment next section if you want to create *.lyr files. Path is hardwire'''
            ##comment: next line removes last extension file.tif = file or file.out.tif = file.out
            #outImageNoExt = '.'.join(outImage.split('.')[:-1]) if '.' in outImage else outImage
            #outFileImageLayer = str(outImageNoExt) + "_newSymbol.lyr"
            #arcpy.SaveToLayerFile_management(outImage, r'c:\temp\%s' % outFileImageLayer)
            #Adding layer not working - Arc removes them?
            #addLayer = arcpy.mapping.Layer(r'c:\temp\%s' % outFileImageLayer)  
            #addLayer.name = outFileImageLayer   
            #arcpy.mapping.AddLayer(dataFrame, addLayer, "TOP")

        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()
        return

class CopyPasteFeatureSymbology(object):
    def __init__(self):
        """Copy and Paste Feature Symbology"""
        self.label = "Feature: Copy and Paste Symbology"
        self.description = "Copy the symbology from a single feature layer to one or more other like layers. The datatype must be the same."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Input Features parameter
        in_layer = arcpy.Parameter(
            displayName="Input Feature Layer to Copy Symbology From",
            name="in_layer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
            
        # Derived Output Features parameter
        out_layers = arcpy.Parameter(
            displayName="Output Feature Layers (drag and drop many here)",
            name="out_layers",
            datatype="GPFeatureLayer",
            parameterType="Required",
            multiValue="True",
            direction="Input")

        print out_layers
        arcpy.AddMessage(out_layers)

        parameters = [in_layer, out_layers]
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        env.addOutputToMap = True
        env.workspace = 'in_memory'
        env.overwriteOutput = 1
        mxd = arcpy.mapping.MapDocument("CURRENT")
        dataFrame = mxd.activeDataFrame
        
        inFeature  = parameters[0].valueAsText
        inDesc = arcpy.Describe(inFeature)
        inType = str(inDesc.shapeType)
        outFeatures  = parameters[1].valueAsText.split(";")

        for outFeature in outFeatures:
            outDesc = arcpy.Describe(outFeature)
            outType = str(outDesc.shapeType)
            
            if (inType <> outType):
                arcpy.AddWarning("*** Warning: %s is not type of %s. Skipping layer." % (outFeature, inType))
            else:
                if (" " in outFeature):
                   arcpy.AddWarning('*** Warning: Cannot apply to layers with spaces in the name. Skipping: %s' % outFeature)
                   arcpy.AddWarning('*** Recommendation: rename group name or layer name with underscores.')
                else:
                   arcpy.ApplySymbologyFromLayer_management(outFeature, inFeature)
                   arcpy.AddMessage('--- New symbology applied to: %s' % outFeature)
                   
                '''Uncomment next section if you want to create *.lyr files. Path is hardwire'''
                ##comment: next line removes last extension file.tif = file or file.out.tif = file.out
                #outFeatureNoExt = '.'.join(outFeature.split('.')[:-1]) if '.' in outFeature else outFeature
                #outFileFeatureLayer = str(outFeatureNoExt) + "_newSymbol.lyr"
                #arcpy.SaveToLayerFile_management(outFeature, r'c:\temp\%s' % outFileFeatureLayer)
                #Adding layer not working - Arc removes them?
                #addLayer = arcpy.mapping.Layer(r'c:\temp\%s' % outFileFeatureLayer)  
                #addLayer.name = outFileFeatureLayer   
                #arcpy.mapping.AddLayer(dataFrame, addLayer, "TOP")

        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()
        return

