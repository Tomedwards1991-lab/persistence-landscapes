import io
import urllib, json, time
import os
import mysql.connector

# Imports the Google Cloud client library
#from google.api_core import protobuf_helpers as protobuf
from google.cloud import vision
from google.cloud.vision import types

# Instantiates a client
client = vision.ImageAnnotatorClient()

mydb = mysql.connector.connect(
  host="csmysql.cs.cf.ac.uk",
  user="c1114882",
  passwd="thom9055",
  database="c1114882"
)

mycursor = mydb.cursor()

sql_getFnames = "SELECT n_top.uid,n_dict.names_list,n_top.common_name " \
                "FROM nbn_top1000 n_top,nbn_dictionary_list n_dict " \
                "WHERE flickr_count != 0 " \
                "and flickr_exists IS NULL " \
                "and n_top.uid = n_dict.uid; " \

mycursor.execute(sql_getFnames)
flickr_names = mycursor.fetchall()
for name in flickr_names:
    uid = name[0]
    names_list = name[1]
    common_name = name[2]
    common_name = common_name.replace("'s","\'s")
    print common_name
    print names_list
    sql = ''

    sql = "SELECT id, common_name FROM `flickr_data` where common_name = '"+common_name+"';"

    print "sql getting names: ",sql
    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    '''
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

                # Loads the image into memory
                with io.open(file_name, 'rb') as image_file:
                    content = image_file.read()

                image = types.Image(content=content)

                # Performs label detection on the image file
                response = client.label_detection(image=image)
                labels = response.label_annotations

                print('Labels:')
                for label in labels:
                    print(label.description)
                    print(label.score)
            
        
        except KeyError:
            continue
        except ValueError:
            continue
    '''