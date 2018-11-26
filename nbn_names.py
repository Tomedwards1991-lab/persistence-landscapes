import mysql.connector
import csv
import urllib
import json
import re
import time

mydb = mysql.connector.connect(
    host="csmysql.cs.cf.ac.uk",
    user="c1114882",
    passwd="thom9055",
    database="c1114882"
)

mycursor = mydb.cursor()
mydb.autocommit = True


def differentULRS():
    # sql = "SELECT common_name,count(common_name) from nbn_data group by common_name order by count(common_name) DESC LIMIT 1000;"
    # mycursor.execute(sql)
    # myresult = mycursor.fetchall()

    '''
    for result in myresult:
       common_name = result[0]
       name_count = result[1]
       print common_name,name_count
       #csvWriter.writerow([str(common_name),str(name_count)])
    '''

    # URL for downloading all the genuses on the teritory of UK
    # url_genus = "https://records-ws.nbnatlas.org/occurrences/index/download?reasonTypeId=10&q=*:*&fq=taxon_name:*&lat=53.371107&lon=-1.560963&radius=200.0&qa=none"

    # genus = "Anser indicus"

    # url for downloading all the species per genus for UK
    # url_species = "https://records-ws.nbnatlas.org/occurrences/search?q=*:*&fq=genus:"+genus+"&lat=53.371107&lon=-1.560963&radius=200.0&pageSize=20&startIndex=0"
    # print url_species
    # f = urllib2.urlopen(url_species)
    # data = f.read()
    # print data


# downloading the top 1000 species from nbn

def removeNonAscii(s):
    return "".join(i for i in s if ord(i) < 128)


def remove(duplicate):
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list


def get_top1000():
    # url for gettnig the top 1000 species on NBN
    url_topspecies_names = "https://records-ws.nbnatlas.org/occurrence/facets?facets=common_name&q=data_resource_uid:*&flimit=1500&lat=53.371107&lon=-1.560963&radius=200.0"
    f = urllib.urlopen(url_topspecies_names)
    data = json.loads(f.read())
    print type(data)
    print data


# in this function we parse the text file donwloaded with get_top1000
# for having the top 1000 species from nbn
def store_top1000():
    top1000 = []
    counts = open('/Users/thomasedwards/Desktop/nbn_friday/newtop1500.txt', 'r')
    data = counts.read()
    data_str = str(data)
    data_str = data_str.replace('[{"fieldName":"common_name","fieldResult":[{', '').replace(',"count":11702}]', '')
    data_array = data_str.split("},{")
    for item in data_array:
        item_array = item.split(",")
        common_name = str(item_array[1]).replace('i18nCode":"common_name.', '').strip()
        count = str(item_array[2]).replace('"count":', '').strip()
        top1000.append([common_name, count])

    return top1000


def read_top1000(filename):
    top1000 = []
    with open(filename) as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            if not (row[2] == 'x'):
                top1000.append(row[0])

    return top1000


# downloading all the species names - works with a given common name as well
def get_allnames(common_name):
    dictionary = []
    synonyms = []
    other_names = []
    classification = []
    classification_order = ""
    common_name_str = common_name.replace(" ", "%20")
    url_names = "https://species-ws.nbnatlas.org/species/" + common_name_str + ".json"

    print url_names
    f = urllib.urlopen(url_names)
    # data = f.read()
    data = json.loads(f.read())
    guid = data["taxonConcept"]["guid"]
    guid = str(guid).replace("u", "")
    name_string = data["taxonConcept"]["nameString"]
    # name_string = removeNonAscii(name_string)
    name_string = name_string.encode('ascii', 'ignore')
    name_complete = data["taxonConcept"]["nameComplete"]
    name_formatted = data["taxonConcept"]["nameFormatted"]
    name_formatted = str(name_formatted)
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', name_formatted)
    cleantext = cleantext.strip()
    cleantext = removeNonAscii(cleantext)
    common_name = common_name.replace("'", "''")
    classification_class = data["classification"]["class"]
    classification_family = data["classification"]["family"]
    classification_genus = data["classification"]["genus"]
    classification_kingdom = data["classification"]["kingdom"]

    classification_class = classification_class.encode('ascii', 'ignore')
    classification_family = classification_family.encode('ascii', 'ignore')
    classification_genus = classification_genus.encode('ascii', 'ignore')
    classification_kingdom = classification_kingdom.encode('ascii', 'ignore')
    if "order" in data["classification"]:
        classification_order = data["classification"]["order"]
        classification_order = classification_order.encode('ascii', 'ignore')
    else:
        classification_order = "no order"
    classification.append(
        [guid, common_name, classification_class, classification_family, classification_genus, classification_kingdom,
         classification_order])

    for i in range(0, len(data["synonyms"])):
        synonym = data["synonyms"][i]['nameString']
        synonym = synonym.strip()
        synonym = synonym.encode('ascii', 'ignore')
        synonyms.append([synonym])

    for j in range(0, len(data["commonNames"])):
        other_name = data["commonNames"][j]["nameString"]
        other_name = other_name.strip()
        # other_name = removeNonAscii(other_name)
        other_name = other_name.encode('ascii', 'ignore')
        other_names.append([other_name])

    all_names = synonyms + other_names

    for name in all_names:
        name = str(name).replace("[", "").replace("]", "").replace("'", "").strip()
        name = name.encode('ascii', 'ignore')
        dictionary.append([guid, common_name, name_string, name])

    dictionary = remove(dictionary)
    return dictionary, classification

