import pymysql

host = 'csmysql.cs.cf.ac.uk'
user = 'c1114882'
password = 'thom9055'
db = 'c1114882'
conn = pymysql.connect(host, user, password, db, charset='utf8')
cursor = conn.cursor()
