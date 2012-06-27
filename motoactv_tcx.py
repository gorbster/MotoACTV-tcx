#!/usr/bin/python
# Requires ElementTree (http://effbot.org/zone/element-index.htm)
# It helps to pipe the output of this script through tidy, e.g.:
# ./csv_to_tcx.py rawDataCsv.csv | tidy -i -xml

import time
import csv
import math
import itertools
import sys

from elementtree.ElementTree import Element, SubElement, dump, tostring
from elementtree.SimpleXMLWriter import XMLWriter

MPS_TO_MPH = 2.237

def XMLHeader():
    return '<?xml version="1.0" encoding="UTF-8"?>'

def DictToXML(inp):
    i_root = Element('item')
    for (field, val) in inp.iteritems():
        SubElement(i_root, field).text = val
        return i_root

def stringGMTimeFromEpoch(epoch):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))
        
def earliestTimeInDict(theDict):
    earliestTime = 0.0
    
    for row in theDict:
        epoch = row['timestamp_epoch']
        if earliestTime == 0:
            earliestTime = epoch
        elif epoch < earliestTime:
            earliestTime = epoch
            
        return earliestTime
        
def main():
    if len(sys.argv) != 2: 
            print 'Usage: ' + sys.argv[0] + ' <CSV file>' 
            sys.exit(1) 
        
    pathToCSV = sys.argv[1]
    
    f = open(pathToCSV)
    dataDict = csv.DictReader(f)
    intensity = "Resting"
    triggerMethod = "Distance"

    tcxTrackpoints = {}
    earliestEpochMS = earliestTimeInDict(dataDict)
    earliestEpoch = math.floor(int(earliestEpochMS) / 1000)

    root = Element("TrainingCenterDatabase")
    root.set("xsi:schemaLocation", "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd")
    root.set("xmlns:ns2", "http://www.garmin.com/xmlschemas/UserProfile/v2")
    root.set("xmlns:ns3", "http://www.garmin.com/xmlschemas/ActivityExtension/v2")
    root.set("xmlns:ns4", "http://www.garmin.com/xmlschemas/ProfileExtension/v1")
    root.set("xmlns:ns5", "http://www.garmin.com/xmlschemas/ActivityGoals/v1")
    root.set("xmlns", "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")

    actsElement = SubElement(root, "Activities")
    actElement = SubElement(actsElement, "Activity", Sport="Running")

    idElement = SubElement(actElement, "Id")
    idElement.text = stringGMTimeFromEpoch(earliestEpoch)

    lastTimeEpoch = 0
    
    lapElement = SubElement(actElement, "Lap", StartTime=stringGMTimeFromEpoch(earliestEpoch))
    
    totalDistanceMeters = 0
    maxSpeed = 0
    calories = 0.0
    maxBPM = 0    
    numRows = 0
    totalBPM = 0
    
    trackpoints = list()
    
    for row in dataDict:
        trackpointElement = Element("Trackpoint")
        trackpoints.append(trackpointElement)
        
        # TIME
        epochMS = row['timestamp_epoch']
        epoch = math.floor(int(epochMS) / 1000)
        timeElement = SubElement(trackpointElement, "Time")
        timeElement.text = stringGMTimeFromEpoch(epoch)

        # POSITION
        latValue = row['LATITUDE']
        longValue = row['LONGITUDE']
        
        if (abs(float(latValue)) <= 180 and abs(float(longValue)) <= 180
            and abs(float(latValue)) > 0.1 and abs(float(longValue)) > 0.1):
            posElement = SubElement(trackpointElement, "Position")
            latElement = SubElement(posElement, "LatitudeDegrees")
            latElement.text = latValue
            longElement = SubElement(posElement, "LongitudeDegrees")
            longElement.text = longValue
        
        # Altitude
        alt = row['ELEVATION']
        altElement = SubElement(trackpointElement, "AltitudeMeters")
        altElement.text = alt

        # DISTANCE
        distanceMeters = row['DISTANCE']
        distElement = SubElement(trackpointElement, "DistanceMeters")
        distElement.text = distanceMeters

        # BPM
        heartRate = math.trunc(float(row['HEARTRATE']))
        # if heartRate > 0:
        bpmElement = SubElement(trackpointElement, 'HeartRateBpm xsi:type=\"HeartRateInBeatsPerMinute_t\"')
        bpmValElement = SubElement(bpmElement, "Value")
        bpmValElement.text = str(heartRate)
                
        extElement = SubElement(trackpointElement, 'Extensions')
        
        # SPEED
        speed = float(row['SPEED'])
        speed *= MPS_TO_MPH
        ns3Element = SubElement(extElement, 'ns3:TPX')
        speedElement = SubElement(ns3Element, 'ns3:Speed')
        speedElement.text = str(speed)
                
        if lastTimeEpoch == 0 or epoch > lastTimeEpoch:
            lastTimeEpoch = epoch

        if totalDistanceMeters == 0 or float(distanceMeters) > float(totalDistanceMeters):
            totalDistanceMeters = distanceMeters

        rowCalories = row['CALORIEBURN']        
        calories = rowCalories

        if maxBPM == 0 or heartRate > maxBPM:
            maxBPM = heartRate

        numRows += 1
        totalBPM += heartRate
        
    # TIME    
    totalTimeSeconds = lastTimeEpoch - earliestEpoch
    avgBPM = totalBPM / numRows
        
    totalTimeElement = SubElement(lapElement, "TotalTimeSeconds")
    totalTimeElement.text = str(int(totalTimeSeconds))

    # DISTANCE
    totalDistanceElement = SubElement(lapElement, "DistanceMeters")
    totalDistanceElement.text = totalDistanceMeters
    
    # CALORIES
    totalCalsElement = SubElement(lapElement, "Calories")
    totalCalsElement.text = str(int(float(calories)))
    
    # BPM
    # if avgBPM > 0:
    avgBPMElement = SubElement(lapElement, 'AverageHeartRateBpm xsi:type="HeartRateInBeatsPerMinute_t"')
    avgBPMValElement = SubElement(avgBPMElement, "Value")
    avgBPMValElement.text = str(int(avgBPM))

    # if maxBPM > 0:
    maxBPMElement = SubElement(lapElement, 'MaximumHeartRateBpm xsi:type="HeartRateInBeatsPerMinute_t"')
    maxBPMValElement = SubElement(maxBPMElement, "Value")
    maxBPMValElement.text = str(int(maxBPM))
    
    # INTENSITY
    intensityElement = SubElement(lapElement, "Intensity")
    intensityElement.text = "Active"

    #TRIGGER
    triggerElement = SubElement(lapElement, "TriggerMethod")
    triggerElement.text = "Distance"

    # Append trackpoints
    trackElement = SubElement(lapElement, "Track")    
    for trackpoint in trackpoints:
        trackElement.append(trackpoint)
    
    print XMLHeader() + tostring(root)

main()
