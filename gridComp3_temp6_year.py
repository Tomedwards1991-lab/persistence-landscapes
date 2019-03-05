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
    query = 'SELECT Count(id) FROM flickr_data where common_name = "' + common_name + '"and id in ' + verified_ids + ';'
    mycursor.execute(query)
    flickrCount = str(mycursor.fetchone())
    flickrCount = re.search(r'\d+', flickrCount)
    flickrCount = flickrCount.group()
    return int(flickrCount)

#get the number of records for a specific species on nbn
def getCountNBN(mycursor,common_name):
    query = "SELECT Count(id) FROM nbn_data where common_name = '" + common_name + "'and year >= 2004;"
    mycursor.execute(query)
    nbnCount = str(mycursor.fetchone())
    nbnCount = re.search(r'\d+', nbnCount)
    nbnCount = nbnCount.group()
    return int(nbnCount)

#get the coordiantes for all the records of flickr for a species
def getFlickrCoordinates(mycursor1,verified_ids,common_name):
    flickrCoord = []
    query = 'SELECT latitude,longitude,date_time from flickr_data where common_name = "' + common_name + '" and id in ' + verified_ids + ';'
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
            year = int(date_time[0][2])

        if "-" in date_time[0]:
            date_time[0] = date_time[0].split("-")
            month = int(date_time[0][1])
            year = int(date_time[0][2])

        flickrCoord.append([latitude, longitude, year,month])
    return flickrCoord

#get the coordiantes for all the records of nbn for a species
def getNBNCoordinates(mycursor1,common_name):
    nbnCoord = []
    query = "SELECT latitude,longitude,year,month from nbn_data where common_name = '" + common_name + "'and year >= 2004;"
    mycursor1.execute(query)
    nbn_result = mycursor1.fetchall()
    for coord in nbn_result:
        latitude = float(coord[0])
        longitude = float(coord[1])
        year = int(coord[2])
        month = int(coord[3])
        nbnCoord.append([latitude, longitude, year,month])

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
def getFlickrCells(getCellLat, getCellLon, i, flickrCoord, flickr_result):
    monthList = [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]]
    yearList = [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]

    for f_coord in flickrCoord:
        f_lat = f_coord[0]
        f_lon = f_coord[1]
        year = f_coord[2]
        month = f_coord[3]

        if getCellLat[1] <= f_lat <= getCellLat[0] and getCellLon[0] <= f_lon <= getCellLon[3]:

            if year in yearList and month in monthList[0]:
                flickr_result.append([i, year, 1, 1])
            if year in yearList and month in monthList[1]:
                flickr_result.append([i, year, 2, 1])



# check whether there are any nbn occurences in a given cell
def getNBNCells(getCellLat, getCellLon,i,nbnCoord,nbn_result):
    monthList = [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]]
    yearList = [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]

    for n_coord in nbnCoord:
        n_lat = n_coord[0]
        n_lon = n_coord[1]
        year = n_coord[2]
        month = n_coord[3]

        if getCellLat[1] <= n_lat <= getCellLat[0] and getCellLon[0] <= n_lon <= getCellLon[3]:
            if year in yearList and month in monthList[0]:
                nbn_result.append([i, year, 1, 1])
            if year in yearList and month in monthList[1]:
                nbn_result.append([i, year, 2, 1])


def unique(dup_list):
    cleaned_list = []
    for item in dup_list:
        if item not in cleaned_list:
            cleaned_list.append(item)
    return cleaned_list

