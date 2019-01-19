import mysql.connector
import matplotlib.pyplot as plt
import re
import os
import csv
import numpy as np
from unidecode import unidecode

'''
mydb = mysql.connector.connect(
    host="csmysql.cs.cf.ac.uk",
    user="c1114882",
    passwd="thom9055",
    database="c1114882"
)

mycursor = mydb.cursor()
mydb.autocommit = True
'''

def getData():
    flickr_counts = []
    nbn_counts = []
    names = []
    sql = "SELECT scientific_name,nbn_count,flickr_count FROM nbn_top1000"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for item in myresult:
        name = str(item[0])
        nbn_c = int(item[1])
        flickr_c = int(item[2])
        flickr_counts.append(flickr_c)
        nbn_counts.append(nbn_c)
        names.append(name)

    return flickr_counts,nbn_counts,names

def flickrCounts():
    query = "SELECT Count(id) FROM temp"
    mycursor.execute(query)
    flickrCount = str(mycursor.fetchone())
    flickrCount = re.search(r'\d+', flickrCount)
    flickrCount = flickrCount.group()
    return int(flickrCount)

def countCategories(category):
    nbn = ""
    flickr = ""
    both = ""

    sql_nbn = "SELECT count(uid) from nbn_top1500 where nbn_count >= "+str(category)+";"
    mycursor.execute(sql_nbn)
    myresult_nbn = mycursor.fetchall()
    for item_nbn in myresult_nbn:
        nbn = int(item_nbn[0])

    sql_flickr = "SELECT count(uid) from nbn_top1500 where flickr_count >= " + str(category) + ";"
    mycursor.execute(sql_flickr)
    myresult_flickr = mycursor.fetchall()
    for item_flickr in myresult_flickr:
        flickr = int(item_flickr[0])

    sql_both = "SELECT count(uid) from nbn_top1500 where nbn_count >= "+str(category)+" and flickr_count >= " + str(category) + ";"
    mycursor.execute(sql_both)
    myresult_both = mycursor.fetchall()
    for item_both in myresult_both:
        both = int(item_both[0])

    return nbn,flickr,both

def lineGraph(categories,nbn_array,flickr_array):
    plt.plot(nbn_array, categories, color='g',label='NBN counts')
    plt.plot(flickr_array, categories, color='orange',label='Flickr counts')
    #ticks = np.arange(100, 1000000, 1000)
    #labels = range(ticks.size)
    #plt.xticks(ticks, labels)
    plt.xlabel('Distinct number of species')
    plt.ylabel('Occurences in dataset')
    plt.legend(loc='upper right')
    plt.title('Distinct species occurences')
    plt.show()

def countComparisonScatter(flickr_counts,nbn_counts,names):

    print flickr_counts
    print nbn_counts

    fig, ax = plt.subplots()
    ax.scatter(flickr_counts,nbn_counts)

    for i, txt in enumerate(names):
        ax.annotate(txt, (nbn_counts[i],flickr_counts[i]))

    plt.title("Number of records per species for NBN versus Flickr")
    plt.xlabel('Number of records per NBN species')
    plt.ylabel('Number of postings per Flickr species')
    plt.savefig('/Users/thomasedwards/Desktop/paper_update_report_02_01_18/fig1.png')
    #plt.show()

def createChart():
    nbn_counts = [1500,1500,1500,1500,1500,940,571,152,100,74,50,29,20]
    flickr_counts = [501,369,246,163,96,39,13]

    n_100 = int(nbn_counts[0])
    n_200 = int(nbn_counts[1])
    n_500 = int(nbn_counts[2])
    n_1000 = int(nbn_counts[3])
    n_2000 = int(nbn_counts[4])
    n_5000 = int(nbn_counts[5])
    n_10000 = int(nbn_counts[6])
    n_50000 = int(nbn_counts[7])
    n_100000 = int(nbn_counts[8])
    n_200000 = int(nbn_counts[9])
    n_300000 = int(nbn_counts[10])
    n_500000 = int(nbn_counts[11])
    n_1000000 = int(nbn_counts[12])

    f_100 = int(flickr_counts[0])
    f_200 = int(flickr_counts[1])
    f_500 = int(flickr_counts[2])
    f_1000 = int(flickr_counts[3])
    f_2000 = int(flickr_counts[4])
    f_5000 = int(flickr_counts[5])
    f_10000 = int(flickr_counts[6])

    labels_n = ['100+: '+str(n_100), '200+: '+str(n_200), '500+: '+str(n_500), '1000+: '+str(n_1000), '2000+: '+str(n_2000), '5000+: '+str(n_5000), '10000+: '+str(n_10000), '50000+: '+str(n_50000),'100000+: '+str(n_100000),'200000+: '+str(n_200000),'300000+: '+str(n_300000),'500000+: '+str(n_500000),'1000000+: '+str(n_1000000)]
    labels_f = ['100+: '+str(f_100), '200+: '+str(f_200), '500+: '+str(f_500), '1000+: '+str(f_1000), '2000+: '+str(f_2000), '5000+: '+str(f_5000), '10000+: '+str(f_10000)]
    sizes_n = [n_100,n_200,n_500,n_1000,n_2000,n_5000,n_10000,n_50000,n_100000,n_200000,n_300000,n_500000,n_1000000]
    sizes_f = [f_100,f_200,f_500,f_1000,f_2000,f_5000,f_10000]
    colors = ['yellowgreen', 'gold', 'lightskyblue','coral', 'grey', 'orchid','salmon', 'green', 'cyan','orange', 'olive', 'lavender']
    color_f = ['yellowgreen', 'gold', 'lightskyblue','coral', 'grey', 'orchid']
    patches, texts = plt.pie(sizes_n,counterclock=False, colors=colors, startangle=-270)
    plt.title("Distinct number of species for NBN ")
    plt.legend(patches, labels_n, loc="center right")
    plt.axis('equal')
    plt.tight_layout()
    filename = '/Users/thomasedwards/Desktop/figures_all/nbn_chart.png'
    plt.savefig(filename)


