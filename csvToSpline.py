#-----------------------------------------------------------------------------------------------------------------------
# Author: Brock Salmon
# Initial Creation Date: 2017-05-13
# Latest Edit: 2018-10-04, minor refactoring now that the file is public
# Filter the Alt, Lat, Lon into separate arrays from an iRacing Telemetry csv and convert them to a Max spline
#-----------------------------------------------------------------------------------------------------------------------

import csv
import math
import pymxs
from collections import defaultdict
import utm

## Changeable Variables
oldFileName = "spa.csv" # The name of the original csv file
newFileName = "spaupdated.csv" # Name of the output file without the header
linesToRemove = 9 # Change to how many lines are in the header (The data names should be in row 1)

# Max Runtime setup
rt = pymxs.runtime

# Function to cut the 9 line header off the csv file
def cut_rows(fileName, updatedFileName):
    with open(fileName, 'r') as f:
        with open(updatedFileName, 'w') as newFile:
            for _ in range(linesToRemove):
                next(f)

            for newRow in f:
                    newFile.write(newRow)


col = defaultdict(list) # Columns will be saved in a list

cut_rows(oldFileName, newFileName) # Remove header

# Read columns of the file, columns can be identified by data name (Alt, Lat, Lon)
with open(newFileName) as file:
    reader = csv.DictReader(file)
    for row in reader:
        for (i,j) in row.items():
            col[i].append(j)

# Save each column into arrays (Element 0 is unit), these can be changed to any data name in the csv(e.g. Throttle)
altArray = col['Alt']
latArray = col['Lat']
lonArray = col['Lon']

# Before the latLonArray can be filled, the 0th element of each array must be removed
altArray.pop(0)
latArray.pop(0)
lonArray.pop(0)

# Convert into UTM Coords
tempLatLonArray = []
for counter in range(len(altArray)):
    tempLatLonArray.append(utm.from_latlon(float(latArray[counter]), float(lonArray[counter])))

# Convert the new list of tuples into a list of strings that are formatted to be partitioned later
latLonArray = ["[%f] (%f) %d %s" % x for x in tempLatLonArray]

# Create new Lat and Lon arrays to store the UTM values (new Alt array to match new convention and covert to float)
utmLatArray = []
utmLonArray = []
utmAltArray = []

# Fill the new UTM arrays
for counter in range(len(latLonArray)):
    utmLatArray.append(float(latLonArray[counter].partition('[')[-1].rpartition(']')[0]))
    utmLonArray.append(float(latLonArray[counter].partition('(')[-1].rpartition(')')[0]))
    utmAltArray.append(float(altArray[counter]))

latDiff = utmLatArray[0]
lonDiff = utmLonArray[0]

for counter in range(len(utmLatArray)):
    utmLatArray[counter] -= latDiff
    utmLonArray[counter] -= lonDiff

# utmLatArray & utmLonArray now hold the UTM values of the 'Lat' and 'Lon' parameters from the Telemetry csv

# Create a spline from the UTM points
s = rt.SplineShape()
idx = rt.addNewSpline(s)

for counter in range(len(utmLatArray)):
    x = utmLatArray[counter]
    y = utmLonArray[counter]
    z = utmAltArray[counter]

    rt.addKnot(s, idx, rt.name('corner'), rt.name('curve'), rt.point3(x, y, z))

rt.updateShape(s)
