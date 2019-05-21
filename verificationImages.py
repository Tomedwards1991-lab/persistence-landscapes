import io
import urllib, json, time
import os
import mysql.connector
import ssl
import csv



#######################################
##########SET UP google session#######

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

def finish(mydb,mycursor):
    mycursor.close()
    mydb.close()

def mainQuery(mydb,mycursor):
    result = []

    sql_getFnames = "SELECT n_top.uid,n_dict.names_list,n_top.common_name " \
                    "FROM nbn_top1500 n_top,nbn_dictionary_list n_dict " \
                    "WHERE n_top.common_name not in ('Adder','Blackbird','Blue Tit','Carrion Crow','Chaffinch','Coal Tit','Collared Dove','Common Carder Bee','Continental Robin'," \
                    "'Dunnock','Goldfinch','Great Spotted Woodpecker','Great Tit','Greenfinch','House Sparrow','Jackdaw','Long-Tailed Tit','Magpie','Song Thrush','Starling','Woodpigeon','Wren'," \
                    "'Swallow','Domestic Cat','Teal','Heart and Dart','Comma','Hebrew Character','Garden Carpet','Ash','Hobby','Knot','Hazelnut','Uncertain','Beech','Flame','Cat''s-Ear','Light Emerald','Clay','Snout'," \
                    "'Spectacle','Spectacle','Garlic Mustard','Hard Rush','Green Carpet','Lords-And-Ladies','Heather','Drinker','Nutmeg','Yellow Shell'," \
                    "'Water Forget-Me-Not','Black Clock','Dace','Satellite','Shoulder Stripe','Broom','Brick','Gothic','Large Emerald','Chevron','Pope','Aspen'," \
                    "'Spinach','Olive Pearl','Herald','Bream Flat','Miller','Hop','Carrot','Blinks','Bleak','Streak','Honesty','Buzzard','Black Rustic','Broken-Barred Carpet','Buzzard','Carrion Crow','Collared Dove'," \
                    "'Common Bonnet','Common Carder Bee','Cow Parsely','Danish Scurvygrass','Early Bumble Bee','Fan-Foot','Hoary Willowherb','Irish Yew','July Highflyer','Large Red Damselfly','Magpie'," \
                    "'Minnow','Pearl Bordered Fritillary','Razorbill','Red Fescue','Sand Martin','Song Thrush','Stone-Curlew','Thale Cress','Tree Sparrow','White-Tailed Bumble Bee','Whitish Feather-moss'," \
                    "'Cow Parsley','Field Maple','Otter','Barn Owl','Bee Orchid','Bluebell''Mandarin Duck', 'Wood Duck', 'Egyptian Goose', " \
                    "'Snow Goose', 'Barnacle Goose'," \
                    " 'Eurasian Eagle Owl', 'Buddleia', 'Sika Deer', 'Golden Pheasant', " \
                    "'Black Swan', 'Giant Hogweed', 'Grey squirrel', 'Rhododendron', " \
                    "'Reeve''s muntjac','wild boar','Gannet','Ivy','Mallard','Mantell Paun','Snipe','Bar-Headed Goose','Rabbit','Barn Owl','Bluebell','Bracken','Dandelion') " \
                    "and n_top.uid = n_dict.uid; " \

    sql_getFnames1 = "SELECT n_top.uid,n_dict.names_list,n_top.common_name " \
                    "FROM nbn_top1500 n_top,nbn_dictionary_list n_dict " \
                    "WHERE n_top.common_name = 'Barn Owl','Bluebell','Bracken','Dandelion';" \

    sql_getFnames2 = "SELECT n_top.uid,n_dict.names_list,n_top.common_name " \
                    "FROM nbn_top1500 n_top,nbn_dictionary_list n_dict " \
                    "WHERE n_top.common_name in ('Gannet','Ivy','Mallard','Mantell Paun','Snipe','Bar-Headed Goose','Rabbit');" \


    sql_getFnames3 = "SELECT n_top.uid,n_dict.names_list,n_top.common_name " \
    "FROM nbn_top1500 n_top,nbn_dictionary_list n_dict " \
    "WHERE n_top.common_name in ('Mandarin Duck', 'Wood Duck', 'Egyptian Goose', " \
                    "'Snow Goose', 'Barnacle Goose'," \
                    " 'Eurasian Eagle Owl', 'Buddleia', 'Sika Deer', 'Golden Pheasant', " \
                    "'Black Swan', 'Giant Hogweed', 'Grey squirrel', 'Rhododendron', " \
                    "'Reeve''s muntjac','wild boar');" \

    mycursor.execute(sql_getFnames)
    flickr_names = mycursor.fetchall()
    all_names_list = []
    for name in flickr_names:
        uid = name[0]
        common_name = name[2]
        common_name = common_name.replace("'s", "''s")
        result.append(common_name)
        all_names = str(name[1])
        all_names = all_names.replace("[", "").replace("]", "")
        all_names_array = all_names.split(",")
        for i in all_names_array:
            i = i.replace('u', '', 1)
            i = i[1:-1]
            i = i.replace("'", "", 1)
            i = i.lower()
            all_names_list.append(i)

    all_names_list = unique(all_names_list)


    return result

