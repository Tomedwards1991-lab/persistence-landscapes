import mysql.connector
import csv
import urllib
import json
from unidecode import unidecode
from collections import defaultdict
from itertools import chain
import time

#from typing import List, Any

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
    #topNotIn = ["Linnet","Peacock","Jenkins Spire Snail","Common Birds-Foot-Trefoil","Crested Dogs-Tail","Cats-Ear","Dogs Mercury","Cettis Warbler","Swans-neck Thyme-moss","Greater Birds-foot-trefoil","Colts-Foot","Harts-tongue Thyme-moss","Sheeps Sorrel","Devils-Bit Scabious","Enchanters-Nightshade","Daubentons Bat","Birds-claw Beard-moss","Shepherds-Purse","Ladys Bedstraw","Lesser Birds-claw Beard-moss","Nuttalls Water-Weed","Smooth Hawks-Beard","Harts-Tongue","Fools Water-Cress","Swartzs Feather-moss","Sheeps-fescue","Cut-Leaved Cranes-Bill","True Lovers Knot","Perforate St. Johns-Wort","Natterers Bat","Doves-Foot Cranes-Bill","Sheeps Fescue agg.","Square St. Johns Wort","Kneiffs Feather-moss","Blairs Shoulder-Knot","Roesels Bush Cricket","Vines Rustic","Bruchs Pincushion","Travellers Jo"]
    top1000 = []
    with open(filename) as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            if not (row[2] == 'x'):
                top1000.append(row[0])

    #return topNotIn
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

            names.append([name, nbn_count])

            mycursor.execute("INSERT INTO nbn_top1000(common_name,nbn_count) VALUES ("+name+","+nbn_count+");")


def update_scientific_names():
    sql = '''      
       UPDATE nbn_top1000
       INNER JOIN nbn_dictionary ON (nbn_top1000.common_name = nbn_dictionary.common_name)
       SET nbn_top1000.uid = nbn_dictionary.uid,
       nbn_top1000.scientific_name = nbn_dictionary.scientific_name
    '''
    mycursor.execute(sql)


def update_flickr_top1000():
    names = []
    cleaned_names = []
    sql = "SELECT * FROM nbn_dictionary_list"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for i in range(0,len(myresult)):
        names.append(myresult[i])


    for n in names:
        uid = unidecode(n[0])

        list_names = n[1]
        list_names_array = list_names.split(",")
        for l in list_names_array:
            l = str(l).replace("[","").replace("]","")
            cleaned_names.append([uid, l])

    cleaned_names = remove(cleaned_names)
    for name in cleaned_names:
        uid = name[0]
        str_name = ""
        if str(name[1]).startswith(" u"):
            str_name = str(name[1])[2:]
        elif str(name[1]).startswith("u"):
            str_name = str(name[1])[2:]
        else:
            str_name = str(name[1])
        #print name[0],str_name
        str_name = str_name.replace("'","").replace('"','')
        sql = "select count(flickr_data.common_name), flickr_data.common_name from flickr_data group by flickr_data.common_name having flickr_data.common_name = '"+str_name+"';"
        print sql
        mycursor.execute(sql)
        flickr_names = mycursor.fetchall()
        if mycursor.rowcount != 0:
            print flickr_names
            flickr_names = str(flickr_names)
            print flickr_names
            ar = flickr_names.split(",")
            name = str(ar[1]).replace("')]","").replace(")]","")
            flickr_counts = str(ar[0]).replace("'[(","").replace("[(","")

            print name
            print flickr_counts
            sql_up = "UPDATE nbn_top1000 SET nbn_top1000.flickr_count = "+flickr_counts+" WHERE nbn_top1000.uid = '"+uid+"';"
            print sql_up
            mycursor.execute(sql_up)



def unique(list1):
    unique_list = []

    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list

