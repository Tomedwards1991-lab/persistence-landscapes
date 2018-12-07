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

directory = '/Users/thomasedwards/PycharmProjects/persistence-landscapes/Flickr_Images'
removeDsStore(directory)
for species_name in os.listdir(directory):
    done.append(species_name)

mycursor = mydb.cursor()


myresult = []

sql_getFnames = "SELECT uid,scientific_name,common_name FROM nbn_top1000 WHERE flickr_count != 0 and flickr_exists IS NULL;"
mycursor.execute(sql_getFnames)
flickr_names = mycursor.fetchall()
for name in flickr_names:
    uid = name[0]
    common_name = name[2]
    common_name = common_name.replace("'s","\'s")
    print common_name
    sql = ''

    sql = "SELECT id, common_name FROM `flickr_data` where common_name = '"+common_name+"';"

    print "sql getting names: ",sql
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        speciesname = x[1]
        photoid = x[0]

        try:

            print "species name: ",speciesname
            print "photoid: ",photoid
            time.sleep(1)

            file = "Flickr_Images/" + speciesname + "/" + str(photoid) + ".jpg"

            if not os.path.exists(file):
                url = "https://api.flickr.com/services/rest/?method=flickr.photos.getSizes" \
                    "&api_key=0097de9ab582dee0c8174ace8875e17d" \
                    "&photo_id=" + photoid + \
                    "&format=json" \
                    "&nojsoncallback=1" \

                response = urllib.urlopen(url)
                data = json.loads(response.read())
                print "the entire response from Flickr: ",data
                directory = "Flickr_Images/" + speciesname

                if not os.path.exists(directory):
                    os.makedirs(directory)

                download = data["sizes"]["size"][-3]['source']
                print "The image: ",download
                urllib.urlretrieve(download, directory + "/" + photoid + ".jpg")
                file_path = directory + "/" + photoid + ".jpg"

        except KeyError:
            continue
        except ValueError:
            continue


'''
print len(myresult)

print myresult

speciesname = ""
photoid = ""
for x in myresult:
    try:
        speciesname = x[1]
        photoid = x[0]

        print speciesname
        print photoid
        time.sleep(1)
        file = "Flickr_Images/" + speciesname + "/" + str(photoid) + ".jpg"

        if not os.path.exists(file):
            url = "https://api.flickr.com/services/rest/?method=flickr.photos.getSizes" \
                    "&api_key=0097de9ab582dee0c8174ace8875e17d" \
                    "&photo_id=" + photoid + \
                    "&format=json" \
                    "&nojsoncallback=1" \

            response = urllib.urlopen(url)
            data = json.loads(response.read())
            print data
            directory = "Flickr_Images/" + speciesname

            if not os.path.exists(directory):
                os.makedirs(directory)

            download = data["sizes"]["size"][-4]['source']
            print download
            urllib.urlretrieve(download, directory + "/" + photoid + ".jpg")
            file_path = directory + "/" + photoid + ".jpg"

    except KeyError:
        continue
    except ValueError:
        continue
'''