def confusionMatrix(new_flickr, new_nbn,columnNum):


    total = len(new_flickr)

    truePositive = 0
    trueNegative = 0
    falsePositive = 0
    falseNegative = 0


    for i in range(0, total):

        if (i-columnNum-1) < total and (i-1) < total and (i+columnNum-1) < total and (i+columnNum) < total and (i-columnNum) < total and (i-columnNum+1) < total and (i+columnNum+1) < total:


            if (new_flickr[i][3] != 0 and new_nbn[i][3] != 0 or new_nbn[i-columnNum-1][3] !=0 or
                    new_nbn[i-1][3] != 0 or new_nbn[i+columnNum-1][3] != 0 or new_nbn[i+columnNum][3] !=0 or
                    new_nbn[i-columnNum][3] != 0 or new_nbn[i-columnNum+1][3] != 0 or new_nbn[i+1][3] !=0 or
                    new_nbn[i + columnNum + 1][3] != 0 and new_nbn[i][1] == new_flickr[i][1] and new_nbn[i][2] == new_flickr[i][2]):

                truePositive = truePositive + 1

            if (new_flickr[i][3] == 0 and new_nbn[i][3] == 0 and new_nbn[i-columnNum-1][3] == 0 and
                    new_nbn[i-1][3] == 0 and new_nbn[i+columnNum-1][3] == 0 and new_nbn[i+columnNum][3] == 0 and
                    new_nbn[i-columnNum][3] == 0 and new_nbn[i-columnNum+1][3] == 0 and new_nbn[i+1][3] == 0 and
                    new_nbn[i + columnNum + 1][3] == 0 and new_nbn[i][1] == new_flickr[i][1] and new_nbn[i][2] == new_flickr[i][2]):

                trueNegative = trueNegative + 1

            if (new_flickr[i][3] == 0 and new_nbn[i][3] != 0 or new_nbn[i-columnNum-1][3] !=0 or
                    new_nbn[i-1][3] != 0 or new_nbn[i+columnNum-1][3] != 0 or new_nbn[i+columnNum][3] !=0 or
                    new_nbn[i-columnNum][3] != 0 or new_nbn[i-columnNum+1][3] != 0 or new_nbn[i+1][3] !=0 or
                    new_nbn[i + columnNum + 1][3] != 0 and new_nbn[i][1] == new_flickr[i][1] and new_nbn[i][2] == new_flickr[i][2]):
                falseNegative = falseNegative + 1

            if (new_flickr[i][3] != 0 and new_nbn[i][3] == 0 and new_nbn[i-columnNum-1][3] == 0 and
                    new_nbn[i-1][3] == 0 and new_nbn[i+columnNum-1][3] == 0 and new_nbn[i+columnNum][3] == 0 and
                    new_nbn[i-columnNum][3] == 0 and new_nbn[i-columnNum+1][3] == 0 and new_nbn[i+1][3] == 0 and
                    new_nbn[i + columnNum + 1][3] == 0 and new_nbn[i][1] == new_flickr[i][1] and new_nbn[i][2] == new_flickr[i][2]):
                falsePositive = falsePositive + 1


    return (truePositive, trueNegative, falsePositive, falseNegative, total)


