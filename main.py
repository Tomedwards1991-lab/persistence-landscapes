# to run python main.py Anser
# this will give the NBN dataset for geese

import sys
import shutil
import math
import numpy
import grid_simplex
import zig_zag_homology
import csv as c
import subprocess
from scipy import stats
import pyproj
import matplotlib.pyplot as plt
import os
import urllib2
import zipfile
import pandas as pd


# from mpl_toolkits.basemap import Basemap

def preruncleanup():
    if os.path.exists('toprocess'):
        shutil.rmtree('toprocess')


def getGenusFromNbn(genus):
    # Anser
    url = "https://records-ws.nbnatlas.org/occurrences/index/download?reasonTypeId=10&q=*:*&fq=genus:" + genus + "&lat=53.371107&lon=-1.560963&radius=200.0&qa=none"
    f = urllib2.urlopen(url)
    data = f.read()
    with open("data.zip", "wb") as code:
        code.write(data)

    path_to_zip_file = "./data.zip"
    path_to_file = "./"
    zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    zip_ref.extractall(path_to_file)
    zip_ref.close()

    csvfile = 'data.csv'

    processDataFromApi(csvfile)


def processDataFromApi(csvfile):
    csv = pd.read_csv(csvfile, sep=',')
    j = 0

    file = open('processeddata.csv', 'w')

    file.write('id,lat,lng,year,month,common name\n')
    for i in csv['Year']:
        # if data
        if (numpy.isnan(i) == False and numpy.isnan(csv['Decimal latitude (WGS84)'][j]) == False and numpy.isnan(
                csv['Decimal latitude (WGS84).1'][j]) == False and numpy.isnan(csv['Month'][j]) == False and pd.isnull(
            csv['Common name'][j]) == False):
            # id lat lng year
            file.write(str(csv['Record ID'][j]) + "," + str(csv['Decimal latitude (WGS84)'][j]) + "," + str(
                csv['Decimal latitude (WGS84).1'][j]) + "," + str(int(csv['Year'][j])) + "," + str(
                int(csv['Month'][j])) + "," + str(csv['Common name'][j]) + "\n")
        else:
            print "Data is missing"
        j = j + 1
    file.close()


def splitByColumn(csvToProcess, splitBy, directory):
    df = pd.read_csv(csvToProcess)

    if not os.path.exists(directory):
        os.makedirs(directory)

    for i, g in df.groupby(splitBy):
        g.to_csv(directory + '/{}.csv'.format(i), header=True, index_label=False, index=False)
    os.remove(csvToProcess)


def splitByMonth(csvToProcess, splitBy, directory):
    df = pd.read_csv(csvToProcess)

    if not os.path.exists(directory):
        os.makedirs(directory)

    for i, g in df.groupby(splitBy):
        name = str(chr(ord('a') + i - 1))
        g.to_csv(directory + '/{}.csv'.format(name), header=True, index_label=False, index=False)
    os.remove(csvToProcess)


def calcMean(kdeOutputArray):
    # Calculate the mean
    summ = 0
    countMean = 0
    for x in range(0, len(kdeOutputArray)):
        for y in range(0, len(kdeOutputArray[0])):
            summ = summ + kdeOutputArray[x][y]
            countMean = countMean + 1
    mean = summ / countMean
    return mean


def splitDataIntoYearAndMonth():
    for commonnames in os.listdir('toprocess'):
        csvToProcess = 'toprocess/' + commonnames
        splitBy = 'year'
        name = commonnames.split('.')[0]
        workingDiredctory = 'toprocess/' + name
        splitByColumn(csvToProcess, splitBy, workingDiredctory)
        for years in os.listdir('toprocess/' + name):
            csvToProcess = 'toprocess/' + name + '/' + years
            splitBy = 'month'
            year = years.split('.')[0]
            workingDiredctory = 'toprocess/' + name + '/' + year
            splitByMonth(csvToProcess, splitBy, workingDiredctory)


def splitDataByCommonName():
    csvToProcess = 'processeddata.csv'
    splitBy = 'common name'
    workingDiredctory = 'toprocess'
    splitByColumn(csvToProcess, splitBy, workingDiredctory)


def removeDsStore(directory):
    if os.path.exists(directory + "/.DS_Store"):
        os.remove(directory + "/.DS_Store")


