import mysql.connector
import matplotlib.pyplot as plt
import csv
import numpy as np
from unidecode import unidecode

mydb = mysql.connector.connect(
    host="csmysql.cs.cf.ac.uk",
    user="c1114882",
    passwd="thom9055",
    database="c1114882"
)

mycursor = mydb.cursor()
mydb.autocommit = True

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

def countCategories(category):
    nbn = ""
    flickr = ""
    sql_nbn = "SELECT count(uid) from nbn_top1000 where nbn_count >= "+str(category)+";"
    mycursor.execute(sql_nbn)
    myresult_nbn = mycursor.fetchall()
    for item_nbn in myresult_nbn:
        nbn = int(item_nbn[0])

    sql_flickr = "SELECT count(uid) from nbn_top1000 where flickr_count >= " + str(category) + ";"
    mycursor.execute(sql_flickr)
    myresult_flickr = mycursor.fetchall()
    for item_flickr in myresult_flickr:
        flickr = int(item_flickr[0])

    return nbn,flickr

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


def main():
    nbn_array = []
    flickr_array = []
    categories = [100, 200, 500, 1000, 2000, 5000, 10000, 50000, 100000, 200000, 300000,500000,1000000]
    for category in categories:
        nbn, flickr = countCategories(category)
        print category,nbn, flickr
        nbn_array.append(nbn)
        flickr_array.append(flickr)
        fields = [str(category),str(nbn),str(flickr)]
        with open('/Users/thomasedwards/Desktop/paper_update_report_02_01_18/categories.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(fields)

    lineGraph(categories, nbn_array, flickr_array)


if __name__ == '__main__':
    main()