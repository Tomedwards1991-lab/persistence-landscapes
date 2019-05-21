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
    sql_image = "SELECT image_id from image_names where image_id like '%." + species_name + "';"
    #print sql_image
    mycursor.execute(sql_image)
    image_names = mycursor.fetchall()
    for result in image_names:
        id_s = str(result[0])
        ids.append(id_s)

    mycursor.close()
    mydb.close()

    ids_str = str(ids).replace('[', '(').replace(']', ')')

    return ids_str

# gannet - lable = 'goose' or lable = 'bird' or lable = 'seabird' or lable = 'geese' or lable = 'birds' or lable = 'gannet' or lable = 'solan goose' or lable = 'water bird'
# ivy - lable = 'plant' or lable = 'plants' or lable = 'flowering plant' or lable = 'flowering plants' or lable = 'ivy' or lable = 'dicotyledons' or lable = 'magnoliopsida' or lable = 'woody plant' or lable like '%woody%' or lable like '%evergreen%' or lable like '%ground-creeping%';"
# grey squirrel - lable = 'grey squirrel' or lable = 'squirrel' or lable like '%squirrel%'
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
    print "ids_str: ",ids_str
    #sql_google = 'select image_id,lable from google_scores where image_id in '+ids_str+' and image_id not like "%.%" and lable = "bird";'
    #sql_google = 'SELECT image_id,lable from google_scores where image_id in '+ids_str+' and lable = "goose";'
    sql_google =  "select DISTINCT (image_id) from (select image_id,lable from google_scores where image_id like '%.Grey Squirrel')x where lable = 'grey squirrel' or lable = 'squirrel' or lable like '%squirrel%';"
    print sql_google
    mycursor.execute(sql_google)
    google_result = mycursor.fetchall()
    for result in google_result:
        id_s = str(result[0])
        #print id_s,label
        if id_s not in google_res:
            google_res.append([id_s])

    mycursor.close()
    mydb.close()

    return google_res

def removeDsStore(directory):
    if os.path.exists(directory + "/.DS_Store"):
        os.remove(directory + "/.DS_Store")

def find(sp_name,id_name):
    removeDsStore('Flickr_images')
    for name in os.listdir('Flickr_images'):
        if sp_name in name:
            for images in os.listdir('Flickr_images/' + sp_name):
                #print "images: ",images
                #print "id_name: ", id_name
                if not images.endswith("_bird.jpg"):
                    if id_name in images:
                        id_s = id_name.replace('.jpg','')
                        real_photo = id_s+".jpg"
                        new_file_name = id_s+"_bird.jpg"
                        print "sp_name: ", sp_name
                        print "id_name: ",id_name
                        print "new_file_name: ",new_file_name
                        old_dir = './Flickr_images/'+sp_name+'/'+real_photo
                        new_dir = './Flickr_images/'+sp_name+'/'+new_file_name
                        print "old_dir: ",old_dir
                        print "new_dir: ",new_dir
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
                                #os.rename(old_dir, new_dir)







def main():
    ids_str = getImages("Grey Squirrel")
    google_res = getGScores(ids_str)
    print len(google_res)
    for item in google_res:
        print item
        id_name_s = str(item[0])
        id_name = id_name_s+'.jpg'
        find("Grey Squirrel", id_name)
    #ids_str = getNegatives('Blackbird', './Flickr_Images')
    #google_res = getGScores(ids_str)
    #fix_negatives(google_res, 'Blackbird', './Flickr_Images')
    #print "Blackbird-----------------------------"
    #stats('Blackbird', './Flickr_Images')
    #stats('Blue Tit', './Flickr_Images')
    #stats('Continental Robin', './Flickr_Images')
    #stats('Woodpigeon', './Flickr_Images')
    #stats('Dunnock', './Flickr_Images')
    #stats('Great Tit', './Flickr_Images')
    #stats('Chaffinch', './Flickr_Images')
    #stats('House Sparrow', './Flickr_Images')
    #stats('Collared Dove', './Flickr_Images')
    #stats('Greenfinch', './Flickr_Images')







if __name__ == '__main__':
    main()