def createMap(comName, year, month, lattitude, longitude):
    rootdir = 'toprocess/'
    removeDsStore(rootdir)
    with open(rootdir + "/" + comName + "/" + year + "/map.html", 'w') as myFile:
        myFile.write("<!DOCTYPE html>")
        myFile.write("<html>")
        myFile.write("  <meta http-equiv=\"content-type\" content=\"text/html; charset=UTF-8\" />")
        myFile.write("  <title>Map Markers</title>")
        myFile.write(
            "  <script src=\"http://maps.google.com/maps/api/js?key=AIzaSyBCHL594XNZtJhgacHTs3Cs96w-TuJEeZQ&sensor=false\"")
        myFile.write("          type=\"text/javascript\"></script>")
        myFile.write("  <style>")
        myFile.write("    html, body {")
        myFile.write("      height: 100%;")
        myFile.write("      margin: 0;")
        myFile.write("      padding: 0;")
        myFile.write("    }")
        myFile.write("    #map {")
        myFile.write("      height: 100%;")
        myFile.write("    }")
        myFile.write("  </style>")
        myFile.write("</head>")
        myFile.write("<body>")
        myFile.write("<div id=" + "map" + "></div>")
        myFile.write("")
        myFile.write("  <script type=\"text/javascript\">")
        myFile.write("    var locations = [")
        for b in range(len(lattitude)):
            myFile.write("['" + comName + ":" + str(year) + ":" + str(month) + "'," + str(lattitude[b]) + "," + str(
                longitude[b]) + "],")
        myFile.write(" ];")
        myFile.write("")
        myFile.write("")
        myFile.write("")
        myFile.write("    var map = new google.maps.Map(document.getElementById('map'), {")
        myFile.write("      zoom: 7,")
        myFile.write("      center: new google.maps.LatLng(51.489475, 0.067588),")
        myFile.write("      mapTypeId: google.maps.MapTypeId.ROADMAP")
        myFile.write("    });")
        myFile.write("")
        myFile.write("    var infowindow = new google.maps.InfoWindow();")
        myFile.write("")
        myFile.write("    var marker, i;")
        myFile.write("")
        myFile.write("    for (i = 0; i < locations.length; i++) {  ")
        myFile.write("      marker = new google.maps.Marker({")
        myFile.write("        position: new google.maps.LatLng(locations[i][1], locations[i][2]),")
        myFile.write("        map: map")
        myFile.write("      });")
        myFile.write("")
        myFile.write("      google.maps.event.addListener(marker, 'click', (function(marker, i) {")
        myFile.write("        return function() {")
        myFile.write("        infowindow.setContent(locations[i][0]);")
        myFile.write("          infowindow.open(map, marker);")
        myFile.write("        }")
        myFile.write("      })(marker, i));")
        myFile.write("    }")
        myFile.write("  </script>")
        myFile.write("</body>")
        myFile.write("</html>")
        myFile.close()


