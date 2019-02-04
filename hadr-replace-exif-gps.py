"""
Summary
This tool is meant as a means for batch renaming imagery and inserting new EXIF GPS coordinates from a separate dataset. 
Ideally the location_lat and location_long columns will have been manually updated with the coordinate for the image location (and not the camera lat/long). The coordinates in these columns are fed into the new filenames and also replace the existing GPS lat/long in the image EXIF metadata for use by the relevant agencies once they have received imagery.

The renamed imagery format as an example:
Original image - DSC_0058932.JPG
Renamed image - 20160421_DAY1-001_

First run the 'Geotagged Photos to Points' tool on the raw imagery, ideally separate folders for each flight day. May need to run the tool for each respective flight day folder. 
This generates a feature class which then requires manually adding a few columns and populating their respective information.

Columns required (can be named differently):
FLIGHT_DATE
FLIGHT_NUMBER
IMAGE_NAME (likely created/populated by default as 'Name')
LOCATION_LATITUDE (DM format)
LOCATION_LONGITUDE (DM format)
LOCATION_NAME
IMAGE_CLASSIFICATION

Credits
(c) 2016 John Stowell
"""

import os
import sys
import arcpy
import pyexiv2
from arcpy import env
from fractions import Fraction

# User defined variables in ArcToolbox model
# imgAttributes - shpfile containing image attributes
# inputFilepath - folder containing raw imagery
arcpy.AddMessage('\n-------------------------------')
imgAttributes = arcpy.GetParameterAsText(0)
inputFilepath = arcpy.GetParameterAsText(1)
arcpy.CreateFolder_management(inputFilepath, "_Renamed")
outputFilepath = (os.path.join(inputFilepath+'\\_Renamed'))

dateCol = arcpy.GetParameterAsText(2) # Flight date
flightNumCol = arcpy.GetParameterAsText(3) # Flight # (Day number)
imageNameCol = arcpy.GetParameterAsText(4) # Image name without path
(eg. image01.jpg)
latitudeCol = arcpy.GetParameterAsText(5) # Location - latitude DMS format
longitudeCol = arcpy.GetParameterAsText(6) # Location - longitude DMS format
locationCol = arcpy.GetParameterAsText(7) # Location (eg. village or
island name)
classificationCol = arcpy.GetParameterAsText(8) # Classification of image

# Retrieve columns for imgAttributes shp table
arcpy.AddMessage('\nGetting relevant attributes for images...')
columns = [dateCol, flightNumCol, imageNameCol, latitudeCol,
longitudeCol, locationCol, classificationCol]

# Sequential number count
count = 0

# Get data attribute table for renaming the respective files
imgDate = [row[0] for row in arcpy.da.SearchCursor(imgAttributes, columns[0])]
imgFlight = [row[0] for row in arcpy.da.SearchCursor(imgAttributes, columns[1])]
imgName = [row[0] for row in arcpy.da.SearchCursor(imgAttributes, columns[2])]
imgLat = [row[0] for row in arcpy.da.SearchCursor(imgAttributes, columns[3])]
imgLong = [row[0] for row in arcpy.da.SearchCursor(imgAttributes, columns[4])]
imgLocation = [row[0] for row in arcpy.da.SearchCursor(imgAttributes,
columns[5])]
imgClassification = [row[0] for row in
arcpy.da.SearchCursor(imgAttributes, columns[6])]

# Compile list of input folder paths+filenames for copying later, then
add to imgList
arcpy.AddMessage('\nCompiling images from the input folder...')
imgList = []
for i, val in enumerate(imgName):
    img = str(os.path.join(inputFilepath+'\\', imgName[i]))
    imgList.extend([img])

# Cycle through list of image files and concatenate columns into a new
image filename
# then copy/rename files to the '_Renamed' folder, and lastly delete
unneeded XML data
arcpy.AddMessage('\nRenaming images and saving to: \n'+outputFilepath+'\n')
for i, val in enumerate(imgList):
    if (imgList[i].endswith(imgName[i])):
        count = count+1
        newImgName = '_'.join([str(imgDate[i]).replace(':',''),
'DAY'+str(imgFlight[i])+'.'+str(count),
imgLat[i].replace(u'\xb0','').replace('\'','').replace('"',''),
imgLong[i].replace(u'\xb0','').replace('\'','').replace('"',''),
imgLocation[i], imgClassification[i]+'.JPG'])
        arcpy.Copy_management(imgList[i], outputFilepath+'\\'+newImgName, '')
        arcpy.Delete_management(outputFilepath+'\\'+newImgName+'.XML')

        metadata = pyexiv2.ImageMetadata(outputFilepath+'\\'+newImgName)
        metadata.read() # Read existing EXIF metadata

        latitude = metadata['Exif.GPSInfo.GPSLatitude']
        tmpLatitude =
imgLat[i].replace(u'\xb0','').replace('\'','').replace('N','').replace('S','').split("
")
        latitude.value = [Fraction(tmpLatitude[0]),
Fraction(tmpLatitude[1]), Fraction(0, 1)]
        longitude = metadata['Exif.GPSInfo.GPSLongitude']
        tmpLongitude =
imgLong[i].replace(u'\xb0','').replace('\'','').replace('E','').replace('W','').split("
")
        longitude.value = [Fraction(tmpLongitude[0]),
Fraction(tmpLongitude[1]), Fraction(0, 1)]

        metadata.write() # Write new EXIF metadata
        arcpy.AddMessage(str(count)+'. Processed '+imgName[i])
    else:
        arcpy.AddMessage('\nImage(s) did not match the attribute table.')
        arcpy.AddMessage('Confirm your attribute table contains the
relevant type of columns: ')
        arcpy.AddMessage('DATE, FLIGHTNUM, IMAGE_NAME, LOC_LAT,
LOC_LONG, LOCATIONNAME, and CLASSIFICATION')

# End
arcpy.AddMessage('\nFinished.\n\n-------------------------------\n')
