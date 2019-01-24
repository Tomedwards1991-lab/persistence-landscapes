import mysql.connector
import re



#database connection
def dbConnection():
    mydb = mysql.connector.connect(
        host="csmysql.cs.cf.ac.uk",
        user="c1114882",
        passwd="thom9055",
        database="c1114882"
    )

    mycursor = mydb.cursor()
    mydb.autocommit = True

    return mydb,mycursor

#close database connecton
def finish(mydb,mycursor):
    mycursor.close()
    mydb.close()

#get the number of records for a specific species on flickr
def getCountFlickr(mycursor):
    query = "SELECT Count(id) FROM flickr_adder"
    mycursor.execute(query)
    flickrCount = str(mycursor.fetchone())
    flickrCount = re.search(r'\d+', flickrCount)
    flickrCount = flickrCount.group()
    return int(flickrCount)

#get the number of records for a specific species on nbn
def getCountNBN(mycursor):
    query = "SELECT Count(id) FROM nbn_adder"
    mycursor.execute(query)
    nbnCount = str(mycursor.fetchone())
    nbnCount = re.search(r'\d+', nbnCount)
    nbnCount = nbnCount.group()
    return int(nbnCount)

#get the coordiantes for all the records of flickr for a species
def getFlickrCoordinates(mycursor1):
    flickrCoord = []
    query = "SELECT latitude,longitude,date_time from flickr_adder"
    mycursor1.execute(query)
    flickr_result = mycursor1.fetchall()
    year = 0
    month = 0
    for coord in flickr_result:
        latitude = float(coord[0])
        longitude = float(coord[1])
        date_time = str(coord[2])
        date_time = date_time.split(" ")
        if "/" in date_time[0]:
            date_time[0] = date_time[0].split("/")
            month = int(date_time[0][1])

        if "-" in date_time[0]:
            date_time[0] = date_time[0].split("-")
            month = int(date_time[0][1])

        flickrCoord.append([latitude,longitude,month])
    return flickrCoord

#get the coordiantes for all the records of nbn for a species
def getNBNCoordinates(mycursor1):
    nbnCoord = []
    query = "SELECT latitude,longitude,year,month from nbn_adder"
    mycursor1.execute(query)
    nbn_result = mycursor1.fetchall()
    for coord in nbn_result:
        latitude = float(coord[0])
        longitude = float(coord[1])
        year = int(coord[2])
        month = int(coord[3])
        nbnCoord.append([latitude,longitude,month])

    return nbnCoord

#calucalte the number of cells for a given grid size
def numOfCells(noKm):
    sizeOfMap = 800
    noCells = abs(sizeOfMap / noKm)

    return noCells

# create the grid
def createGrid(columnNum, lowLat, highLat, leftLon, rightLon):
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

# get the id and the coordiantes for each corner of each cell of the grid
def getCellByID(gridLatArray, gridLonArray, squareID, rowNum):
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

    return getCellLat, getCellLon

# check whether there are any flickr occurences in a given cell
def getFlickrCells(getCellLat, getCellLon,i,flickrCoord,flickr_result):
    monthList = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]
    for f_coord in flickrCoord:
        f_lat = f_coord[0]
        f_lon = f_coord[1]
        month = f_coord[2]

        if getCellLat[1] <= f_lat <= getCellLat[0] and getCellLon[0] <= f_lon <= getCellLon[3]:
            if month in monthList[0]:
                flickr_result.append([i, 1, 1])
            if month in monthList[1]:
                flickr_result.append([i, 2, 1])
            if month in monthList[2]:
                flickr_result.append([i, 3, 1])
        else:
            if month in monthList[0]:
                flickr_result.append([i, 1, 0])
            if month in monthList[1]:
                flickr_result.append([i, 2, 0])
            if month in monthList[2]:
                flickr_result.append([i, 3, 0])



# check whether there are any nbn occurences in a given cell
def getNBNCells(getCellLat, getCellLon,i,nbnCoord,nbn_result):
    for n_coord in nbnCoord:
        n_lat = n_coord[0]
        n_lon = n_coord[1]

        if getCellLat[1] <= n_lat <= getCellLat[0] and getCellLon[0] <= n_lon <= getCellLon[3]:
            if not i in nbn_result:
                nbn_result.append(i)