def calculatePersistanceDiagrams():
    rootdir = 'toprocess/'
    removeDsStore(rootdir)
    totalNumberPersistenceObjectsYearsAll = []
    for comNames in os.listdir(rootdir):
        removeDsStore(rootdir + "/" + comNames)
        for years in os.listdir(rootdir + "/" + comNames):
            # Initialize grid of points
            grid_simplex_object = grid_simplex.grid_simplex(100, 100)
            zig_zag_homology_object = zig_zag_homology.zig_zag_homology(grid_simplex_object.simplices)
            removeDsStore(rootdir + "/" + comNames + "/" + years)
            loopPos = 0
            for months in os.listdir(rootdir + "/" + comNames + "/" + years):
                removeDsStore(rootdir + "/" + comNames + "/" + years + "/" + months)
                curentfile = rootdir + "/" + comNames + "/" + years + "/" + months
                # print curentfile
                stringlat = []
                stringlng = []
                lat = []
                lng = []

                count = 0
                curMonth = c.reader(open(curentfile, 'rU'))
                curMonth.next()

                for row in curMonth:
                    latitude = row[1]
                    longitude = row[2]
                    if (latitude != "" and longitude != ""):
                        stringlat.append(latitude)
                        stringlng.append(longitude)
                        count = count + 1
                if (count > 1 and len(set(stringlat)) != 1):
                    for item in stringlat:
                        lat.append(float(item))

                    for item in stringlng:
                        lng.append(float(item))

                    # Define projection for the British National Grid
                    bng = pyproj.Proj(init='epsg:27700')

                    # do british projection
                    bx, by = bng(lat, lng)
                    monthss = months.replace('.csv', '')
                    createMap(comNames, years, monthss, lat, lng)

                    m1, m2 = lat, lng

                    xmin = min(m1)
                    xmax = max(m1)
                    ymin = min(m2)
                    ymax = max(m2)

                    # Apply KDE to the coordiantes and print the results on a grid
                    X, Y = numpy.mgrid[xmin:xmax:100j, ymin:ymax:100j]
                    positions = numpy.vstack([X.ravel(), Y.ravel()])
                    values = numpy.vstack([m1, m2])
                    kernel = stats.gaussian_kde(values, bw_method='silverman')
                    kdeOutputArray = numpy.reshape(kernel(positions).T, X.shape)

                    mean = calcMean(kdeOutputArray)

                    # Turn the points on in the grid
                    a = numpy.zeros((len(kdeOutputArray), len(kdeOutputArray[0])), dtype=int)
                    for x in range(0, len(kdeOutputArray)):
                        for y in range(0, len(kdeOutputArray[0])):
                            if kdeOutputArray[x][y] > mean:
                                a[x][y] = 1

                    grid_simplex_object.update_active_simplex(a)

                    zig_zag_homology_object.update_simplex_active(grid_simplex_object.simplex_active, loopPos)
                    loopPos = loopPos + 1
                    # grid_simplex_object.plot_active_simplex()

            xCoordsZ = []
            yCoordsZ = []
            xCoordso = []
            yCoordso = []
            labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

            for sublistZ in zig_zag_homology_object.zero_dim_persistence:
                ind_1Z = sublistZ[0]
                if (str(sublistZ[1]) == "inf"):
                    ind_2Z = 12
                else:
                    ind_2Z = sublistZ[1]

                xCoordsZ.append(ind_1Z)
                yCoordsZ.append(ind_2Z)

                # plt.scatter(xCoordsZ,yCoordsZ)
            for sublisto in zig_zag_homology_object.one_dim_persistence:
                ind_1o = sublisto[0]
                if (str(sublisto[1]) == "inf"):
                    ind_2o = 12
                else:
                    ind_2o = sublisto[1]

                xCoordso.append(ind_1o)
                yCoordso.append(ind_2o)
            totalNoObjects = 0
            totalNoObjects = len(xCoordsZ)
            total_persistence_objects = []
            total_persistence_objects = [totalNoObjects]
            file_persistent_objects = open(rootdir + "/" + comNames + "/" + years + "/persistanceobjects.txt", "w")
            for item_object in total_persistence_objects:
                file_persistent_objects.write("%s\n" % item_object)
            file_persistent_objects.close()

            plt.scatter(xCoordsZ, yCoordsZ)
            plt.plot(xCoordso, yCoordso, 'k-', lw=2)
            plt.title(comNames + "_" + years)
            plt.axis([0, 12, 0, 12])
            plt.xlabel('Start time')
            plt.ylabel('End time')
            # plt.show()
            plt.savefig(rootdir + "/" + comNames + "/" + years + '/scatter.png')
            plt.clf()

            # Print results
            fh = open(rootdir + "/" + comNames + "/" + years + "/persistancediag.txt", "w")
            fh.write("zero_dim_persistence: " + str(zig_zag_homology_object.zero_dim_persistence))
            fh.write("one_dim_persistence: " + str(zig_zag_homology_object.one_dim_persistence))
            fh.close()

            # When fihished turn off all points in the grid.
            zig_zag_homology_object.remove_all_simplex()
            zig_zag_homology_object.sort_persistence()


def countmonths(directory):
    numberofmonths = 0
    for months in os.listdir(directory):
        if (months.endswith(".csv")):
            numberofmonths = numberofmonths + 1

    return numberofmonths


def noMonthsWithResults():
    noOfMonths = []
    yearsList = []
    noOfMonthsPerYear = []
    noOfMonthsPerYearAll = []
    rootdir = 'toprocess/'
    removeDsStore(rootdir)
    for comNames in os.listdir(rootdir):
        removeDsStore(rootdir + "/" + comNames)
        for years in os.listdir(rootdir + "/" + comNames):
            locationofcuryear = rootdir + "/" + comNames + "/" + years
            listMonths = countmonths(locationofcuryear)

            # print "years:", rootdir + "/" +comNames + "/" + years
            # print "listMonths:",listMonths
            number_months = listMonths
            noOfMonths.append(number_months)
            yearsList.append(years)
            noOfMonthsPerYear = [comNames, years, number_months]
            noOfMonthsPerYearAll.append(noOfMonthsPerYear)
            # print "year:", years
            # print "No of months:",number_months
    return noOfMonthsPerYearAll