def iter_row(mycursor1, size=100):
    while True:
        rows = mycursor1.fetchmany(size)
        if not rows:
            break
        for row in rows:
            yield row

def getFlickr(mydb1,mycursor1,result):
    invalid_ids = []
    with open('invalid_ids.csv') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            row_str = str(row[0])
            id = row_str.split(".")[1]
            invalid_ids.append(id)

    invalid_ids_str = str(invalid_ids).replace("[","(").replace("]",")")
    #print invalid_ids_str

    new_result = []
    for res in result:
        new_result.append(str(res))

    flickr_data = []
    result_str = str(new_result)
    result_str = result_str.replace("[","(").replace("]",")")
    #sql = "SELECT id, common_name FROM `flickr_data` where common_name = '" + common_name + "';"
    sql = "SELECT id, common_name FROM `flickr_data` where common_name in " + result_str + " and id not in "+invalid_ids_str+";"

    #print "SQL GETTING NAMES: ",sql
    mycursor1.execute(sql)
    for x in iter_row(mycursor1, 100):
        speciesname = x[1]
        photoid = x[0]

        flickr_data.append([speciesname,photoid])

    return flickr_data


def getPhotosAndLabels(flickr_data):


    google_table = []
    # Instantiates a client
    client = vision.ImageAnnotatorClient()
    ssl._create_default_https_context = ssl._create_unverified_context

    for x in flickr_data:
        speciesname = x[0]
        photoid = x[1]
        print "species name:",speciesname
        print "photoid",photoid

        try:


            file = "Flickr_Images/" + speciesname + "/" + str(photoid) + ".jpg"
            #print "file: ",file
            if not os.path.exists(file):
                url = "https://api.flickr.com/services/rest/?method=flickr.photos.getSizes" \
                    "&api_key=0097de9ab582dee0c8174ace8875e17d" \
                    "&photo_id=" + photoid + \
                    "&format=json" \
                    "&nojsoncallback=1" \

                #print "FLICKR URL:", url
                response = urllib.urlopen(url)
                data = json.loads(response.read())
                #print "the entire response from Flickr: ",data

                data_str = str(data)
                if "u'message': u'Photo not found'" in data_str:
                    print "----------PHOTO NOT FOUND-------------------"
                    #print "data_str not found: ", data_str
                    not_found = speciesname+"."+photoid
                    #print "not_found: ",not_found
                    newline = str(not_found)
                    with open('invalid_ids.csv','a') as f:
                        f.write(newline + '\n')
                        newline = ""


                directory = "Flickr_Images/" + speciesname

                if not os.path.exists(directory):
                    os.makedirs(directory)

                download = data["sizes"]["size"][-4]['source']
                download.replace("https", "http")
                #print "The image download from Flickr: ",download

                urllib.urlretrieve(download, directory + "/" + photoid + ".jpg")
                #print "Hi"
                file_path = directory + "/" + photoid + ".jpg"
                #print "The file path to the image:", file_path


                # The name of the image file to annotate
                file_name = os.path.join(os.path.dirname(__file__),file_path)

                #print "--------For the image table--------"
                #print "photoid: ", photoid

                image_table_id = str(photoid)+"."+str(speciesname)
                #print image_table_id
                #image_table.append([str(image_table_id),"need update","need update",nothing,nothing])
                mydb2, mycursor2 = dbConnection()
                mycursor2.execute('INSERT IGNORE INTO image_names VALUES ("' + str(image_table_id)+'","need filling","nothing","nothing","nothing");')
                #print sql_image
                #print "IMAGE INSERT FINISHED"
                finish(mydb2, mycursor2)
                # Loads the image into memory
                with io.open(file_name, 'rb') as image_file:
                    content = image_file.read()

                image = types.Image(content=content)

                # Performs label detection on the image file
                response = client.label_detection(image=image)
                labels = response.label_annotations

                #print('Labels:')
                for label in labels:
                    label_description = str(label.description).lower()
                    label_description = label_description.replace("'", "''")
                    #print "-------------VALUES FOR Google-scores------------"
                    #print(photoid)
                    #print(label_description)
                    #print(label.score)
                    google_id = str(photoid)+"."+str(speciesname)
                    google_table.append([str(google_id),label_description,str(label.score)])
                    mydb3, mycursor3 = dbConnection()
                    sql_g = "INSERT INTO google_scores VALUES ('" + str(google_id) + "','" + label_description + "','" + str(label.score) + "');"
                    mycursor3.execute(sql_g)
                    #print sql_g
                    #print "GOOGLE INSERT FINISHED"
                    finish(mydb3, mycursor3)
                    #print "after finish"
        except KeyError:
            continue
        except ValueError:
            continue
        except IOError:
            continue


def main():
    mydb, mycursor = dbConnection()
    result = mainQuery(mydb,mycursor)
    finish(mydb, mycursor)

    #print "result: ", result

    mydb1, mycursor1 = dbConnection()
    flickr_data = getFlickr(mydb1, mycursor1, result)
    finish(mydb1, mycursor1)

    getPhotosAndLabels(flickr_data)




if __name__ == '__main__':
    main()
