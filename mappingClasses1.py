import re



# counts occurences of both NBN and Flickr within each cell of a grid
# then looks whether there are occurences of both Flickr and NBN within each cell
# in order to adjust code to work for ajucent cells
# we need to find the ids of the adjusent cells and change the code for confusion matrix
class gridFunctions(object):

    # Four corners of the map / grid
    lowLat = 49.00
    highLat = 61.00
    leftLon = -11.50
    rightLon = 2.00

    # cell size - min *7, *10, *14, *28, *70, max *700
    noKm = 5

    def numOfCells(noKm):
        sizeOfMap = 800
        noCells = abs(sizeOfMap / noKm)

        return noCells

    columnNum = numOfCells(noKm)

    # Creates an array of longitude and an array of latitude values which when plotted will display a grid
    # The size of the cells are updated by increasing/decreasing the columnNum value
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

    # takes a latitude and longitude array which contains the coordiantes of a cell
    # calculate the exact centre of the cell
    # return the longitude/latitude coordinates
    # used to display a count number or marker in the centre of a cell

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

    # input the id of a cell
    # search the grid and return the coordinates of the cell in an latitude array and a longitude array
    # used to get the four corners of a cell:
    # top left corner which is equal to the ID parameter,
    # the bottom left is ID + 1,
    # the top right is ID + total number of rows,
    # the bottom right is ID + total numbers of rows + 1
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

    # takes a lat and lon array which contain the coordiantes of a cell
    # calcualtes the exact center of a cell
    # determine how many Flickr records for a specific species are found within the cells bounding box
    def getCellPhotoCountSQL(self, getCellLon, getCellLat, cur):
        query = "SELECT Count(id) FROM flickr_data WHERE longitude >= " + str(
            getCellLon[0]) + " and longitude <=" + str(getCellLon[3]) + " and latitude >= " + str(
            getCellLat[1]) + " and latitude <=" + str(getCellLat[0])
        cur.execute(query)
        count = str(cur.fetchone())
        count = re.search(r'\d+', count)
        count = count.group()
        return count

    # Takes a latitude and longitude array which contain the coordinates of a cell
    # determine how many CSV records for a specific species are found within the cells bounding box
    def getCellPhotoCountCSV(self, getCellLon, getCellLat, cur):

        query = "SELECT Count(id) FROM nbn_data WHERE longitude >= " + str(getCellLon[0]) + " and longitude <=" + str(
            getCellLon[3]) + " and latitude >= " + str(getCellLat[1]) + " and latitude <=" + str(
            getCellLat[0])
        cur.execute(query)
        count = str(cur.fetchone())
        count = re.search(r'\d+', count)
        count = count.group()
        return count


class mathComparisons(object):

    def confusionMatrix(self, flickrCountArray, nbnCountArray):

        # http://www.dataschool.io/simple-guide-to-confusion-matrix-terminology/
        total = len(flickrCountArray)

        truePositive = 0
        trueNegative = 0
        falsePositive = 0
        falseNegative = 0

        for i in range(0, total):
            if (nbnCountArray[i] != 0 and flickrCountArray[i] != 0):
                truePositive = truePositive + 1

            if (nbnCountArray[i] == 0 and flickrCountArray[i] == 0):
                trueNegative = trueNegative + 1

            if (nbnCountArray[i] != 0 and flickrCountArray[i] == 0):
                falseNegative = falseNegative + 1

            if (nbnCountArray[i] == 0 and flickrCountArray[i] != 0):
                falsePositive = falsePositive + 1

        return (truePositive, trueNegative, falsePositive, falseNegative, total)

    def precisionCalculation(self, truePositive, falsePositive):

        return (float(truePositive) / (falsePositive + truePositive))

    def recallCalculation(self, truePositive, falseNegative):

        return (float(truePositive) / (truePositive + falseNegative))

    def accuracyCalculation(self, truePositive, trueNegative, total):

        return ((truePositive + trueNegative) / float(total))

    def f1Calculation(self, precision, recall):

        return (2 * ((precision * recall) / (precision + recall)))