def insert_top1000_nbn(filename):
    names = []
    with open(filename, 'r') as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            name = row[0]
            nbn_count = row[1]
            name = name.replace("'", "")
            names.append([name, nbn_count])

            mycursor.execute("INSERT INTO nbn_top1000(common_name,nbn_count) VALUES ("+name+","+nbn_count+");")


def update_scientific_names():
    sql = '''      
       UPDATE nbn_top1000
       INNER JOIN nbn_dictionary ON (nbn_top1000.common_name = nbn_dictionary.comon_name)
       SET nbn_top1000.uid = nbn_dictionary.uid,
       nbn_top1000.scientific_name = nbn_dictionary.scientific_name
    '''
    mycursor.execute(sql)


def update_flickr_top1000():
    all_names = []
    common_names = []
    scientific_names = []
    other_names = []
    flickr_names = []
    sql = "SELECT * FROM nbn_dictionary"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for i in range(0,len(myresult)):
        common_names.append([myresult[i][0],myresult[i][1]])
        scientific_names.append([myresult[i][0],myresult[i][2]])
        other_names.append([myresult[i][0],myresult[i][3]])



    common_names = remove(common_names)
    scientific_names = remove(scientific_names)
    other_names = remove(other_names)

    for j in range(0,len(common_names)):

        common_name = str(common_names[j][1])
        common_name = '"'+common_name+'"'
        common_name = common_name.replace("'","''")
        print common_name

        sql = "select count(flickr_data.common_name), flickr_data.common_name from flickr_data group by flickr_data.common_name having flickr_data.common_name = "+common_name+";"
        mycursor.execute(sql)
        flickr_names = mycursor.fetchall()
        flickr_names = str(flickr_names)
        ar = flickr_names.split(",")
        flickr_counts = str(ar[0]).replace("'[(","").replace("[(","")
        if len(flickr_counts) > 2:
            print flickr_counts
            sql_up = "UPDATE nbn_top1000 SET nbn_top1000.flickr_count = "+flickr_counts+" WHERE nbn_top1000.common_name = "+common_name+";"
            print sql_up
            mycursor.execute(sql_up)




def main():
    #insert_top1000_nbn('/Users/thomasedwards/Desktop/nbn_friday/species_nbn_top1000_better.csv')
    #update_scientific_names()
    update_flickr_top1000()




    '''
    top1000 = store_top1000()
    with open('/Users/thomasedwards/Desktop/nbn_friday/species_nbn_top1500.csv', 'w') as csvFile:
      writer = csv.writer(csvFile)
      writer.writerows(top1000)
    csvFile.close()
    '''
    '''
    top1000 = read_top1000('/Users/thomasedwards/Desktop/nbn_friday/species_nbn_top1000_better.csv')
    for item in top1000:
        common_name = item
        common_name = common_name.replace('"', '')
        print common_name

        time.sleep(1)
        dictionary, classification = get_allnames(common_name)

        for item in dictionary:
            uid = "'" + item[0] + "'"
            common_name = "'" + item[1] + "'"
            scientific_name = "'" + item[2] + "'"
            other_names = "'" + item[3] + "'"
            print item
            mycursor.execute(
                "INSERT INTO nbn_dictionary VALUES(" + uid + "," + common_name + "," + scientific_name + "," + other_names + ")")

        print "________________________________________"
        for clas in classification:
            print clas
            uid = "'" + clas[0] + "'"
            common_name = "'" + clas[1] + "'"
            classs = "'" + clas[2] + "'"
            family = "'" + clas[3] + "'"
            genus = "'" + clas[4] + "'"
            kingdom = "'" + clas[5] + "'"
            order_species = "'" + clas[6] + "'"

            mycursor.execute(
                "INSERT INTO nbn_classification VALUES(" + uid + "," + common_name + "," + classs + "," + family + "," + genus + "," + kingdom + "," + order_species + ")")
    '''

if __name__ == '__main__':
    main()