def verifyImages():
    verified = []
    sql = "select * from image_names,google_scores where image_names.image_id = google_scores.image_id and image_names.terms like '%greenfinch%'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for item in myresult:
        image_id = str(item[0])
        terms = str(item[2]).replace("[","").replace("]","")
        google_label = str(item[6])
        google_score = item[7]
        terms_array = terms.split(", ")
        terms_cleaned = []
        for term in terms_array:
            term = term.replace("'","").strip()
            terms_cleaned.append(term)
            if term == google_label:
                print "-------------------------Match------------------------------"
                print image_id
                verified.append(image_id)
                sql_up = "UPDATE image_names SET image_names.verify = 'yes' WHERE image_names.image_id = '" + image_id + "';"
                print sql_up

                mycursor.execute(sql_up)

    print len(verified)

def removeDsStore(directory):
    if os.path.exists(directory + "/.DS_Store"):
        os.remove(directory + "/.DS_Store")

def iter_row(mycursor1, size=100):
    while True:
        rows = mycursor1.fetchmany(size)
        if not rows:
            break
        for row in rows:
            yield row

def fixImages():

    names = ['Long-Tailed Tit','Magpie','Large Red Damselfly','Cow Parsley','Tree Sparrow','Buzzard','Razorbill','Common Lizard','Silver-Washed Fritillary','Otter','Barn Owl','Bell Heather','Bluebell','Black-poplar','Bee Orchid','Fan-Foot','Red-Fescue','Sand Martin','Black Rustic']
    new_names = []
    removeDsStore('Flickr_Images')
    for species_name in os.listdir('Flickr_Images'):
        if species_name not in names:
            for image in os.listdir('Flickr_Images/' + species_name):
                image_name = image.replace(".jpg","").replace("_yes","")
                new_name = species_name+"."+image_name

                new_names.append(new_name)

    mydb = mysql.connector.connect(
        host="csmysql.cs.cf.ac.uk",
        user="c1114882",
        passwd="thom9055",
        database="c1114882"
    )
    for item in new_names:
        species_name = item.split(".")[0]
        image_name = item.split(".")[1]
        print species_name, image_name
        print item


        mycursor = mydb.cursor()
        mydb.autocommit = True
        sql_up = "UPDATE image_names SET image_names.image_id = '"+item+"' WHERE image_names.image_id = '" + image_name + "';"
        print sql_up
        mycursor.execute(sql_up)

    mycursor.close()
    mydb.close()


    '''
    ids = []
    mydb = mysql.connector.connect(
        host="csmysql.cs.cf.ac.uk",
        user="c1114882",
        passwd="thom9055",
        database="c1114882"
    )

    mycursor = mydb.cursor()
    mydb.autocommit = True

    sql_images = "select image_id from image_names where image_id not like '%.%';"

    mycursor.execute(sql_images)

    for x in iter_row(mycursor, 100):
        photoid = str(x[0])
        ids.append(photoid)

    mycursor.close()
    mydb.close()
    '''





def main():
    #print flickrCounts()
    #verifyImages()
    fixImages()

    #createChart()
    '''
    nbn_array = []
    flickr_array = []
    both_array = []
    categories = [100, 200, 500, 1000, 2000, 5000, 10000, 50000, 100000, 200000, 300000,500000,1000000]
    for category in categories:
        nbn, flickr,both = countCategories(category)
        print category,nbn, flickr,both
        nbn_array.append(nbn)
        flickr_array.append(flickr)
        both_array.append(both)
        fields = [str(category),str(nbn),str(flickr),str(both)]
        with open('/Users/thomasedwards/Desktop/paper_update_report_02_01_18/categories1500.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(fields)
    '''


if __name__ == '__main__':
    main()