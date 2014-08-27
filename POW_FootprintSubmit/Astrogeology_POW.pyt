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

        with open("submit_POWfromArcMap.html", "w") as f:
           f.write(r'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">')
           f.write(r'<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">')
           f.write(r'<head>')
           f.write(r'  <meta http-equiv="content-type" content="text/html; charset=utf-8" />')
           f.write(r'</head>')
           f.write(r'<body>')
           f.write(r'   <h2 id="title">Submit page for Map Projection On the Web</h1>')
           f.write(r'<div id="jobdetails">')
           f.write(r'  <form action="http://astrocloud.wr.usgs.gov/index.php" method="post">')
           f.write(r'    <input type="hidden" name="view" value="addjob"/>')
           f.write(r'    <input type="hidden" name="type" value="POW"/>')
           formURLs = '    <input type="hidden" name="urls" value="%s" />' % theURLs
           #formURLs = '    <textarea name="urls" value="%s" rows="10" cols="100"></textarea>' % theURLs
           f.write(formURLs)
           #f.write(r'    <p>POW File URLs</p>')
           #f.write(r'    <textarea name="urls" rows="6" cols="100"></textarea>')
           #f.write(r'    <p>Target</p>')
           formTarget = '    <input type="hidden" name="target" value="%s" />' % theTarget 
           f.write(formTarget)
           #f.write(r'    <input type="hidden" name="target" value="Mars" />')
           f.write(r'    <input type="submit" value="Submit"/>')
           #f.write(r'    <input type="hidden" name="__ncforminfo" value="rHjB90aZJn6UB6i_mcmeng1BEd1LHiTuwRUgh7jcYqWJwsER_qUO00PBAQwj05VKp6auERS67nZ6vBH-QDufrNWwbU9r6iJR"></form>')
           f.write(r'</div>')
           f.write('<br><b>Images:</b>\n<br>')
           f.write('%s' % theURLs.replace(",","<br>\n"))
           f.write(r'</body>')
           f.write(r'</html>')        
        webbrowser.open("submit_POWfromArcMap.html")

#no need to post anything just building page above.
#     
#        payload = { 'urls': theURLlist, 
#           'target': 'MARS',
#            'view': 'addjob',
#            'type': 'POW' } #,
#            #'submit': 'Submit' }
#        params = urllib.urlencode(payload)
#        POWurl = r'file::/Programming/python/POW/submit_results.html'
        #POWurl = r'http://astrocloud.wr.usgs.gov/index.php' #?view=pickfiles'

#Module URLLIB
#        results = urllib2.urlopen(POWurl, params)
#        with open("results.html", "w") as f:
#            f.write(results.read())
#        webbrowser.open("results.html")

#Module Requests
#        with requests.session() as s:
#            resp = s.get(POWurl)
#            payload['survey_session_id'] = get_session_id(resp)
#            response_post = s.post(POWurl, data=payload)
#            print response_post.text
#            arcpy.AddMessage(response_post.text)

#        r = requests.post(POWurl, payload)
#        with open("requests_results.html", "w") as f:
#            f.write(r.content)
#        webbrowser.open("requests_results.html")
