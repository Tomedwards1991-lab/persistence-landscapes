import mysql.connector
import os

def getImages(species_name):
    mydb = mysql.connector.connect(
        host="csmysql.cs.cf.ac.uk",
        user="c1114882",
        passwd="thom9055",
        database="c1114882"
    )

    mycursor = mydb.cursor()
    mydb.autocommit = True

    ids = []
    sql_image = "SELECT image_id from image_names where image_id like '" + species_name + ".%';"
    print sql_image
    mycursor.execute(sql_image)
    image_names = mycursor.fetchall()
    for result in image_names:
        id = str(result[0]).split(".")[1]
        name = str(result[0]).split(".")[0]
        ids.append(id)

    mycursor.close()
    mydb.close()

    ids_str = str(ids).replace('[', '(').replace(']', ')')

    return ids_str

def getGScores(ids_str):
    google_res = []
    mydb = mysql.connector.connect(
        host="csmysql.cs.cf.ac.uk",
        user="c1114882",
        passwd="thom9055",
        database="c1114882"
    )

    mycursor = mydb.cursor()
    mydb.autocommit = True

    #sql_google = 'select image_id,lable from google_scores where image_id in '+ids_str+' and image_id not like "%.%" and lable = "bird";'
    sql_google = 'select image_id,lable from google_scores where image_id in '+ids_str+'and image_id not like "%.%";'
    print sql_google
    mycursor.execute(sql_google)
    google_result = mycursor.fetchall()
    for result in google_result:
        id = str(result[0])
        label = str(result[1])
        google_res.append([id,label])

    mycursor.close()
    mydb.close()
    return google_res

def removeDsStore(directory):
    if os.path.exists(directory + "/.DS_Store"):
        os.remove(directory + "/.DS_Store")

def find(sp_name,id_name, path):
    removeDsStore(path)
    for name in os.listdir('Flickr_Images'):
        if sp_name in name:
            for images in os.listdir('Flickr_Images/' + sp_name):
                print images
                if not images.endswith("_bird.jpg"):
                    if id_name in images:
                        id = id_name.replace('.jpg','')
                        real_photo = id+".jpg"
                        new_file_name = id+"_bird.jpg"
                        print id_name
                        print new_file_name
                        old_dir = './Flickr_Images/'+sp_name+'/'+real_photo
                        new_dir = './Flickr_Images/'+sp_name+'/'+new_file_name
                        print old_dir
                        print new_dir
                        os.rename(old_dir, new_dir)

def stats(sp_name,path):
    count = 0
    removeDsStore(path)
    for name in os.listdir('Flickr_Images'):
        if sp_name in name:
            for images in os.listdir('Flickr_Images/' + sp_name):
                if images.endswith("_fp.jpg"):
                    count = count+1

    print count

def getNegatives(sp_name,path):
    neg_ids = []
    removeDsStore(path)
    for name in os.listdir('Flickr_Images'):
        if sp_name in name:
            for images in os.listdir('Flickr_Images/' + sp_name):
                if not images.endswith("_bird.jpg"):
                    id = images.replace("_fn.jpg","")
                    id = id.replace(".jpg","")
                    neg_ids.append(id)

    neg_ids_str = str(neg_ids).replace('[', '(').replace(']', ')')
    return(neg_ids_str)

def fix_negatives(google_res,sp_name,path):
    filter_res = []
    list_tags = 'bird','perching bird','blue tit','tit','old world flycatcher','chickadee','continental robin','robin','songbird','pigeon','woodpigeon','pigeons and doves','sparrow','finch','greenfinch','great tit','dunnock','chaffinch'
    for item in google_res:
        id_name = item[0]
        tag = item[1]
        if tag in list_tags:
            removeDsStore(path)
            for name in os.listdir('Flickr_Images'):
                if sp_name in name:
                    for images in os.listdir('Flickr_Images/' + sp_name):
                        if images.endswith("_fn.jpg"):
                            if id_name in images:
                                print "------------------FIRST IF-----------------"
                                print images
                                print tag
                                id = id_name.replace('_fn.jpg', '')
                                real_photo = id + "_fn.jpg"
                                new_file_name = id + "_bird.jpg"
                                print id_name
                                print new_file_name
                                old_dir = './Flickr_Images/' + sp_name + '/' + real_photo
                                new_dir = './Flickr_Images/' + sp_name + '/' + new_file_name
                                print old_dir
                                print new_dir
                                os.rename(old_dir, new_dir)
                        elif not images.endswith("_fn.jpg") and not images.endswith("_bird.jpg"):
                            if id_name in images:
                                print "-------------SECOND IF------------"
                                print images
                                print tag
                                id = id_name.replace('.jpg', '')
                                real_photo = id + ".jpg"
                                new_file_name = id + "_bird.jpg"
                                print id_name
                                print new_file_name
                                old_dir = './Flickr_Images/' + sp_name + '/' + real_photo
                                new_dir = './Flickr_Images/' + sp_name + '/' + new_file_name
                                print old_dir
                                print new_dir
                                os.rename(old_dir, new_dir)







def main():
    #ids_str = getImages("Greenfinch")
    #print ids_str
    #google_res = getGScores(ids_str)
    #for item in google_res:
        #print item
        #id_name = item[0]
        #find("Greenfinch", id_name, './Flickr_Images')
    #ids_str = getNegatives('Blackbird', './Flickr_Images')
    #google_res = getGScores(ids_str)
    #fix_negatives(google_res, 'Blackbird', './Flickr_Images')
    print "Blackbird-----------------------------"
    stats('Blackbird', './Flickr_Images')
    print "BLUE TIT-------------------------------"
    stats('Blue Tit', './Flickr_Images')
    print "Continental Robin----------------------"
    stats('Continental Robin', './Flickr_Images')
    print "Woodpigeon-------------------------"
    stats('Woodpigeon', './Flickr_Images')
    print "Dunnock----------------------------"
    stats('Dunnock', './Flickr_Images')
    print "Great Tit-------------------------"
    stats('Great Tit', './Flickr_Images')
    print "Chaffinch-------------------------"
    stats('Chaffinch', './Flickr_Images')
    print "House Sparrow----------------------"
    stats('House Sparrow', './Flickr_Images')
    print "Collared Dove---------------------"
    stats('Collared Dove', './Flickr_Images')
    print "Greenfinch------------------------"
    stats('Greenfinch', './Flickr_Images')







if __name__ == '__main__':
    main()