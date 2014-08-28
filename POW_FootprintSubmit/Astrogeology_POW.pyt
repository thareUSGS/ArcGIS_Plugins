# -*- coding: cp1252 -*-
import arcpy
import webbrowser

class Toolbox(object):
    def __init__(self):
        self.label =  "Astrogeology POW toolbox"
        self.alias  = "POW"

        # List of tool classes associated with this toolbox
        self.tools = [SubmitToPOW] 

class SubmitToPOW(object):
    def __init__(self):
        self.label       = "Astrogeology POW Tools"
        self.description = "Submit job to Astrogeology Map Projection " + \
                           "on the Web (POW) image processing service."
 
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
            displayName="EDR Source Location Field",
            name="edr_source",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        edr_field.value = "edr_source"
        
        # Target Field parameter
        target_field = arcpy.Parameter(
            displayName="Planetary Target",
            name="targetname",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        target_field.value = "targetname"

        parameters = [in_features, edr_field, target_field]
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
        target_fieldName = parameters[2].valueAsText

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
        if (theCount > 50):
            print('\nOnly 50 features allowed to be selected. Please select less images and rerun\n')
            messages.addErrorMessage('\nOnly 50 features allowed to be selected. Please select less images and rerun\n')
            raise arcpy.ExecuteError

        cursor = arcpy.da.SearchCursor(inFeatures, [edr_fieldName, target_fieldName])
        theURLlist = []
        for row in cursor:
            theURLlist.append(row[0])
        #theURLs = '\n'.join(theURLlist)
        theURLs = ','.join(theURLlist)
        theTarget = row[1]
        #print(theURLs)
        arcpy.AddMessage(theURLs)

        htmlTop = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8" />
  <meta name="robots" content="index, follow" />
  <meta name="keywords" content="projection, cloud, map-a-planet, coordinates, planet, mapping, usgs, nasa, cartography, astrogeology, mars, moon, jupiter, saturn, voyager, cassini" />
  <meta name="description" content="USGS Astrogeology Cloud Imagery Processing" />
  <title>Imagery Processing Cloud - USGS Astrogeology Science Center - Submit page for Map Projection On the Web</title>
  <link href="favicon.ico" rel="shortcut icon" type="image/x-icon" />
  <!-- should use a dynamic stylesheet based on what service/referer -->
  <link rel="stylesheet" href="http://astrocloud.wr.usgs.gov/css/jobs.css" type="text/css" />
<!--[if IE]>
  <link rel="stylesheet" href="http://astrocloud.wr.usgs.gov/css/ie.css" type="text/css" />  
<![endif]-->
</head>

<body>
  <div id="header">
    <a href="http://www.usgs.gov">
      <img class="logo" height="70" width="180" src="http://astrocloud.wr.usgs.gov/images/usgs_logo_main_2x.png" alt="USGS: Science for a Changing World"/>
    </a>
    <h1 id="title">Map Projection On the Web</h1>
        </div>
  <div id="wrapper">
    <div id="nav">
      <div id="username"></div>
      <ul class="links">
        <li><a href="http://astrocloud.wr.usgs.gov/index.php?view=login" target="_blank">Login</a></li>
        <li><a href="http://astrocloud.wr.usgs.gov/index.php?view=reset" target="_blank">Reset Your Password</a></li>
        <li><a href="http://astrocloud.wr.usgs.gov/index.php?view=edituser&act=request" target="_blank">Request User Account</a></li>
        <li><a href="http://pilot.wr.usgs.gov" target="_blank">Search Pilot</a></li>
      </ul>
    </div>
<!--
       <div style="background-image:url(http://astrocloud.wr.usgs.gov/images/pow-workflow.png)" class="banner"></div>
       <div class="tabs">
         <a href=""http://astrocloud.wr.usgs.gov/index.php?view=pow" class="active">Map Projection on the Web</a>
       </div>
-->
    <div id="content">
<div class="main-content">
'''

        htmlBottom = '''
  <!--
  <h2>Integrated Tools</h2>
  <ul class="def-list">
    <li><span class="label"><a href="http://isis.astrogeology.usgs.gov/UserDocs">ISIS3</a></span> - ISIS (version 3) is an image processing software package. The focus of the software is to manipulate imagery collected by current and past NASA planetary missions sent to Mars, Jupiter, Saturn, and other solar system bodies.
    <li><span class="label"><a href="http://pilot.wr.usgs.gov">PILOT and UPC</a></span> – The Planetary Image LOcator Tool is a web based search tool for the Unified Planetary Coordinate (UPC) database of the Planetary Data System. PILOT features SPICE-corrected image locations and searching capabilities using a navigable map, user selectable image constraints (e.g., incidence angle, solar longitude, pixel resolution and phase angle), and facilitates bulk downloads and/or image processing using POW.
    <li><span class="label"><a href="http://www.gdal.org">GDAL</a></span> – Geospatial Data Abstraction Library is used for conversion from ISIS (version 3) format to GeoTiff, GeoJpeg2000, Jpeg, and PNG. Conversion to PDS format is handled by ISIS.
  </ul>
  <h2>References</h2>
  <ul class="def-list">
    <li><span class="label" style="color:black;">POW</span>
    <ul class="def-list">
      <li>Hare, T.M., et at., (2013), LPSC XLIV, abstract <a href="http://www.lpi.usra.edu/meetings/lpsc2013/pdf/2068.pdf">2068</a></li>
    </ul>
    <li><span class="label" style="color:black;">ISIS</span>
    <ul class="def-list">
      <li>Keszthelyi, L., et al., 2013, LPSC XLIV, abstract <a href="http://www.lpi.usra.edu/meetings/lpsc2013/pdf/2546.pdf">2546</a></li>
      <li>Sides S. et al., 2013, LPSC XLIV, abstract <a href="http://www.lpi.usra.edu/meetings/lpsc2013/pdf/1746.pdf">1746</a></li>
    </ul>
    <li><span class="label" style="color:black;">GDAL</span>
    <ul class="def-list">
      <li>Geospatial Data Abstraction Library <a href="http://www.gdal.org">GDAL</a></li>
    </ul>
    <li><span class="label" style="color:black;">PILOT</span>
    <ul class="def-list">
      <li>Bailen, M.S., et al, (2013), LPSC XLIV, abstract <a href="http://www.lpi.usra.edu/meetings/lpsc2013/pdf/2246.pdf">2246</a></li>
    </ul>
    <li><span class="label" style="color:black;">PDS</span>
    <ul class="def-list">
      <li>Planetary Data System Standards Reference, <a href="http://pds.nasa.gov/tools/standards-reference.shtml">v. 3.8, JPL D-7669, Part 2.</a></li>
    </ul>
    <li><span class="label" style="color:black;">UPC</span>
    <ul class="def-list">
      <li>Akins, S. W., et al, (2009), LPSC XL, abstract <a href="http://www.lpi.usra.edu/meetings/lpsc2009/pdf/2002.pdf">2002</a></li>
    </ul>
  </ul>
  -->
</div>
</div>
<div id="footer">
        <div class="site-links">
          <a href="http://astrocloud.wr.usgs.gov/">home</a>&nbsp;&nbsp;|&nbsp;&nbsp;
          <a href="mailto:astroweb@usgs.gov" >contact</a>&nbsp;&nbsp;|&nbsp;&nbsp;
          <a href="http://isis.astrogeology.usgs.gov/IsisSupport/viewforum.php?f=52" target="_blank">support</a>&nbsp;&nbsp;|&nbsp;&nbsp;
          <a href="http://astrodocs.wr.usgs.gov/index.php/PILOT:Main" target="_blank">help</a>
        </div>
        <div class="gov-links">
          <a href="http://www.doi.gov" target=_top>U.S. Department of the Interior</a> &nbsp;|&nbsp;
          <a href="http://www.usgs.gov" target=_top>U.S. Geological Survey</a> 
        </div>
      </div>
  </body>
</html>
'''

        htmlHelp = '''
<b>Note:</b> Before submission make sure you are logged in.
To verify, click the "Login" link above. If you are not yet 
logged in you will be prompted for your username and password.
If this is your first time on POW, you will need to first request
a user account (link above).
Once you are verified, come back to this page and click the Submit button.<br>
'''
           
        with open("submit_POWfromArcMap.html", "w") as f:
           f.write(htmlTop)
           f.write(r'<div id="jobdetails">')
           f.write(r'  <form action="http://astrocloud.wr.usgs.gov/index.php" method="post">')
           f.write(r'    <input type="hidden" name="view" value="addjob"/>')
           f.write(r'    <input type="hidden" name="type" value="POW"/>')
           formURLs = '    <input type="hidden" name="urls" value="%s" />' % theURLs
           f.write(formURLs)
           formTarget = '    <input type="hidden" name="target" value="%s" />' % theTarget 
           f.write(formTarget)
           f.write(r'    <input type="submit" value="Submit"/><br><br>')
           f.write(htmlHelp)
           f.write(r'</div>')
           f.write('<br><h2>Images to be submitted:</h2>\n<br>')
           f.write('%s' % theURLs.replace(",","<br>\n"))
           f.write('<br>\n<br>')
           f.write(htmlBottom)
        webbrowser.open("submit_POWfromArcMap.html")

