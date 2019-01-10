import mappingClasses
import numpy as np
import math
import os
import panda as pd
import csv
import collections
from dbConnection import *

gridmap = mappingClasses.gridFunctions()
mathcomp = mappingClasses.mathComparisons()

# speciesArray = ['Black-Headed Gull','Bullfinch','Long-Tailed Tit','Coal Tit', 'Sparrowhawk','Moorhen','Goldfinch']
speciesArray = ['Adder']
gridLonArray, gridLatArray, lowLat, rowNum = gridmap.createGrid(gridmap.columnNum, gridmap.lowLat, gridmap.highLat,
                                                                gridmap.leftLon, gridmap.rightLon)

'''
speciesArray = []
namesNBNcount = collections.Counter()
csvNBNfile = 'nbn_data_unique.csv'
with open(csvNBNfile, 'r') as csvNBN:
	for row in csv.reader(csvNBN):
		if row[0] != "Burdock":
			namesNBNcount[row[0]] += 1


namesFlickrcount = collections.Counter()
csvFlickrfile = 'flickr_data_unique.csv'
with open(csvFlickrfile, 'r') as csvFlickr:
	for row in csv.reader(csvFlickr):
		if row[0] != "Burdock":
			namesFlickrcount[row[0]] += 1

for key, value in namesNBNcount.items():
	for keyF, valueF in namesFlickrcount.items():
		if key == keyF and value > 100 and valueF > 100:
			speciesArray.append(key)



select di.common_name, nd.id, nd.latitude, nd.longitude, nd.year, nd.month
from dictionary di, nbn_data nd
where di.other_names = nd.common_name
'''

# Loop through each species in the array
for j in range(0, len(speciesArray)):

    species = speciesArray[j]
    print species

    totalCSVCount = gridmap.getCSVCount(cursor)
    totalSQLCount = gridmap.getSQLCount(cursor)
    sqlCountArray = []
    csvCountArray = []
    writeComparisons = []
    keysList = []
    # loop through the cells getting the counts for SQL and CSV and normalising the data ot be sotred in a probability distributions for similarity calculations
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

        else:
            keysList.append(i)
            # print i
            getCellLon, getCellLat = gridmap.getCellByID(gridLatArray, gridLonArray, i, rowNum)
            print "getCellLon: ", getCellLon
            print "getCellLat: ", getCellLat
            sqlCellCount = gridmap.getCellPhotoCountSQL(getCellLon, getCellLat,cursor)
            csvCellCount = gridmap.getCellPhotoCountCSV(getCellLon, getCellLat,cursor)

            sqlCellCount = (int(sqlCellCount) / float(totalSQLCount)) * 100
            sqlCellCount = round(sqlCellCount * 2) / 2

            csvCellCount = (int(csvCellCount) / float(totalCSVCount)) * 100
            csvCellCount = round(csvCellCount * 2) / 2

            sqlCountArray.append(sqlCellCount)
            csvCountArray.append(csvCellCount)

    # Calcualte each of the similarity results
    # print keysList

    truePositive, trueNegative, falsePositive, falseNegative, total = mathcomp.confusionMatrix(sqlCountArray,
                                                                                               csvCountArray, keysList)

    precision = mathcomp.precisionCalculation(truePositive, falsePositive)
    recall = mathcomp.recallCalculation(truePositive, falseNegative)
    f1 = mathcomp.f1Calculation(precision, recall)
    accuracy = mathcomp.accuracyCalculation(truePositive, trueNegative, total)
    print precision
    print recall
    print f1
    print accuracy

    newline = str(species) + "," + str(totalCSVCount) + "," + str(totalSQLCount) + " ,5 km," + str(
        truePositive) + "," + str(trueNegative) + "," + str(falsePositive) + "," + str(falseNegative) + "," + str(
        precision * 100) + "," + str(recall * 100) + "," + str(f1 * 100) + "," + str(accuracy * 100)
    with open('/Users/thomasedwards/Desktop/paper_update_report_02_01_18/output_Adder_verified3x3.csv', 'a') as f:
        f.write(newline + '\n')
        newline = ""