def populate_dictList():
    dd = defaultdict(list)
    dictNames = dict()
    names = []
    sc_names = {}
    sql = "SELECT * FROM nbn_dictionary"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for i in range(0, len(myresult)):
        term_id = myresult[i][0]
        common_name = myresult[i][1]
        if common_name == "Blair's Shoulder-Knot":
            common_name = 'Blair''s Shoulder-Knot'
        if common_name == "Hart's-Tongue":
            common_name = 'Hart''s-Tongue'
        if common_name == "Smooth Hawk's-Beard":
            common_name = 'Smooth Hawk''s-Beard'
        if common_name == "Dog's Mercury":
            common_name = 'Dog''s Mercury'
        if common_name == "Fool's Water-Cress":
            common_name = 'Fool''s Water-Cress'
        if common_name == "Greater Bird's-foot-trefoil":
            common_name = 'Greater Bird''s-foot-trefoil'
        if common_name == "Perforate St. John's-Wort":
            common_name = 'Perforate St. John''s-Wort'
        if common_name == "Daubenton's Bat":
            common_name = 'Daubenton''s Bat'
        if common_name == "Lady's Bedstraw":
            common_name = 'Lady''s Bedstraw'
        if common_name == "Hart's-Tongue":
            common_name = 'Hart''s-Tongue'
        if common_name == "Cat's-Ear":
            common_name = 'Cat''s-Ear'
        if common_name == "Nuttall's Water-Weed":
            common_name = 'Nuttall''s Water-Weed'
        if common_name == "Sheep's Sorrel":
            common_name = 'Sheep''s Sorrel'
        if common_name == "Shepherd's-Purse":
            common_name = 'Shepherd''s-Purse'
        if common_name == "Sheep's-fescue":
            common_name = 'Sheep''s-fescue'
        if common_name == "Kneiff's Feather-moss":
            common_name = 'Kneiff''s Feather-moss'
        if common_name == "Cut-Leaved Crane's-Bill":
            common_name = 'Cut-Leaved Crane''s-Bill'
        if common_name == "Hart's-tongue Thyme-moss":
            common_name = 'Hart''s-tongue Thyme-moss'
        if common_name == "Devil's-Bit Scabious":
            common_name = 'Devil''s-Bit Scabious'
        if common_name == "Colt's-Foot":
            common_name = 'Colt''s-Foot'
        if common_name == "True Lover's Knot":
            common_name = 'True Lover''s Knot'
        if common_name == "Roesel's Bush Cricket":
            common_name = 'Roesel''s Bush Cricket'
        if common_name == "Crested Dog's-Tail":
            common_name = 'Crested Dog''s-Tail'
        if common_name == "Swartz's Feather-moss":
            common_name = 'Swartz''s Feather-moss'
        if common_name == "Traveller's Joy":
            common_name = 'Traveller''s Joy'
        if common_name == "Sheep's Fescue agg.":
            common_name = 'Sheep''s Fescue agg.'
        if common_name == "Natterer's Bat":
            common_name = 'Natterer''s Bat'
        if common_name == "Lesser Bird's-claw Beard-moss":
            common_name = 'Lesser Bird''s-claw Beard-moss'
        if common_name == "Bird's-claw Beard-moss":
            common_name = 'Bird''s-claw Beard-moss'
        if common_name == "Cetti's Warbler":
            common_name = 'Cetti''s Warbler'
        if common_name == "Enchanter's-Nightshade":
            common_name = 'Enchanter''s-Nightshade'
        if common_name == "Swan's-neck Thyme-moss":
            common_name = 'Swan''s-neck Thyme-moss'
        if common_name == "Bruch's Pincushion":
            common_name = 'Bruch''s Pincushion'
        if common_name == "Dove's-Foot Crane's-Bill":
            common_name = 'Dove''s-Foot Crane''s-Bill'
        if common_name == "Jenkins' Spire Snail":
            common_name = 'Jenkins'' Spire Snail'
        if common_name == "Common Bird's-Foot-Trefoil":
            common_name = 'Common Bird''s-Foot-Trefoil'
        if common_name == "Vine's Rustic":
            common_name = 'Vine''s Rustic'
        if common_name == "Square St. John's Wort":
            common_name = 'Square St. John''s Wort'

        scientific_name = myresult[i][2]
        scientific_name = scientific_name.replace('"', '')
        other_names = myresult[i][3]
        other_names = other_names.replace('"', '')

        names.append([term_id,other_names])
        sc_names[term_id] = [common_name,scientific_name]




    for line in names:
        if line[0] in dictNames:
            # append the new number to the existing array at this slot
            dictNames[line[0]].append(line[1])
        else:
            # create a new array in this slot
            dictNames[line[0]] = [line[1]]

    for d in (sc_names, dictNames):  # you can list as many input dicts as you want here
        for key, value in d.iteritems():
            dd[key].append(value)

    print len(dd)
    for item in dd:
        list_dd = list(chain.from_iterable(list(dd[item])))
        item = '"'+str(item)+'"'
        str_list = '"'+str(list_dd)+'"'
        sql = "INSERT INTO nbn_dictionary_list(uid,names_list) VALUES (" + item + "," + str_list + ");"
        print sql
        mycursor.execute("INSERT INTO nbn_dictionary_list(uid,names_list) VALUES (" + item + "," + str_list + ");")





def main():
    #populate_dictList()
    #insert_top1000_nbn('/Users/thomasedwards/Desktop/nbn_friday/species_nbn_top1000_better.csv')
    #update_scientific_names()
    update_flickr_top1000()
    #update_scientific_names()




    '''
    top1000 = store_top1000()
    with open('/Users/thomasedwards/Desktop/nbn_friday/species_nbn_top1500.csv', 'w') as csvFile:
      writer = csv.writer(csvFile)
      writer.writerows(top1000)
    csvFile.close()
    

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