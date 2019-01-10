from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
import pymysql
import re
import sys
import csv
import collections
import math
from pyproj import Proj, transform


class gridFunctions(object):
    # Four corners of the map / grid
    lowLat = 49.00
    highLat = 61.00
    leftLon = -11.50
    rightLon = 2.00

    # cell size - min *7, *10, *14, *28, *70, max *700
    # noMiles = 28
    noMiles = 10

    def numOfCells(noMiles):
        # sizeOfMap = 700
        sizeOfMap = 800
        noCells = abs(sizeOfMap / noMiles)

        return noCells

    columnNum = numOfCells(noMiles)

    def createGrid(self, columnNum, lowLat, highLat, leftLon, rightLon):
        lonArray = []
        latArray = []
        squareWidth = ((leftLon - rightLon) / columnNum)
        plotLon = leftLon
        tempRowNum = 0
        while plotLon <= rightLon:
            # plot the top of each column
            lonArray.append(plotLon)
            latArray.append(highLat)
            tempRowNum = tempRowNum + 1
            plotLat = highLat
            # for each column plot each of the rows.
            while plotLat >= lowLat:
                plotLat = plotLat + (squareWidth / 1.75)
                lonArray.append(plotLon)
                latArray.append(plotLat)
                tempRowNum = tempRowNum + 1
            plotLon = plotLon - squareWidth
            rowNum = tempRowNum
            tempRowNum = 0
        lowLat = plotLat
        return (lonArray, latArray, lowLat, rowNum)

    def getCSVCount(self, cur):
        query = "SELECT Count(id) FROM nbn_adder"
        cur.execute(query)
        csvCount = str(cur.fetchone())
        csvCount = re.search(r'\d+', csvCount)
        csvCount = csvCount.group()
        return (csvCount)

    def getSQLCount(self, cur):
        query = "SELECT Count(id) FROM flickr_adder;"
        cur.execute(query)
        sqlCount = str(cur.fetchone())
        sqlCount = re.search(r'\d+', sqlCount)
        sqlCount = sqlCount.group()
        return (sqlCount)

    def getCellByID(self, gridLatArray, gridLonArray, squareID, rowNum):
        getCellLat = []
        getCellLat.append(gridLatArray[squareID])
        getCellLat.append(gridLatArray[squareID + 1])
        getCellLat.append(gridLatArray[squareID + rowNum + 1])
        getCellLat.append(gridLatArray[squareID + rowNum])
        getCellLat.append(gridLatArray[squareID])

        getCellLon = []
        getCellLon.append(gridLonArray[squareID])
        getCellLon.append(gridLonArray[squareID + 1])
        getCellLon.append(gridLonArray[squareID + rowNum + 1])
        getCellLon.append(gridLonArray[squareID + rowNum])
        getCellLon.append(gridLonArray[squareID])

        return getCellLon, getCellLat

    def getCellPhotoCountSQL(self, getCellLon, getCellLat,cur):
        query = "SELECT Count(id) FROM flickr_data WHERE longitude >= " + str(
            getCellLon[0]) + " and longitude <=" + str(getCellLon[3]) + " and latitude >= " + str(
            getCellLat[1]) + " and latitude <=" + str(getCellLat[0])
        cur.execute(query)
        count = str(cur.fetchone())
        count = re.search(r'\d+', count)
        count = count.group()
        return count

    def getCellPhotoCountCSV(self, getCellLon, getCellLat,cur):

        query = "SELECT Count(id) FROM nbn_data WHERE longitude >= " + str(getCellLon[0]) + " and longitude <=" + str(
            getCellLon[3]) + " and latitude >= " + str(getCellLat[1]) + " and latitude <=" + str(
            getCellLat[0])
        cur.execute(query)
        count = str(cur.fetchone())
        count = re.search(r'\d+', count)
        count = count.group()
        return count


