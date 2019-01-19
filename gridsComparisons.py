import mysql.connector
import numpy as np
import re
from scipy.sparse import coo_matrix

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
    query = "SELECT latitude,longitude from flickr_adder"
    mycursor1.execute(query)
    flickr_result = mycursor1.fetchall()
    for coord in flickr_result:
        latitude = float(coord[0])
        longitude = float(coord[1])
        flickrCoord.append([latitude,longitude])
    return flickrCoord

#get the coordiantes for all the records of nbn for a species
def getNBNCoordinates(mycursor1):
    nbnCoord = []
    query = "SELECT latitude,longitude from nbn_adder"
    mycursor1.execute(query)
    nbn_result = mycursor1.fetchall()
    for coord in nbn_result:
        latitude = float(coord[0])
        longitude = float(coord[1])
        nbnCoord.append([latitude,longitude])

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
def getFlickrCells(getCellLat, getCellLon,i,flickrCoord):

    for f_coord in flickrCoord:
        f_lat = f_coord[0]
        f_lon = f_coord[1]

        if getCellLat[1] <= f_lat <= getCellLat[0] and getCellLon[0] <= f_lon <= getCellLon[3]:
            print "------------------FLICKR SUCCESS-----------------------"
            print i

            break
        else:
            print "----------------------FLICKR FAIL------------------------------"
            print i

# check whether there are any nbn occurences in a given cell
def getNBNCells(getCellLat, getCellLon,i,nbnCoord):
    for n_coord in nbnCoord:
        n_lat = n_coord[0]
        n_lon = n_coord[1]

        if getCellLat[1] <= n_lat <= getCellLat[0] and getCellLon[0] <= n_lon <= getCellLon[3]:
            print "------------------NBN SUCCESS-----------------------"
            print i
        else:
            print "----------------------NBNFAIL------------------------------"
            print i

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

    columnNum = numOfCells(5)

    # create the grid
    lonArray, latArray, lowLat, rowNum = createGrid(columnNum, lowLat, highLat, leftLon, rightLon)
    print "lonArray: ",lonArray
    print "latArray: ",latArray
    print "lowLat: ",lowLat
    print "rowNum: ",rowNum
    print "columnNum: ",columnNum

    #for each cell, get its coordinates, check if there are any flickr or nbn occcurences in this cell
    for i in range(0, (rowNum * columnNum) - 1):
        getCellLat, getCellLon = getCellByID(latArray, lonArray, i, rowNum)
        getFlickrCells(getCellLat, getCellLon,i,flickrCoord)
        getNBNCells(getCellLat, getCellLon, i, nbnCoord)














if __name__ == '__main__':
    main()