def confusionMatrix(flickr_extended, nbn_extended,columnNum):

    #adjust = [rowNum*columnNum-2,rowNum*columnNum-1,rowNum*columnNum]
    #all_banned = first_row_ids+last_row_ids+first_col_ids+last_col_ids+adjust


    total = len(flickr_extended)

    truePositive = 0
    trueNegative = 0
    falsePositive = 0
    falseNegative = 0


    for i in range(0, total):

        if (i-columnNum-1) < total and (i-1) < total and (i+columnNum-1) < total and (i+columnNum) < total and (i-columnNum) < total and (i-columnNum+1) < total and (i+columnNum+1) < total:
            print flickr_extended[i][0]
            print nbn_extended[i-columnNum-1][1]
            print nbn_extended[i-1][1]
            print nbn_extended[i][1]
            print nbn_extended[i+columnNum-1][1]
            print nbn_extended[i+columnNum][1]
            print nbn_extended[i-columnNum][1]
            print nbn_extended[i-columnNum+1][1]
            print nbn_extended[i+1][1]
            print nbn_extended[i+columnNum+1][1]


            if (flickr_extended[i][1] != 0 and nbn_extended[i][1] != 0 or nbn_extended[i-columnNum-1][1] !=0 or
                nbn_extended[i-1][1] != 0 or nbn_extended[i+columnNum-1][1] != 0 or nbn_extended[i+columnNum][1] !=0 or
                nbn_extended[i-columnNum][1] != 0 or nbn_extended[i-columnNum+1][1] != 0 or nbn_extended[i+1][1] !=0 or
                nbn_extended[i + columnNum + 1][1] != 0):

                truePositive = truePositive + 1

            if (flickr_extended[i][1] == 0 and nbn_extended[i][1] == 0 and nbn_extended[i-columnNum-1][1] == 0 and
                nbn_extended[i-1][1] == 0 and nbn_extended[i+columnNum-1][1] == 0 and nbn_extended[i+columnNum][1] == 0 and
                nbn_extended[i-columnNum][1] == 0 and nbn_extended[i-columnNum+1][1] == 0 and nbn_extended[i+1][1] == 0 and
                nbn_extended[i + columnNum + 1][1] == 0):
                trueNegative = trueNegative + 1

            if (flickr_extended[i][1] == 0 and nbn_extended[i][1] != 0 or nbn_extended[i-columnNum-1][1] !=0 or
                nbn_extended[i-1][1] != 0 or nbn_extended[i+columnNum-1][1] != 0 or nbn_extended[i+columnNum][1] !=0 or
                nbn_extended[i-columnNum][1] != 0 or nbn_extended[i-columnNum+1][1] != 0 or nbn_extended[i+1][1] !=0 or
                nbn_extended[i + columnNum + 1][1] != 0):
                falseNegative = falseNegative + 1

            if (flickr_extended[i][1] != 0 and nbn_extended[i][1] == 0 and nbn_extended[i-columnNum-1][1] == 0 and
                nbn_extended[i-1][1] == 0 and nbn_extended[i+columnNum-1][1] == 0 and nbn_extended[i+columnNum][1] == 0 and
                nbn_extended[i-columnNum][1] == 0 and nbn_extended[i-columnNum+1][1] == 0 and nbn_extended[i+1][1] == 0 and
                nbn_extended[i + columnNum + 1][1] == 0):
                falsePositive = falsePositive + 1


    return (truePositive, trueNegative, falsePositive, falseNegative, total)


def main():
    mydb, mycursor = dbConnection()
    flickrCount = getCountFlickr(mycursor)
    nbnCount = getCountNBN(mycursor)
    finish(mydb, mycursor)

    mydb1, mycursor1 = dbConnection()
    flickrCoord = getFlickrCoordinates(mycursor1)
    nbnCoord = getNBNCoordinates(mycursor1)
    finish(mydb1, mycursor1)

    # set uo the coordinates for the grid
    lowLat = 49.00
    highLat = 61.00
    leftLon = -11.50
    rightLon = 2.00

    cells = [20,30,40,45]

    for c in cells:
        columnNum = numOfCells(c)


        # create the grid
        lonArray, latArray, lowLat, rowNum = createGrid(columnNum, lowLat, highLat, leftLon, rightLon)
        print "lonArray: ",lonArray
        print "latArray: ",latArray
        print "lowLat: ",lowLat
        rowNum = rowNum - 1
        print "rowNum: ",rowNum
        columnNum = columnNum - 1
        print "columnNum: ",columnNum
        print c
        flickr_extended = []
        nbn_extended = []
        all_ids = []
        flickr_result = []
        nbn_result = []
        #for each cell, get its coordinates, check if there are any flickr or nbn occcurences in this cell
        for i in range(0, (rowNum * columnNum)-1):
            getCellLat, getCellLon = getCellByID(latArray, lonArray, i, rowNum)
            getFlickrCells(getCellLat, getCellLon,i,flickrCoord,flickr_result)
            getNBNCells(getCellLat, getCellLon, i, nbnCoord,nbn_result)
            all_ids.append(i)



        first_row_ids = []
        last_row_ids = []
        first_col_ids = []
        last_col_ids = []
        for first_row in range(0,columnNum):
            first_row_ids.append(first_row)

        for last_row in range((rowNum * columnNum) - 18,(rowNum * columnNum) - 1):
            last_row_ids.append(last_row)

        for first_col in range(0,(rowNum * columnNum) - 15,columnNum):
            first_col_ids.append(first_col)

        for last_col in range(columnNum-1,(rowNum * columnNum),columnNum):
            last_col_ids.append(last_col)


        for res in all_ids:
            if res in flickr_result:
                flickr_extended.append([res,1])
            else:
                flickr_extended.append([res, 0])

        for res_1 in all_ids:
            if res_1 in nbn_result:
                nbn_extended.append([res_1,1])
            else:
                nbn_extended.append([res_1, 0])

        print "len flickr: ",len(flickr_extended)
        print "nbn len: ", len(nbn_extended)
        truePositive, trueNegative, falsePositive, falseNegative, total = confusionMatrix(flickr_extended, nbn_extended,columnNum)


        print "tp: ",truePositive
        print "tn: ",trueNegative
        print "fp: ",falsePositive
        print "fn: ",falseNegative



        precision = float(truePositive) / (falsePositive + truePositive)
        recall = float(truePositive) / (truePositive + falseNegative)
        accuracy = (truePositive + trueNegative) / float(total)
        f1 = 2 * ((precision * recall) / (precision + recall))
        print "precision: ", precision
        print "recall: ", recall
        print "accuracy: ", accuracy
        print "f1 measure: ", f1

        newline = "Adder," + str(nbnCount) + "," + str(flickrCount) + "," + str(c) + "," + str(truePositive) + "," + str(trueNegative) + "," + str(falsePositive) + "," + str(falseNegative) + "," + str(precision) + "," + str(recall) + "," + str(f1) + "," + str(accuracy)
        with open('/Users/thomasedwards/Desktop/paper_update_report_02_01_18/output_Adder_3x3.csv', 'a') as f:
            f.write(newline + '\n')
            newline = ""



if __name__ == '__main__':
    main()