class mathComparisons(object):

    def confusionMatrix(self, sqlCountArray, csvCountArray, keysList):

        # http://www.dataschool.io/simple-guide-to-confusion-matrix-terminology/
        total = len(sqlCountArray)
        valuesList = []
        identifiersSQL_dict = {}
        identifiersCSV_dict = {}
        # print keysList
        for i in range(0, total):
            valuesList.append(i)
            identifiersSQL_dict[keysList[i]] = sqlCountArray[i]
            identifiersCSV_dict[keysList[i]] = csvCountArray[i]

        truePositive = 0
        trueNegative = 0
        falsePositive = 0
        falseNegative = 0
        # print identifiers_dict
        # for i in range(0,total):
        subdictSQL = {}
        subdictCSV = {}

        for k, i in identifiersSQL_dict.iteritems():
            if (k - 1) in identifiersSQL_dict.keys() and (k + 1) in identifiersSQL_dict.keys() and (
                    k + 39) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in
                                  (k, k - 1, k + 1, k + 39, k + 40, k + 41, k - 41, k - 40, k - 39))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in
                                  (k, k - 1, k + 1, k + 39, k + 40, k + 41, k - 41, k - 40, k - 39))
                # print subdictCSV.values()[index]
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0 or subdictCSV.values()[7] != 0 or
                        subdictCSV.values()[8] != 0):
                    truePositive = truePositive + 1

                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0 and subdictCSV.values()[7] == 0 and
                        subdictCSV.values()[8] == 0):
                    trueNegative = trueNegative + 1

                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0 or subdictCSV.values()[7] != 0 or
                        subdictCSV.values()[8] != 0):
                    falseNegative = falseNegative + 1

                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] != 0 and
                        subdictCSV.values()[2] != 0 and subdictCSV.values()[3] != 0 and subdictCSV.values()[4] != 0 and
                        subdictCSV.values()[5] != 0 and subdictCSV.values()[6] != 0 and subdictCSV.values()[7] != 0 and
                        subdictCSV.values()[8] != 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) not in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 1, k + 39))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 1, k + 39))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 1) in identifiersSQL_dict.keys() and (
                    k + 39) in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 1, k + 1, k + 39))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 1, k + 1, k + 39))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) not in identifiersSQL_dict.keys() and (k + 1) in identifiersSQL_dict.keys() and (
                    k + 39) not in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 40, k - 39, k + 1))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 40, k - 39, k + 1))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 1) not in identifiersSQL_dict.keys() and (
                    k + 39) not in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 1, k - 39, k - 40, k - 41))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 1, k - 39, k - 40, k - 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) not in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 1, k + 1, k - 39, k - 40))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 1, k + 1, k - 39, k - 40))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) not in identifiersSQL_dict.keys() and (k + 39) not in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k + 1, k - 39, k - 40, k - 41))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k + 1, k - 39, k - 40, k - 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) not in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 1, k + 1, k + 40, k + 41))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 1, k + 1, k + 40, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 1, k + 1, k + 39, k + 40, k + 41))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 1, k + 1, k + 39, k + 40, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) not in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 1, k + 1, k + 41, k + 39, k - 41))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 1, k + 1, k + 41, k + 39, k - 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) not in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 40, k - 41, k - 1, k + 39, k - 39))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 40, k - 41, k - 1, k + 39, k - 39))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) not in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 1, k + 39, k - 40, k + 40))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 1, k + 39, k - 40, k + 40))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) not in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 1, k + 39, k - 40, k - 39))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 1, k + 39, k - 40, k - 39))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) not in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 1, k - 39, k - 40, k + 1))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 1, k - 39, k - 40, k + 1))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) not in identifiersSQL_dict.keys() and (k + 39) not in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 40, k - 39, k + 1, k + 41))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 40, k - 39, k + 1, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) not in identifiersSQL_dict.keys() and (k + 39) not in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 40, k + 40, k - 39, k + 1, k + 41))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 40, k + 40, k - 39, k + 1, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) not in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict(
                    (k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 1, k + 39, k - 40, k - 39, k + 40))
                subdictCSV = dict(
                    (k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 1, k + 39, k - 40, k - 39, k + 40))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict(
                    (k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 1, k + 39, k - 40, k - 39, k + 40, k + 1))
                subdictCSV = dict(
                    (k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 1, k + 39, k - 40, k - 39, k + 40, k + 1))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0 or subdictCSV.values()[7] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0 and subdictCSV.values()[7] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0 or subdictCSV.values()[7] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0 and subdictCSV.values()[7] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict(
                    (k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 1, k + 39, k - 40, k - 39, k + 1))
                subdictCSV = dict(
                    (k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 1, k + 39, k - 40, k - 39, k + 1))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict(
                    (k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 1, k + 39, k - 40, k - 39, k + 40, k + 1))
                subdictCSV = dict(
                    (k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 1, k + 39, k - 40, k - 39, k + 40, k + 1))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0 or subdictCSV.values()[7] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0 and subdictCSV.values()[7] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0 or subdictCSV.values()[7] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0 and subdictCSV.values()[7] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) not in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict(
                    (k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 1, k + 41, k - 40, k - 39, k + 1))
                subdictCSV = dict(
                    (k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 1, k + 41, k - 40, k - 39, k + 1))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) not in identifiersSQL_dict.keys() and (k + 39) not in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict(
                    (k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 40, k - 39, k + 1, k + 40, k + 41))
                subdictCSV = dict(
                    (k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 40, k - 39, k + 1, k + 40, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) not in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k + 39, k + 40, k + 41, k + 1, k - 39))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k + 39, k + 40, k + 41, k + 1, k - 39))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) not in identifiersSQL_dict.keys() and (
                    k + 1) not in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 1, k - 40, k - 39))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 1, k - 40, k - 39))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) not in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 1, k - 40, k - 39, k + 1))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 1, k - 40, k - 39, k + 1))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) not in identifiersSQL_dict.keys() and (k + 39) not in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k + 40, k - 39, k + 1, k + 41))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k + 40, k - 39, k + 1, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) not in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k + 40, k + 39, k + 1, k + 41))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k + 40, k + 39, k + 1, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) not in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 1, k + 39, k + 40))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 1, k + 39, k + 40))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 1, k + 39, k - 40, k - 39, k + 1))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 1, k + 39, k - 40, k - 39, k + 1))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 1, k + 39, k + 40, k + 41, k + 1))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 1, k + 39, k + 40, k + 41, k + 1))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) not in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 39, k + 39, k + 40, k + 41, k + 1))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 39, k + 39, k + 40, k + 41, k + 1))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) not in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 1, k + 39, k + 40, k + 41))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 1, k + 39, k + 40, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) not in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 40, k + 1, k + 39, k + 40, k + 41))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 40, k + 1, k + 39, k + 40, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) not in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) not in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 1, k - 40, k - 39, k + 1, k + 41))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 1, k - 40, k - 39, k + 1, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) not in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 1, k - 40, k + 39, k + 40, k + 41))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 1, k - 40, k + 39, k + 40, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) not in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 1, k + 39, k - 40, k + 40))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 1, k + 39, k - 40, k + 40))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) not in identifiersSQL_dict.keys() and (k + 39) not in identifiersSQL_dict.keys() and (
                    k + 1) not in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k + 41, k + 40))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k + 41, k + 40))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) not in identifiersSQL_dict.keys() and (k + 39) not in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k + 1, k + 41, k + 40))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k + 1, k + 41, k + 40))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) not in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) not in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 1, k + 39, k + 40))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 1, k + 39, k + 40))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) not in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict(
                    (k, identifiersSQL_dict[k]) for k in (k, k + 39, k - 40, k + 40, k - 39, k + 1, k + 41))
                subdictCSV = dict(
                    (k, identifiersCSV_dict[k]) for k in (k, k + 39, k - 40, k + 40, k - 39, k + 1, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict(
                    (k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 1, k + 39, k + 40, k + 1, k + 41))
                subdictCSV = dict(
                    (k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 1, k + 39, k + 40, k + 1, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) not in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict(
                    (k, identifiersSQL_dict[k]) for k in (k, k - 40, k - 41, k - 1, k + 39, k + 40, k + 41))
                subdictCSV = dict(
                    (k, identifiersCSV_dict[k]) for k in (k, k - 40, k - 41, k - 1, k + 39, k + 40, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) not in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k + 39, k + 40, k - 39, k + 1, k + 41))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k + 39, k + 40, k - 39, k + 1, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict(
                    (k, identifiersSQL_dict[k]) for k in (k, k - 1, k + 39, k + 40, k - 39, k + 1, k + 41))
                subdictCSV = dict(
                    (k, identifiersCSV_dict[k]) for k in (k, k - 1, k + 39, k + 40, k - 39, k + 1, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict(
                    (k, identifiersSQL_dict[k]) for k in (k, k - 1, k + 39, k - 40, k + 40, k - 39, k + 1, k + 41))
                subdictCSV = dict(
                    (k, identifiersCSV_dict[k]) for k in (k, k - 1, k + 39, k - 40, k + 40, k - 39, k + 1, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0 or subdictCSV.values()[7] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0 and subdictCSV.values()[7] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0 or subdictCSV.values()[7] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0 and subdictCSV.values()[7] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) not in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict(
                    (k, identifiersSQL_dict[k]) for k in (k, k - 41, k + 39, k - 40, k + 40, k - 39, k + 1, k + 41))
                subdictCSV = dict(
                    (k, identifiersCSV_dict[k]) for k in (k, k - 41, k + 39, k - 40, k + 40, k - 39, k + 1, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0 or subdictCSV.values()[7] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0 and subdictCSV.values()[7] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0 or subdictCSV.values()[7] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0 and subdictCSV.values()[7] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict(
                    (k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 1, k + 39, k - 40, k + 40, k + 1, k + 41))
                subdictCSV = dict(
                    (k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 1, k + 39, k - 40, k + 40, k + 1, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0 or subdictCSV.values()[7] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0 and subdictCSV.values()[7] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0 or subdictCSV.values()[7] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0 and subdictCSV.values()[7] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) not in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) not in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) not in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict((k, identifiersSQL_dict[k]) for k in (k, k - 1, k + 39, k + 40, k + 41))
                subdictCSV = dict((k, identifiersCSV_dict[k]) for k in (k, k - 1, k + 39, k + 40, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0):
                    falsePositive = falsePositive + 1

            if (k - 1) in identifiersSQL_dict.keys() and (k + 39) in identifiersSQL_dict.keys() and (
                    k + 1) in identifiersSQL_dict.keys() and (k + 40) in identifiersSQL_dict.keys() and (
                    k - 41) in identifiersSQL_dict.keys() and k - 40 not in identifiersSQL_dict.keys() and (
                    k - 39) in identifiersSQL_dict.keys() and (k + 41) in identifiersSQL_dict.keys():
                subdictSQL = dict(
                    (k, identifiersSQL_dict[k]) for k in (k, k - 41, k - 1, k + 39, k + 40, k - 39, k + 1, k + 41))
                subdictCSV = dict(
                    (k, identifiersCSV_dict[k]) for k in (k, k - 41, k - 1, k + 39, k + 40, k - 39, k + 1, k + 41))
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0 or subdictCSV.values()[7] != 0):
                    truePositive = truePositive + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0 and subdictCSV.values()[7] == 0):
                    trueNegative = trueNegative + 1
                if (subdictSQL.values()[0] == 0 and subdictCSV.values()[0] != 0 or subdictCSV.values()[1] != 0 or
                        subdictCSV.values()[2] != 0 or subdictCSV.values()[3] != 0 or subdictCSV.values()[4] != 0 or
                        subdictCSV.values()[5] != 0 or subdictCSV.values()[6] != 0 or subdictCSV.values()[7] != 0):
                    falseNegative = falseNegative + 1
                if (subdictSQL.values()[0] != 0 and subdictCSV.values()[0] == 0 and subdictCSV.values()[1] == 0 and
                        subdictCSV.values()[2] == 0 and subdictCSV.values()[3] == 0 and subdictCSV.values()[4] == 0 and
                        subdictCSV.values()[5] == 0 and subdictCSV.values()[6] == 0 and subdictCSV.values()[7] == 0):
                    falsePositive = falsePositive + 1

        return (truePositive, trueNegative, falsePositive, falseNegative, total)

    def precisionCalculation(self, truePositive, falsePositive):

        if ((falsePositive + truePositive) != 0):
            return (float(truePositive) / (falsePositive + truePositive))

    def recallCalculation(self, truePositive, falseNegative):

        if ((truePositive + falseNegative) != 0):
            return (float(truePositive) / (truePositive + falseNegative))

    def accuracyCalculation(self, truePositive, trueNegative, total):
        if (float(total) != 0):
            return ((truePositive + trueNegative) / float(total))

    def f1Calculation(self, precision, recall):
        if ((precision + recall) != 0):
            return (2 * ((precision * recall) / (precision + recall)))