def totalNoOccurences():
    rootdir = 'toprocess/'
    removeDsStore(rootdir)
    totalNumOfRecordsPerYearAll = []
    for comNames in os.listdir(rootdir):
        removeDsStore(rootdir + "/" + comNames)
        for years in os.listdir(rootdir + "/" + comNames):
            noMonthsperYear = 0
            recordsWithinYearList = []
            totalNumOfRecordsPerYear = []
            removeDsStore(rootdir + "/" + comNames + "/" + years)
            for months in os.listdir(rootdir + "/" + comNames + "/" + years):
                if (months.endswith(".csv")):
                    curentfile = rootdir + "/" + comNames + "/" + years + "/" + months
                    print curentfile
                    curMonth = c.reader(open(curentfile, 'rU'))
                    curMonth.next()
                    recordsWithinMonth = 0
                    for row in curMonth:
                        recordsWithinMonth = recordsWithinMonth + 1
                        print "count per month intside loop:", recordsWithinMonth
                    recordsWithinYearList.append(recordsWithinMonth)
            totalNumOfRecordsPerYear = [sum(recordsWithinYearList)]
            totalNumOfRecordsPerYearAll.append(totalNumOfRecordsPerYear)
    return totalNumOfRecordsPerYearAll


def avgNoOccurences():
    rootdir = 'toprocess/'
    removeDsStore(rootdir)
    avgNumOfRecordsPerYearAll = []
    for comNames in os.listdir(rootdir):
        removeDsStore(rootdir + "/" + comNames)
        for years in os.listdir(rootdir + "/" + comNames):
            noMonthsperYear = 0
            recordsWithinYearList = []
            avgNumOfRecordsPerYear = []
            sumRecordsWithinYear = 0
            avgNumPerYear = 0.0
            removeDsStore(rootdir + "/" + comNames + "/" + years)
            for months in os.listdir(rootdir + "/" + comNames + "/" + years):
                if (months.endswith(".csv")):
                    curentfile = rootdir + "/" + comNames + "/" + years + "/" + months
                    curMonth = c.reader(open(curentfile, 'rU'))
                    curMonth.next()
                    recordsWithinMonth = 0
                    for row in curMonth:
                        recordsWithinMonth = recordsWithinMonth + 1
                    # print "count per month outside loop:",recordsWithinMonth
                recordsWithinYearList.append(recordsWithinMonth)
            noMonthsperYear = len(os.listdir(rootdir + "/" + comNames + "/" + years))
            sumRecordsWithinYear = sum(recordsWithinYearList)
            avgNumPerYear = sumRecordsWithinYear / noMonthsperYear
            avgNumOfRecordsPerYear = [avgNumPerYear]
            avgNumOfRecordsPerYearAll.append(avgNumOfRecordsPerYear)
    return avgNumOfRecordsPerYearAll


def numberPersisentObjects():
    rootdir = 'toprocess/'
    removeDsStore(rootdir)
    persObjects = []
    persObjectsList = []
    for comNames in os.listdir(rootdir):
        removeDsStore(rootdir + "/" + comNames)
        for years in os.listdir(rootdir + "/" + comNames):
            filePersObjects = open(rootdir + "/" + comNames + "/" + years + "/persistanceobjects.txt", "r")
            for line in filePersObjects:
                line = line.rstrip()
                persObjects = [line]
                persObjectsList.append(persObjects)
            # os.remove(rootdir + "/" +comNames+"/"+years + "/persistanceobjects.txt")
    return persObjectsList


def calcStatistics():
    noMonthsperYear = noMonthsWithResults()
    totalNoPerYear = totalNoOccurences()
    avgNoOccurencesPerYear = avgNoOccurences()
    numberPersisentObjectsPerYear = numberPersisentObjects()

    columnNames = ["name_species", "year", "number_months_with_results", "total_number_occurances",
                   "avg_number_occurances", "total_number_persistence_objects"]
    for i, element in enumerate(noMonthsperYear):
        noMonthsperYear[i].extend(totalNoPerYear[i])
        noMonthsperYear[i].extend(avgNoOccurencesPerYear[i])
        noMonthsperYear[i].extend(numberPersisentObjectsPerYear[i])
    noMonthsperYear.insert(0, columnNames)

    statisticsFile = open('statistics.csv', 'w')
    with statisticsFile:
        writer = c.writer(statisticsFile)
        writer.writerows(noMonthsperYear)
    print("Writing complete")


# getGenusFromNbn(sys.argv[1])
# splitDataByCommonName()
# splitDataIntoYearAndMonth()
# calculatePersistanceDiagrams()


calcStatistics()
