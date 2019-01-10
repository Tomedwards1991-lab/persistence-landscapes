import mysql.connector

mydb = mysql.connector.connect(
  host="csmysql.cs.cf.ac.uk",
  user="c1114882",
  passwd="thom9055",
  database="c1114882"
)

mycursor = mydb.cursor()
mydb.autocommit = True

sql = "select i.image_id,i.terms,g.lable " \
      "from image_names i, google_scores g " \
      "where i.image_id = g.image_id; " \

mycursor.execute(sql)
result = mycursor.fetchall()


for i in result:
    list_terms = []
    image_id = str(i[0])
    terms = str(i[1]).replace("[","").replace("]","")
    label = str(i[2])
    print image_id
    print label

    terms_array = terms.split(",")
    for item in terms_array:
        item = item[1:-1]
        item = item.replace("'", "", 1)
        item = item.strip()
        list_terms.append(item)

    print list_terms
    if label in list_terms:
        print "match"
        print image_id
        print label
        mycursor.execute("UPDATE image_names SET verify = 'match', column2 = '"+label+"' WHERE image_id = '"+image_id+"';")
    else:
        print "no match"
        mycursor.execute("UPDATE image_names SET verify = 'no match'")

