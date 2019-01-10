import mappingClasses_t
import numpy as np
import math
import os
import panda as pd
import csv
from dbConnection import *

gridmap = mappingClasses_t.gridFunctions()
mathcomp = mappingClasses_t.mathComparisons()

gridLonArray, gridLatArray, lowLat, rowNum = gridmap.createGrid(gridmap.columnNum, gridmap.lowLat, gridmap.highLat,
                                                                gridmap.leftLon, gridmap.rightLon)

# speciesArray = ["Magpie","Common Swift","Nuthatch","Black-Headed Gull", "Bullfinch","Long-Tailed Tit","Coal Tit","Sparrowhawk","Moorhen","Goldfinch"]
speciesArray = ["Adder"]
# Loop through each species in the array
yearList = [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]
monthList = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]
for j in range(0, len(speciesArray)):
    species = speciesArray[j]

    totalCSVCount = gridmap.getCSVCount(species, cursor)
    totalSQLCount = gridmap.getSQLCount(species, cursor)
    flickrCountArray = []
    nbnCountArray = []
    print totalCSVCount, totalSQLCount

    # loop through the cells getting the counts for SQL and CSV and normalising the data ot be sotred in a probability distributions for similarity calculations
    # loop through the cells getting the counts for SQL and CSV and normalising the data ot be sotred in a probability distributions for similarity calculations
    # i is squareID

    for i in range(0, (rowNum * gridmap.columnNum) - 1):
        # avoid all cells that are no in the UK
        # avoid all cells that are no in the UK
        if (i <= 209 or (i >= 211 and i <= 249) or (i >= 252 and i <= 259) or (i >= 263 and i <= 287) or (
                i >= 303 and i <= 327) or (i >= 343 and i <= 365) or (i >= 383 and i <= 394) or (i >= 397 and i <= 404)
                or (i >= 423 and i <= 433) or (i >= 436 and i <= 446) or (i >= 462 and i <= 467) or (
                        i >= 476 and i <= 485) or (i >= 516 and i <= 525) or (i >= 556 and i <= 564) or (
                        i >= 596 and i <= 604)
                or (i >= 635 and i <= 643) or (i == 715) or (i >= 719 and i <= 720) or (i >= 725 and i <= 729) or (
                        i >= 732 and i <= 735) or (i >= 754 and i <= 759) or (i >= 764 and i <= 778) or (
                        i >= 794 and i <= 819) or
                (i >= 834 and i <= 861) or (i >= 874 and i <= 903) or (i >= 914 and i <= 944) or (
                        i >= 953 and i <= 985) or (i >= 990 and i <= 1000) or (i >= 294 and i <= 297) or (
                        i >= 335 and i <= 337) or (i >= 694 and i <= 695)
                or (i == 680) or (i >= 685 and i <= 689) or (i >= 648 and i <= 649) or (i == 503) or (i == 543) or (
                        i == 583)):
            i = i

        else:
            for y in range(0, len(yearList)):
                for m in range(0, len(monthList)):
                    year = yearList[y]
                    monthrange = monthList[m]
                    print year, monthrange
                    getCellLon, getCellLat = gridmap.getCellByID(gridLatArray, gridLonArray, i, rowNum)
                    print "getCellLon", getCellLon
                    print "getCellLat", getCellLat

                    flickrCellCount = gridmap.getCellPhotoCountSQL(species, getCellLon, getCellLat, year, monthrange,cursor)
                    nbnCellCount = gridmap.getCellPhotoCountCSV(species, getCellLon, getCellLat, year, monthrange,cursor)
                    print flickrCellCount
                    print nbnCellCount

                    flickrCellCount = (int(flickrCellCount) / float(totalSQLCount)) * 100
                    flickrCellCount = round(flickrCellCount * 2) / 2

                    nbnCellCount = (int(nbnCellCount) / float(totalCSVCount)) * 100
                    nbnCellCount = round(nbnCellCount * 2) / 2

                    flickrCountArray.append(flickrCellCount)
                    nbnCountArray.append(nbnCellCount)

                    print "flickrCountArray", flickrCountArray
                    print "nbnCountArray", nbnCountArray

    # Calculate each of the similarity results
    truePositive, trueNegative, falsePositive, falseNegative, total = mathcomp.confusionMatrix(flickrCountArray,nbnCountArray)

    precision = mathcomp.precisionCalculation(truePositive, falsePositive)
    print "precision:",precision
    recall = mathcomp.recallCalculation(truePositive, falseNegative)
    print "recall:",recall
    f1 = mathcomp.f1Calculation(precision, recall)
    print "f1:",f1
    accuracy = mathcomp.accuracyCalculation(truePositive, trueNegative, total)
    print accuracy

    newline = str(species) + "," + str(totalCSVCount) + "," + str(totalSQLCount) + " ,5 km," + str(precision) + "," + str(recall) + "," + str(f1) + "," + str(accuracy)
    with open('/Users/thomasedwards/Desktop/paper_update_report_02_01_18/comparisonsTemporal_1_Adder.csv', 'a') as f:
        f.write(newline + '\n')
        newline = ""