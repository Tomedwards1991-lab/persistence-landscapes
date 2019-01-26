import mysql.connector
import re
import os



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

def removeDsStore(directory):
    if os.path.exists(directory + "/.DS_Store"):
        os.remove(directory + "/.DS_Store")

def getVerifiedFlickr(common_name):
    verified_ids_list = []
    removeDsStore('Flickr_Images')
    for common_name in os.listdir('Flickr_Images'):
        for image in os.listdir('Flickr_Images/' +common_name):
            if image.endswith("_bird.jpg") or image.endswith("_fn.jpg"):
                #print "image: ",image
                verified_id = image.replace("_bird.jpg","").replace("_fn.jpg", "")
                verified_ids_list.append(verified_id)

    verified_ids = str(verified_ids_list).replace("[","(").replace("]",")")
    return verified_ids


#get the number of records for a specific species on flickr
def getCountFlickr(mycursor,verified_ids,common_name):
    query = 'SELECT Count(id) FROM flickr_data where common_name = "'+common_name+'"and id in '+verified_ids+';'
    mycursor.execute(query)
    flickrCount = str(mycursor.fetchone())
    flickrCount = re.search(r'\d+', flickrCount)
    flickrCount = flickrCount.group()
    return int(flickrCount)

#get the number of records for a specific species on nbn
def getCountNBN(mycursor,common_name):
    query = "SELECT Count(id) FROM nbn_data where common_name = '"+common_name+"';"
    mycursor.execute(query)
    nbnCount = str(mycursor.fetchone())
    nbnCount = re.search(r'\d+', nbnCount)
    nbnCount = nbnCount.group()
    return int(nbnCount)

#get the coordiantes for all the records of flickr for a species
def getFlickrCoordinates(mycursor1,verified_ids,common_name):
    flickrCoord = []
    query = 'SELECT latitude,longitude from flickr_data where common_name = "'+common_name+'" and id in '+verified_ids+';'
    mycursor1.execute(query)
    flickr_result = mycursor1.fetchall()
    for coord in flickr_result:
        latitude = float(coord[0])
        longitude = float(coord[1])
        flickrCoord.append([latitude,longitude])
    return flickrCoord

#get the coordiantes for all the records of nbn for a species
def getNBNCoordinates(mycursor1,common_name):
    nbnCoord = []
    query = "SELECT latitude,longitude from nbn_data where common_name = '"+common_name+"';"
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
    #print "square_id: ",squareID
    getCellLat = []
    getCellLat.append(gridLatArray[squareID])
    #print "first getCellLat: ",getCellLat
    getCellLat.append(gridLatArray[squareID + 1])
    #print "second getCellLat: ", getCellLat
    getCellLat.append(gridLatArray[squareID + rowNum + 1])
    #print "third getCellLat: ", getCellLat
    getCellLat.append(gridLatArray[squareID + rowNum])
    #print "forth getCellLat: ", getCellLat
    getCellLat.append(gridLatArray[squareID])

    getCellLon = []
    getCellLon.append(gridLonArray[squareID])
    #print "first getCellLon: ",getCellLon
    getCellLon.append(gridLonArray[squareID + 1])
    #print "second getCellLon: ", getCellLon
    getCellLon.append(gridLonArray[squareID + rowNum + 1])
    #print "third getCellLon: ", getCellLon
    getCellLon.append(gridLonArray[squareID + rowNum])
    #print "forth getCellLon: ", getCellLon
    getCellLon.append(gridLonArray[squareID])

    return getCellLat, getCellLon

# check whether there are any flickr occurences in a given cell
def getFlickrCells(getCellLat, getCellLon,i,flickrCoord,flickr_result):

    for f_coord in flickrCoord:
        f_lat = f_coord[0]
        f_lon = f_coord[1]

        if getCellLat[1] <= f_lat <= getCellLat[0] and getCellLon[0] <= f_lon <= getCellLon[3]:
            if not i in flickr_result:
                flickr_result.append(i)



