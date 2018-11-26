import urllib, json, time
import os
import urllib2
import csv
import mysql.connector

mydb = mysql.connector.connect(
  host="csmysql.cs.cf.ac.uk",
  user="c1114882",
  passwd="thom9055",
  database="c1114882"
)

done = []
def removeDsStore(directory):
    if os.path.exists(directory + "/.DS_Store"):
        os.remove(directory + "/.DS_Store")

directory = '/Users/tom/PycharmProjects/untitled/venv/images'
removeDsStore(directory)
for species_name in os.listdir(directory):
    done.append(species_name)

mycursor = mydb.cursor()

sql = "SELECT id, common_name FROM `flickr_data`"

mycursor.execute(sql)

myresult = mycursor.fetchall()

print len(myresult)

speciesname = ""
photoid = ""
for x in myresult:
    try:
        if not (x[1] in done):
            speciesname = x[1]
            photoid = x[0]

            print speciesname
            print photoid
            time.sleep(1)
            file = "images/" + speciesname + "/" + str(photoid) + ".jpg"

            if not os.path.exists(file):
                url = "https://api.flickr.com/services/rest/?method=flickr.photos.getSizes" \
                        "&api_key=0097de9ab582dee0c8174ace8875e17d" \
                        "&photo_id=" + photoid + \
                        "&format=json" \
                        "&nojsoncallback=1" \

                response = urllib.urlopen(url)
                data = json.loads(response.read())
                print data
                directory = "images/" + speciesname

                if not os.path.exists(directory):
                    os.makedirs(directory)

                download = data["sizes"]["size"][-3]['source']
                urllib.urlretrieve(download, directory + "/" + photoid + ".jpg")
                file_path = directory + "/" + photoid + ".jpg"

    except KeyError:
        continue
    except ValueError:
        continue