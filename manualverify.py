import cmd
import sys
import mysql.connector

tweets = []
mydb = None
mycursor = None


def dbConnection():

    global mydb
    global mycursor

    mydb = mysql.connector.connect(
        host="csmysql.cs.cf.ac.uk",
        user="c1114882",
        passwd="thom9055",
        database="c1114882"
    )

    mycursor = mydb.cursor()
    mydb.autocommit = True


def finish():
    global mydb
    global mycursor

    mycursor.close()
    mydb.close()


def retrieve_tweets():
    global tweets
    global mycursor

    sql = "SELECT id, text " \
          "FROM tweets " \
          "WHERE checked = False;"
    mycursor.execute(sql)
    tweets = mycursor.fetchall()


def classify_tweets(classifiedAs):
    global mydb
    global mycursor
    global tweets

    print "classified As " + str(classifiedAs)
    sqlupdate = "UPDATE tweets " \
                "SET observation =" + str(classifiedAs) + ", checked = True "\
                "WHERE id = " + str(tweets[0][0]) + ";"
    print sqlupdate


    mycursor.execute(sqlupdate)

    del tweets[0]

    if len(tweets) < 1:
        finish(mydb,mycursor)
        sys.exit()

    print tweets[0]


class CommandExecutor(cmd.Cmd):

    dbConnection()
    retrieve_tweets()

    intro = tweets[0]

    prompt = "> "

    def do_y(self, args=None):
        classify_tweets(True)

    def do_n(self, args=None):
        classify_tweets(False)

    def do_quit(self, args=None):
        finish()
        return True


executor = CommandExecutor()
executor.cmdloop()