def main():
    names = ['Collared Dove', 'Greenfinch']
    for common_name in names:
        verified_ids = getVerifiedFlickr(common_name)

        mydb, mycursor = dbConnection()
        flickrCount = getCountFlickr(mycursor, verified_ids, common_name)
        nbnCount = getCountNBN(mycursor, common_name)
        finish(mydb, mycursor)

        mydb1, mycursor1 = dbConnection()
        flickrCoord = getFlickrCoordinates(mycursor1, verified_ids, common_name)
        nbnCoord = getNBNCoordinates(mycursor1, common_name)
        finish(mydb1, mycursor1)

        # set uo the coordinates for the grid
        lowLat = 49.00
        highLat = 61.00
        leftLon = -11.50
        rightLon = 2.00


        cells = [5, 10, 15, 20,25,30, 35,40,45,50,55,60]

        for c in cells:
            columnNum = numOfCells(c)


            # create the grid
            lonArray, latArray, lowLat, rowNum = createGrid(columnNum, lowLat, highLat, leftLon, rightLon)
            rowNum = rowNum - 1
            print "rowNum: ",rowNum
            columnNum = columnNum - 1
            print "columnNum: ",columnNum
            print "cell size: ",c
            print "common_name: ",common_name
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

            flickr_result = unique(flickr_result)
            nbn_result = unique(nbn_result)
            all_ids_months = []
            for id in all_ids:
                all_ids_months.append([id, 2004, 1, 0])
                all_ids_months.append([id, 2004, 2, 0])
                all_ids_months.append([id, 2004, 1, 1])
                all_ids_months.append([id, 2004, 2, 1])

                all_ids_months.append([id, 2005, 1, 0])
                all_ids_months.append([id, 2005, 2, 0])
                all_ids_months.append([id, 2005, 1, 1])
                all_ids_months.append([id, 2005, 2, 1])

                all_ids_months.append([id, 2006, 1, 0])
                all_ids_months.append([id, 2006, 2, 0])
                all_ids_months.append([id, 2006, 1, 1])
                all_ids_months.append([id, 2006, 2, 1])

                all_ids_months.append([id, 2007, 1, 0])
                all_ids_months.append([id, 2007, 2, 0])
                all_ids_months.append([id, 2007, 1, 1])
                all_ids_months.append([id, 2007, 2, 1])

                all_ids_months.append([id, 2008, 1, 0])
                all_ids_months.append([id, 2008, 2, 0])
                all_ids_months.append([id, 2008, 1, 1])
                all_ids_months.append([id, 2008, 2, 1])

                all_ids_months.append([id, 2009, 1, 0])
                all_ids_months.append([id, 2009, 2, 0])
                all_ids_months.append([id, 2009, 1, 1])
                all_ids_months.append([id, 2009, 2, 1])

                all_ids_months.append([id, 2010, 1, 0])
                all_ids_months.append([id, 2010, 2, 0])
                all_ids_months.append([id, 2010, 1, 1])
                all_ids_months.append([id, 2010, 2, 1])

                all_ids_months.append([id, 2011, 1, 0])
                all_ids_months.append([id, 2011, 2, 0])
                all_ids_months.append([id, 2011, 1, 1])
                all_ids_months.append([id, 2011, 2, 1])

                all_ids_months.append([id, 2012, 1, 0])
                all_ids_months.append([id, 2012, 2, 0])
                all_ids_months.append([id, 2012, 1, 1])
                all_ids_months.append([id, 2012, 2, 1])

                all_ids_months.append([id, 2013, 1, 0])
                all_ids_months.append([id, 2013, 2, 0])
                all_ids_months.append([id, 2013, 1, 1])
                all_ids_months.append([id, 2013, 2, 1])

                all_ids_months.append([id, 2014, 1, 0])
                all_ids_months.append([id, 2014, 2, 0])
                all_ids_months.append([id, 2014, 1, 1])
                all_ids_months.append([id, 2014, 2, 1])

                all_ids_months.append([id, 2015, 1, 0])
                all_ids_months.append([id, 2015, 2, 0])
                all_ids_months.append([id, 2015, 1, 1])
                all_ids_months.append([id, 2015, 2, 1])

                all_ids_months.append([id, 2016, 1, 0])
                all_ids_months.append([id, 2016, 2, 0])
                all_ids_months.append([id, 2016, 1, 1])
                all_ids_months.append([id, 2016, 2, 1])

                all_ids_months.append([id, 2017, 1, 0])
                all_ids_months.append([id, 2017, 2, 0])
                all_ids_months.append([id, 2017, 1, 1])
                all_ids_months.append([id, 2017, 2, 1])

                all_ids_months.append([id, 2018, 1, 0])
                all_ids_months.append([id, 2018, 2, 0])
                all_ids_months.append([id, 2018, 1, 1])
                all_ids_months.append([id, 2018, 2, 1])

            new_nbn = []
            for item in all_ids_months:
                if item in nbn_result:
                    # print "item: ",item
                    new_nbn.append(item)
                else:
                    new_item = str(item[:3]).replace("[", "").replace("]", "")
                    new_item = new_item + ", 0"
                    array_items = new_item.split(",")
                    ar1_item = int(array_items[0].strip())
                    ar2_item = int(array_items[1].strip())
                    ar3_item = int(array_items[2].strip())
                    ar4_item = int(array_items[3].strip())
                    new_item_l = [ar1_item, ar2_item, ar3_item,ar4_item]
                    # print "new_item_l: ",new_item_l
                    new_nbn.append(new_item_l)

            new_flickr = []
            for item_1 in all_ids_months:
                if item_1 in flickr_result:
                    # print "item_1: ",item_1
                    new_flickr.append(item_1)
                else:
                    new_item_1 = str(item_1[:3]).replace("[", "").replace("]", "")
                    new_item_1 = new_item_1 + ", 0"
                    array_items_1 = new_item_1.split(",")
                    ar1_item_1 = int(array_items_1[0].strip())
                    ar2_item_1 = int(array_items_1[1].strip())
                    ar3_item_1 = int(array_items_1[2].strip())
                    ar4_item_1 = int(array_items_1[3].strip())
                    new_item_l_1 = [ar1_item_1, ar2_item_1, ar3_item_1,ar4_item_1]
                    # print "new_item_l_1: ", new_item_l_1
                    new_flickr.append(new_item_l_1)

            print "flickr len: ", len(new_flickr)
            print "nbn len: ", len(new_nbn)

            truePositive, trueNegative, falsePositive, falseNegative, total = confusionMatrix(new_flickr, new_nbn,columnNum)


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

            newline = str(common_name)+"," + str(nbnCount) + "," + str(flickrCount) + "," + str(c) + "," + str(truePositive) + "," + str(trueNegative) + "," + str(falsePositive) + "," + str(falseNegative) + "," + str(precision) + "," + str(recall) + "," + str(f1) + "," + str(accuracy)
            with open('/Users/thomasedwards/Desktop/paper_update_report_02_01_18/output_all_temporal_year_3x3_6months.csv', 'a') as f:
                f.write(newline + '\n')
                newline = ""



if __name__ == '__main__':
    main()