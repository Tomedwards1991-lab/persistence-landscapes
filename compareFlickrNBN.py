import mappingClasses1
import numpy as np
import math
import os
import panda as pd
import csv
import collections
from dbConnection import *


gridmap = mappingClasses1.gridFunctions()
mathcomp = mappingClasses1.mathComparisons()

gridLonArray, gridLatArray, lowLat, rowNum = gridmap.createGrid(gridmap.columnNum, gridmap.lowLat, gridmap.highLat,gridmap.leftLon, gridmap.rightLon)

# speciesArray = ['Black-Headed Gull','Bullfinch','Long-Tailed Tit','Coal Tit', 'Sparrowhawk','Moorhen','Goldfinch']
speciesArray = ['Adder']
'''
namesNBNcount = collections.Counter()
csvNBNfile = 'nbn_data_unique_1.csv'
with open(csvNBNfile, 'r') as csvNBN:
	for row in csv.reader(csvNBN):
		if row[0] != "Burdock":
			namesNBNcount[row[0]] += 1


namesFlickrcount = collections.Counter()
csvFlickrfile = 'flickr_data_unique_1.csv'
with open(csvFlickrfile, 'r') as csvFlickr:
	for row in csv.reader(csvFlickr):
		if row[0] != "Burdock":
			namesFlickrcount[row[0]] += 1

for key, value in namesNBNcount.items():
	for keyF, valueF in namesFlickrcount.items():
		if key == keyF and value > 100 and valueF > 100:
			speciesArray.append(key)
'''
# Loop through each species in the array

for j in range(0, len(speciesArray)):

    species = speciesArray[j]
    print species

    totalCSVCount = gridmap.getCSVCount(species,cursor)
    totalSQLCount = gridmap.getSQLCount(species,cursor)
    flickrCountArray = []
    nbnCountArray = []
    print "nbn,flickr total counts: ", totalCSVCount, totalSQLCount

    # loop through the cells getting the counts for SQL and CSV and normalising the data ot be sotred in a probability distributions for similarity calculations
    # loop through the cells getting the counts for SQL and CSV and normalising the data ot be sotred in a probability distributions for similarity calculations
    # i is squareID
    count = 0
    for i in range(0, (rowNum * gridmap.columnNum) - 1):

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
            count = count + 1


        else:

            getCellLon, getCellLat = gridmap.getCellByID(gridLatArray, gridLonArray, i, rowNum)
            print "getCellLon", getCellLon
            print "getCellLat", getCellLat

            flickrCellCount = gridmap.getCellPhotoCountSQL(species, getCellLon, getCellLat,cursor)
            nbnCellCount = gridmap.getCellPhotoCountCSV(species, getCellLon, getCellLat,cursor)

            flickrCellCount = (int(flickrCellCount) / float(totalSQLCount)) * 100
            flickrCellCount = round(flickrCellCount * 2) / 2

            nbnCellCount = (int(nbnCellCount) / float(totalCSVCount)) * 100
            nbnCellCount = round(nbnCellCount * 2) / 2

            flickrCountArray.append(flickrCellCount)
            nbnCountArray.append(nbnCellCount)

    print "flickrCountArray", flickrCountArray
    print "nbnCountArray", nbnCountArray
    # Calculate each of the similarity results
    print len(flickrCountArray)
    print len(nbnCountArray)

    truePositive, trueNegative, falsePositive, falseNegative, total = mathcomp.confusionMatrix(nbnCountArray,flickrCountArray)
    print "truePositive", truePositive
    print "trueNegative", trueNegative
    print "falsePositive", falsePositive
    print "falseNegative", falseNegative
    print "total", total

    precision = mathcomp.precisionCalculation(truePositive, falsePositive)
    precision = precision * 100
    precision = round(precision, 2)
    print precision
    recall = mathcomp.recallCalculation(truePositive, falseNegative)
    recall = recall * 100
    recall = round(recall, 2)
    print recall
    f1 = mathcomp.f1Calculation(precision, recall)
    f1 = round(f1, 2)
    print f1
    accuracy = mathcomp.accuracyCalculation(truePositive, trueNegative, total)
    accuracy = accuracy*100
    accuracy = round(accuracy, 2)
    print accuracy


    newline = str(species) + "," + str(totalCSVCount) + "," + str(totalSQLCount) + " ,5 km," + str(
        truePositive) + "," + str(trueNegative) + "," + str(falsePositive) + "," + str(falseNegative) + "," + str(precision) + "," + str(recall) + "," + str(f1) + "," + str(accuracy)
    with open('/Users/thomasedwards/Desktop/paper_update_report_02_01_18/output_Adder.csv', 'a') as f:
        f.write(newline + '\n')
        newline = ""