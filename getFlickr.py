import urllib, json, time
import urllib2
import psycopg2
import csv

'''
conn = psycopg2.connect(database="gisproject", user = "postgres", password = "aliKat", host = "localhost", port = "5432")
print "Success"
cur = conn.cursor()
'''

fields=['id','tag','date','lat','lng']
with open('flikrout5.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow(fields)

with open('export.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        tags = row[1]
        printtags = tags

        if ((' ' in tags) == True):
            tags = tags.replace(" ", "+")
            tags = "%22" + tags + "%22"

        tags = tags.replace("'", "%27")

        page = 1
        key = "0097de9ab582dee0c8174ace8875e17d"
        place = "cnffEpdTUb5v258BBA"

        url = "https://api.flickr.com/services/rest/?method=" \
              "flickr.photos.search&" \
              "api_key=" + key + "&" \
              "tags=" + tags + "&" \
              "place_id=" + place + "&" \
              "per_page=500&" \
              "page=" + str(page) + "&" \
              "format=json&" \
              "nojsoncallback=1"
        print url
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        time.sleep(1)

        page = data['photos']['page']
        pages = data['photos']['pages']
        if pages > 17:
          totalPages = 17

        while page <= pages:
            url = "https://api.flickr.com/services/rest/?method=" \
                 "flickr.photos.search&" \
                 "api_key=" + key + "&" \
                 "tags=" + tags + "+&" \
                 "place_id=" + place + "&" \
                 "per_page=500&" \
                 "page="+str(page)+"&" \
                 "format=json&" \
                 "nojsoncallback=1"
            print url
            response = urllib.urlopen(url)
            data = json.loads(response.read())
            time.sleep(1)

            for i in range(0, len(data['photos']['photo'])):
                photoId = data['photos']['photo'][i]['id']
                getInfoUrl = "https://api.flickr.com/services/rest/?" \
                             "method=flickr.photos.getInfo&" \
                             "api_key=" + key + "&" \
                             "photo_id="+str(photoId)+"&" \
                             "format=json&" \
                             "nojsoncallback=1"
                print getInfoUrl
                getInfoResponse = urllib.urlopen(getInfoUrl)
                getInfoData = json.loads(getInfoResponse.read())
                time.sleep(1)

                try:
                    lat = getInfoData['photo']['location']['latitude']
                    lng = getInfoData['photo']['location']['longitude']
                    title = getInfoData['photo']['title']['_content']
                    dateTaken = getInfoData['photo']['dates']['taken']
                    datePosted = getInfoData['photo']['dates']['posted']
                    image_url = getInfoData['photo']['urls']['url']

                    fields = [photoId, printtags, dateTaken, datePosted,lat, lng,title,image_url]
                    with open('flikrout.csv', 'a') as f:
                        writer = csv.writer(f)
                        writer.writerow(fields)
                except KeyError:
                    pass

            page = page + 1