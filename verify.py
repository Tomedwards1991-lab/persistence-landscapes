import mysql.connector
import os

mydb = mysql.connector.connect(
  host="csmysql.cs.cf.ac.uk",
  user="c1114882",
  passwd="thom9055",
  database="c1114882"
)

mycursor = mydb.cursor()
mydb.autocommit = True

def getFromDB():

    sql = "select i.image_id, i.terms " \
        "from image_names i " \
        "where i.verify = 'yes';"

    mycursor.execute(sql)
    result = mycursor.fetchall()
    db_results = []

    for row in result:
        image_id =str(row[0])
        terms = str(row[1]).replace("[","").replace("]","")
        terms_array = terms.split(",")
        common_name = terms_array[0]
        db_results.append([image_id,common_name])

    return db_results


def find(sp_name,id_name, path):
    for root, dirs, files in os.walk(path):
        root_str = str(root)
        if len(root_str) > 15:
            position = root_str.rfind('/')
            root_match = root_str[position:]
            root_match_l = root_match.lower()
            root_match_l = root_match_l.replace("/","")
            root_match_l = "'"+root_match_l+"'"

            if sp_name == root_match_l:
                #print "root", root
                for file in files:
                    if id_name in file:
                        id = id_name.replace('.jpg','')
                        new_file_name = id+"_yes.jpg"
                        print file
                        print new_file_name
                        old_dir = './Flickr_Images'+root_match+'/'+file
                        new_dir = './Flickr_Images'+root_match+'/'+new_file_name
                        print old_dir
                        print new_dir
                        os.rename(old_dir, new_dir)
                    #return os.path.join(root, id_name)


def main():
    db_results = getFromDB()

    for item in db_results:
        id = str(item[0])
        sp_name = str(item[1])
        id_name = id+'.jpg'
        find(sp_name,id_name, './Flickr_Images')







if __name__ == '__main__':
    main()