# check whether there are any nbn occurences in a given cell
def getNBNCells(getCellLat, getCellLon,i,nbnCoord,nbn_result):
    for n_coord in nbnCoord:
        n_lat = n_coord[0]
        n_lon = n_coord[1]

        if getCellLat[1] <= n_lat <= getCellLat[0] and getCellLon[0] <= n_lon <= getCellLon[3]:
            if not i in nbn_result:
                nbn_result.append(i)



def confusionMatrix(flickr_extended, nbn_extended):

    total = len(flickr_extended)

    truePositive = 0
    trueNegative = 0
    falsePositive = 0
    falseNegative = 0

    for i in range(0, total):
        if (nbn_extended[i][1] != 0 and flickr_extended[i][1] != 0):
            truePositive = truePositive + 1

        if (nbn_extended[i][1] == 0 and flickr_extended[i][1] == 0):
            trueNegative = trueNegative + 1

        if (nbn_extended[i][1] != 0 and flickr_extended[i][1] == 0):
            falseNegative = falseNegative + 1

        if (nbn_extended[i][1] == 0 and flickr_extended[i][1] != 0):
            falsePositive = falsePositive + 1

    return (truePositive, trueNegative, falsePositive, falseNegative, total)

def main():
    names = ['Blue Tit','Continental Robin','Woodpigeon','Dunnock','Great Tit','Chaffinch','House Sparrow','Collared Dove','Greenfinch']
    for common_name in names:

        verified_ids = getVerifiedFlickr(common_name)

        mydb, mycursor = dbConnection()
        flickrCount = getCountFlickr(mycursor,verified_ids,common_name)
        nbnCount = getCountNBN(mycursor,common_name)
        finish(mydb, mycursor)

        mydb1, mycursor1 = dbConnection()
        flickrCoord = getFlickrCoordinates(mycursor1,verified_ids,common_name)
        nbnCoord = getNBNCoordinates(mycursor1,common_name)
        finish(mydb1, mycursor1)


        # set up the coordinates for the grid
        lowLat = 49.00
        highLat = 61.00
        leftLon = -11.50
        rightLon = 2.00

        cells = [5,10,15,20,25,30,35,40,45,50,55,60]

        for c in cells:
            print "cell size: ",c
            columnNum = numOfCells(c)

            # create the grid
            lonArray, latArray, lowLat, rowNum = createGrid(columnNum, lowLat, highLat, leftLon, rightLon)
            #print "lonArray: ",lonArray
            #print "latArray: ",latArray
            print "lowLat: ",lowLat
            rowNum = rowNum - 1
            print "rowNum: ",rowNum
            columnNum = columnNum-1
            print "columnNum: ", columnNum

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
            truePositive, trueNegative, falsePositive, falseNegative, total = confusionMatrix(flickr_extended, nbn_extended)
            print "tp: ",truePositive
            print "tn: ",trueNegative
            print "fp: ",falsePositive
            print "fn: ",falseNegative
            print "total: ",total
            precision = float(truePositive) / (falsePositive + truePositive)
            recall = float(truePositive) / (truePositive + falseNegative)
            accuracy = (truePositive + trueNegative) / float(total)
            f1 = 2 * ((precision * recall) / (precision + recall))
            print "precision: ", precision
            print "recall: ", recall
            print "accuracy: ", accuracy
            print "f1 measure: ", f1

            newline = str(common_name)+"," + str(nbnCount) + "," + str(flickrCount) + ",800,"+str(c)+"," + str(truePositive) + "," + str(trueNegative) + "," + str(falsePositive) + "," + str(falseNegative) + "," + str(precision) + "," + str(recall) + "," + str(f1) + "," + str(accuracy)
            with open('/Users/thomasedwards/Desktop/paper_update_report_02_01_18/output_all_spatial_1x1.csv', 'a') as f:
                f.write(newline + '\n')
                newline = ""

if __name__ == '__main__':
    main()