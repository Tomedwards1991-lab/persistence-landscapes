import urllib, json, time
import os
import urllib2
import csv
import datetime
import mysql.connector
from unidecode import unidecode

mydb = mysql.connector.connect(
    host="csmysql.cs.cf.ac.uk",
    user="c1114882",
    passwd="thom9055",
    database="c1114882"
)

mycursor = mydb.cursor()
mydb.autocommit = True


def removeDsStore(directory):
    if os.path.exists(directory + "/.DS_Store"):
        os.remove(directory + "/.DS_Store")


removeDsStore('images')
for species_name in os.listdir('images'):
    if not (species_name.endswith("_db")):

        try:
            removeDsStore('images/' + species_name)
            for image in os.listdir('images/' + species_name):
                if not (image.endswith("_db.jpg")):
                    image = image.replace(".jpg", "")
                    photoid = image
                    time.sleep(1)

                    url = "https://api.flickr.com/services/rest/?method=flickr.photos.getInfo" \
                          "&api_key=0097de9ab582dee0c8174ace8875e17d" \
                          "&photo_id=" + photoid + \
                          "&format=json" \
                          "&nojsoncallback=1" \
 \
                            print url
                    response = urllib.urlopen(url)
                    data = json.loads(response.read())
                    date_uploaded = data["photo"]["dateuploaded"]
                    date_uploaded = datetime.datetime.fromtimestamp(int(date_uploaded)).strftime('%Y-%m-%d %H:%M:%S')
                    username = data["photo"]["owner"]["username"]
                    username = unidecode(username)
                    username = username.replace("'", "''")
                    realname = data["photo"]["owner"]["realname"]
                    realname = unidecode(realname)
                    realname = realname.replace("'", "''")
                    title = data["photo"]["title"]["_content"]
                    title = unidecode(title)
                    title = title.replace("'", "''")
                    date_taken = data["photo"]["dates"]["taken"]
                    date_posted = data["photo"]["dates"]["posted"]
                    date_posted = datetime.datetime.fromtimestamp(int(date_posted)).strftime('%Y-%m-%d %H:%M:%S')
                    tags = data["photo"]["tags"]["tag"]
                    sql = "INSERT INTO `flickr_metadata` VALUES ('" + photoid + "','" + speciesname + "','" + date_uploaded + "','" + username + "','" + realname + "','" + title + "','" + date_taken + "','" + date_posted + "')"
                    print sql
                    mycursor.execute(sql)

                    for tag_info in tags:
                        machine_tag = tag_info["machine_tag"]
                        tag = tag_info["_content"]
                        tag = unidecode(tag)
                        tag = tag.replace("'", "''")
                        tag_row = tag_info["raw"]
                        tag_row = unidecode(tag_row)
                        tag_row = tag_row.replace("'", "''")
                        tag_author = tag_info["authorname"]
                        tag_author = unidecode(tag_author)
                        tag_author = tag_author.replace("'", "''")
                        sql_tags = "INSERT INTO `flickr_tags` VALUES ('" + str(photoid) + "','" + str(
                            machine_tag) + "','" + tag + "','" + tag_row + "','" + tag_author + "','" + speciesname + "')"
                        print sql_tags

                        mycursor.execute("INSERT INTO `flickr_tags` VALUES ('" + str(photoid) + "','" + str(
                            machine_tag) + "','" + tag + "','" + tag_row + "','" + tag_author + "','" + speciesname + "')")

                    photoid_file = photoid + ".jpg"
                    photoid_file_path = 'images/' + speciesname + '/' + photoid_file
                    inserted_file = photoid + "_db.jpg"
                    inserted_file_path = 'images/' + speciesname + '/' + inserted_file
                    print "id from db", photoid_file
                    print photoid_file_path
                    print inserted_file_path

                    os.rename(photoid_file_path, inserted_file_path)


        except KeyError:
            continue

removeDsStore('images')
for species_name in os.listdir('images'):
    folderpath = 'images/' + species_name
    new = 'images/' + species_name + "_db"
    removeDsStore('images/' + species_name)
    files = os.listdir('images/' + species_name)
    lenth_files = len(files)
    lend = 0
    for filename in files:
        if filename.endswith("_db.jpg"):
            lend = lend + 1
    print lend
    print lenth_files
    if lend == lenth_files:
        print folderpath
        print new
        os.rename(folderpath, new)