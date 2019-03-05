import urllib, json, time
import mysql.connector
#import pymysql
import csv

def dbConnection():
    mydb = mysql.connector.connect(
        host="csmysql.cs.cf.ac.uk",
        user="c1114882",
        passwd="thom9055",
        database="c1114882"
    )

    mycursor = mydb.cursor()
    mydb.autocommit = True
    return mydb, mycursor


# close database connecton
def finish(mydb, mycursor):
    mycursor.close()
    mydb.close()

def getData(tags):

    printtags = tags

    if ((' ' in tags) == True):
        tags = tags.replace(" ", "+")
        tags = "%22" + tags + "%22"

    tags = tags.replace("'", "%27")

    page = 1
    key = "0097de9ab582dee0c8174ace8875e17d"
    place = "cnffEpdTUb5v258BBA"
    try:
        url = "https://api.flickr.com/services/rest/?method=" \
                "flickr.photos.search&" \
                "api_key=" + key + "&" \
                "tags=" + tags + "&" \
                "place_id=" + place + "&" \
                "per_page=500&" \
                "page=" + str(page) + "&" \
                "format=json&" \
                "nojsoncallback=1"
        #print url
        response = urllib.urlopen(url)
        data = json.loads(response.read())

        page = data['photos']['page']
        totalPages = data['photos']['pages']
        if totalPages > 17:
            totalPages = 17

        while page <= totalPages:
            print "page: ",page
            url = "https://api.flickr.com/services/rest/?method=" \
                    "flickr.photos.search&" \
                    "api_key=" + key + "&" \
                    "tags=" + tags + "+&" \
                    "place_id=" + place + "&" \
                    "per_page=500&" \
                    "page="+str(page)+"&" \
                    "format=json&" \
                    "nojsoncallback=1"
            #print url
            response = urllib.urlopen(url)
            data = json.loads(response.read())

            for i in range(0, len(data['photos']['photo'])):
                photoId = data['photos']['photo'][i]['id']
                getInfoUrl = "https://api.flickr.com/services/rest/?" \
                                "method=flickr.photos.getInfo&" \
                                "api_key=" + key + "&" \
                                "photo_id="+str(photoId)+"&" \
                                "format=json&" \
                                "nojsoncallback=1"

                print "page: ", page
                print "getInfoUrl: ",getInfoUrl
                getInfoResponse = urllib.urlopen(getInfoUrl)
                getInfoData = json.loads(getInfoResponse.read())
                #time.sleep(1)


                lat = getInfoData['photo']['location']['latitude']
                lng = getInfoData['photo']['location']['longitude']
                #title = getInfoData['photo']['title']['_content']
                dateTaken = getInfoData['photo']['dates']['taken']
                #datePosted = getInfoData['photo']['dates']['posted']
                #image_url = getInfoData['photo']['urls']['url']

                mydb, mycursor = dbConnection()
                sql = 'INSERT IGNORE INTO flickr_data VALUES ("' + str(printtags) + '", "' + str(photoId) + '", "' + str(lat) + '", "' + str(lng) + '", "' + str(dateTaken)+'");'
                mycursor.execute(sql)
                finish(mydb, mycursor)

            page = page + 1

    except KeyError:
        pass

    except ValueError:
        pass

    except mysql.connector.OperationalError:

        mydb, mycursor = dbConnection()
        sql = 'INSERT IGNORE INTO flickr_data VALUES ("' + str(printtags) + '", "' + str(photoId) + '", "' + str(lat) + '", "' + str(lng) + '", "' + str(dateTaken) + '");'
        mycursor.execute(sql)
        finish(mydb, mycursor)



def main():

    names = [ 'Rhododendron','Rhododenron ponticum', 'Wood Duck', 'Aix sponsa', 'Giant Hogweed','Heracleum mantegazzianum']
    print names
    for tags in names:
        print tags
        getData(tags)


if __name__ == "__main__":
    main()