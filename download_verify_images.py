import io
import urllib, json, time
import os
import mysql.connector

# Imports the Google Cloud client library
#from google.api_core import protobuf_helpers as protobuf
from google.cloud import vision
from google.cloud.vision import types

def unique(list1):
    unique_list = []

    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list

# Instantiates a client
client = vision.ImageAnnotatorClient()

mydb = mysql.connector.connect(
  host="csmysql.cs.cf.ac.uk",
  user="c1114882",
  passwd="thom9055",
  database="c1114882"
)

mycursor = mydb.cursor()
mydb.autocommit = True

sql_getFnames = "SELECT n_top.uid,n_dict.names_list,n_top.common_name " \
                "FROM nbn_top1000 n_top,nbn_dictionary_list n_dict " \
                "WHERE flickr_count != 0 " \
                "and flickr_exists IS NULL " \
                "and n_top.uid = n_dict.uid " \
                "and n_top.uid = 'NHMSYS0000875576'; " \


mycursor.execute(sql_getFnames)
flickr_names = mycursor.fetchall()
for name in flickr_names:
    all_names_list = []
    uid = name[0]
    all_names = str(name[1])
    all_names = all_names.replace("[","").replace("]","")
    all_names_array = all_names.split(",")
    for i in all_names_array:
        i = i.replace('u','',1)
        i = i[1:-1]
        i = i.replace("'","",1)
        i = i.lower()
        all_names_list.append(i)


    all_names_list = unique(all_names_list)
    common_name = name[2]
    common_name = common_name.replace("'s","''s")
    sql = ''


    sql = "SELECT id, common_name FROM `flickr_data` where common_name = '"+common_name+"';"

    #print "sql getting names: ",sql
    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    for x in myresult:
        speciesname = x[1]
        photoid = x[0]

        try:

            print "species name: ",speciesname

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
                #print "the entire response from Flickr: ",data
                directory = "Flickr_Images/" + speciesname

                if not os.path.exists(directory):
                    os.makedirs(directory)

                download = data["sizes"]["size"][-4]['source']
                #print "The image: ",download
                urllib.urlretrieve(download, directory + "/" + photoid + ".jpg")
                file_path = directory + "/" + photoid + ".jpg"


                # The name of the image file to annotate
                file_name = os.path.join(
                    os.path.dirname(__file__),file_path)


                print "--------For the image table--------"
                print "photoid: ", photoid
                print "uid: ", uid
                print "all_names: ", all_names_list
                mycursor.execute('INSERT IGNORE INTO image_names VALUES ("'+str(photoid)+'","'+str(uid)+'","'+str(all_names_list)+'",'+'"nothing","nothing");')

                # Loads the image into memory
                with io.open(file_name, 'rb') as image_file:
                    content = image_file.read()

                image = types.Image(content=content)

                # Performs label detection on the image file
                response = client.label_detection(image=image)
                labels = response.label_annotations


                print('Labels:')
                for label in labels:
                    label_description = str(label.description).lower()
                    print "-------------VALUES FOR Google-scores------------"
                    print(photoid)
                    print(label_description)
                    print(label.score)
                    mycursor.execute("INSERT INTO google_scores VALUES ('" + str(photoid) + "','" + label_description + "','" + str(label.score) + "');")

        except KeyError:
            continue
        except ValueError:
            continue
