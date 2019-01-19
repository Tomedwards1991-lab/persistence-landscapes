import mysql.connector
import csv

def getGoogleLabels(species_name):
    mydb = mysql.connector.connect(
        host="csmysql.cs.cf.ac.uk",
        user="c1114882",
        passwd="thom9055",
        database="c1114882"
    )

    mycursor = mydb.cursor()
    mydb.autocommit = True

    ids = []
    sql_image = "SELECT image_id from image_names where image_id like '"+species_name+".%';"
    print sql_image
    mycursor.execute(sql_image)
    image_names = mycursor.fetchall()
    for result in image_names:
        id = str(result[0]).split(".")[1]
        name = str(result[0]).split(".")[0]
        ids.append(id)

    mycursor.close()
    mydb.close()

    ids_str = str(ids).replace('[','(').replace(']',')')

    mydb = mysql.connector.connect(
        host="csmysql.cs.cf.ac.uk",
        user="c1114882",
        passwd="thom9055",
        database="c1114882"
    )

    mycursor = mydb.cursor()
    mydb.autocommit = True
    google_out = []
    sql_google = 'select lable,count(lable) from (select image_id,lable from google_scores where image_id in '+ids_str+') t1 group by lable order by count(lable) DESC;'

    #sql_google = "select lable,count(lable) from (select image_id,lable from google_scores where image_id in (8100864940,8418554655)) t1 group by lable order by count(lable) DESC;"
    print species_name
    print sql_google
    mycursor.execute(sql_google)
    google_labels = mycursor.fetchall()
    for g_result in google_labels:
        label = str(g_result[0])
        count = str(g_result[1])
        print label,count
        google_out.append([label,count])

    mycursor.close()
    mydb.close()

    with open('google_labels_Continental Robin.csv', 'w') as f_handle:
        writer = csv.writer(f_handle)
        header = ['label', 'count']
        writer.writerow(header)
        for row in google_out:
            writer.writerow(row)

def readCSV(fileName):
    with open(fileName) as csv_file:
        csv_reader = csv.reader(csv_file)

        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            if 0 < line_count <= 15:
                print row
                line_count += 1

#def createChart(csv_file):

def main():
    #getGoogleLabels('Continental Robin')
    readCSV('google_labels_Blackbird.csv')


if __name__ == '__main__':
    main()