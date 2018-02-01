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
import glob


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


def calculatePersistanceDiagrams():
    rootdir = 'toprocess/'
    removeDsStore(rootdir)
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
                print curentfile
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
                    m1, m2 = bx, by

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

            for sublistZ in zig_zag_homology_object.zero_dim_persistence:
                ind_1Z = sublistZ[0]
                if (str(sublistZ[1]) == "inf"):
                    ind_2Z = 12
                else:
                    ind_2Z = sublistZ[1]

                xCoordsZ.append(ind_1Z)
                yCoordsZ.append(ind_2Z)

                plt.scatter(xCoordsZ, yCoordsZ)

            for sublisto in zig_zag_homology_object.one_dim_persistence:
                ind_1o = sublisto[0]
                if (str(sublisto[1]) == "inf"):
                    ind_2o = 12
                else:
                    ind_2o = sublisto[1]

                xCoordso.append(ind_1o)
                yCoordso.append(ind_2o)

            plt.scatter(xCoordsZ, yCoordsZ)
            plt.plot(xCoordso, yCoordso, 'k-', lw=2)
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


# getGenusFromNbn(sys.argv[1])

splitDataByCommonName()
splitDataIntoYearAndMonth()
calculatePersistanceDiagrams()
