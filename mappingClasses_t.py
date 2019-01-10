import re


class gridFunctions(object):
    # Four corners of the map / grid
    lowLat = 49.00
    highLat = 61.00
    leftLon = -11.50
    rightLon = 2.00

    # cell size - min *7, *10, *14, *28, *70, max *700
    noKM = 5

    def numOfCells(noKM):
        sizeOfMap = 800
        noCells = abs(sizeOfMap / noKM)

        return noCells

    columnNum = numOfCells(noKM)

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

    def getCSVCount(self, species, cursor):
        species = "'" + species + "'"
        query = "SELECT Count(id) FROM nbn_adder WHERE common_name = " + species + ";"
        cursor.execute(query)
        sqlCount = str(cursor.fetchone())
        sqlCount = re.search(r'\d+', sqlCount)
        sqlCount = sqlCount.group()
        return (sqlCount)

    def getSQLCount(self, species, cursor):
        species = "'" + species + "'"
        query = "SELECT Count(id) FROM flickr_adder WHERE common_name = " + species + ";"
        cursor.execute(query)
        sqlCount = str(cursor.fetchone())
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

    def getCellPhotoCountSQL(self, species, getCellLon, getCellLat, year, monthrange, cursor):
        species = "'" + species + "'"
        query = "SELECT id,date_time FROM flickr_adder where common_name = " + species + " AND longitude >= " + str(
            getCellLon[0]) + " and longitude <=" + str(getCellLon[3]) + " and latitude <= " + str(
            getCellLat[0]) + " and latitude >=" + str(getCellLat[1]) + ";"
        cursor.execute(query)
        rows = cursor.fetchall()
        count = 0
        for row in rows:
            id_sql = row[0]
            date_time = row[1].split("/")
            year_sql = int(date_time[0])
            month = int(date_time[1])
            if (year_sql == year and month in monthrange):
                # print year_sql,month
                count = count + 1
            # print str(count)
        # count = str(cursor.fetchone())
        # count = re.search(r'\d+' , count)
        # count = count.group()

        return count

    def getCellPhotoCountCSV(self, species, getCellLon, getCellLat, year, monthrange, cursor):
        species = "'" + species + "'"
        query = "SELECT id,year,month FROM  nbn_adder where common_name = " + species + " AND longitude >= " + str(
            getCellLon[0]) + " and longitude <=" + str(getCellLon[3]) + " and latitude <= " + str(
            getCellLat[0]) + " and latitude >=" + str(getCellLat[1]) + ";"
        cursor.execute(query)
        rows = cursor.fetchall()
        count = 0
        for row in rows:
            id_csv = row[0]
            year_csv = int(row[1])
            month = int(row[2])
            if (year_csv == year and month in monthrange):
                # print year_csv,month
                count = count + 1
            # print str(count)
        # count = str(cursor.fetchone())
        # count = re.search(r'\d+' , count)
        # count = count.group()
        return count


class mathComparisons(object):

    def confusionMatrix(self, sqlCountArray, csvCountArray):

        # http://www.dataschool.io/simple-guide-to-confusion-matrix-terminology/
        total = len(sqlCountArray)

        truePositive = 0
        trueNegative = 0
        falsePositive = 0
        falseNegative = 0

        for i in range(0, total):

            if (csvCountArray[i] != 0 and sqlCountArray[i] != 0):
                truePositive = truePositive + 1

            if (csvCountArray[i] == 0 and sqlCountArray[i] == 0):
                trueNegative = trueNegative + 1

            if (csvCountArray[i] != 0 and sqlCountArray[i] == 0):
                falseNegative = falseNegative + 1

            if (csvCountArray[i] == 0 and sqlCountArray[i] != 0):
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