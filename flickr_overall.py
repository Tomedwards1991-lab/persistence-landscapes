import mysql.connector



mydb = mysql.connector.connect(
    host="csmysql.cs.cf.ac.uk",
    user="c1114882",
    passwd="thom9055",
    database="c1114882"
)

mycursor = mydb.cursor()
mydb.autocommit = True


def iter_row(mycursor, size=100):
    while True:
        rows = mycursor.fetchmany(size)
        if not rows:
            break
        for row in rows:
            yield row

def query_with_fetchmany():
    count_2018 = 0
    count_2017 = 0
    count_2016 = 0
    count_2015 = 0
    count_2014 = 0
    count_2013 = 0
    count_2012 = 0
    count_2011 = 0
    count_2010 = 0
    count_2009 = 0
    count_2008 = 0
    count_2007 = 0
    count_2006 = 0
    count_2005 = 0
    count_2004 = 0

    m_01 = 0
    m_02 = 0
    m_03 = 0
    m_04 = 0
    m_05 = 0
    m_06 = 0
    m_07 = 0
    m_08 = 0
    m_09 = 0
    m_10 = 0
    m_11 = 0
    m_12 = 0

    year = 0
    month = 0
    mycursor.execute("select date_time from flickr_data")
    for row in iter_row(mycursor, 100):
        date_time = row[0]
        date_time = date_time.split(" ")
        if "/" in date_time[0]:
            date_time[0] = date_time[0].split("/")
            date = date_time[0][2] + "-" + date_time[0][1]
            year = int(date_time[0][2])
            month =int(date_time[0][1])
            print month

        if "-" in date_time[0]:
            date_time[0] = date_time[0].split("-")
            date = date_time[0][0] + "-" + date_time[0][1]
            year = int(date_time[0][2])
            month = int(date_time[0][1])
            print month

        if year == 2004:
            #print year
            count_2004 = count_2004+1
            #print count_2004
        if year == 2005:
            #print year
            count_2005 = count_2005+1
            #print count_2005
        if year == 2006:
            #print year
            count_2006 = count_2006+1
            #print count_2006
        if year == 2007:
            #print year
            count_2007 = count_2007+1
            #print count_2007
        if year == 2008:
            #print year
            count_2008 = count_2008+1
            #print count_2008
        if year == 2009:
            #print year
            count_2009 = count_2009+1
            #print count_2009
        if year == 2010:
            #print year
            count_2010 = count_2010+1
            #print count_2010
        if year == 2011:
            #print year
            count_2011 = count_2011+1
            #print count_2011
        if year == 2012:
            #print year
            count_2012 = count_2012+1
            #print count_2012
        if year == 2013:
            #print year
            count_2013 = count_2013+1
            #print count_2013
        if year == 2014:
            #print year
            count_2014 = count_2014+1
            #print count_2014
        if year == 2015:
            #print year
            count_2015 = count_2015+1
            #print count_2015
        if year == 2016:
            #print year
            count_2016 = count_2016+1
            #print count_2016
        if year == 2017:
            #print year
            count_2017 = count_2017+1
            #print count_2017
        if year == 2018:
            #print year
            count_2018 = count_2018+1
            #print count_2018

        if month == 1:
            print month
            m_01 = m_01+1
            print m_01
        if month == 2:
            print month
            m_02 = m_02+1
            print m_02
        if month == 3:
            print month
            m_03 = m_03+1
            print m_03
        if month == 4:
            print month
            m_04 = m_04+1
            print m_04
        if month == 5:
            print month
            m_05 = m_05+1
            print m_05
        if month == 6:
            print month
            m_06 = m_06+1
            print m_06
        if month == 7:
            print month
            m_07 = m_07+1
            print m_07
        if month == 8:
            print month
            m_08 = m_08+1
            print m_08
        if month == 9:
            print month
            m_09 = m_09+1
            print m_09
        if month == 10:
            print month
            m_10 = m_10+1
            print m_10
        if month == 11:
            print month
            m_11 = m_11+1
            print m_11
        if month == 12:
            print month
            m_12 = m_12+1
            print m_12





    months_count = [m_01,m_02,m_03,m_04,m_05,m_06,m_07,m_08,m_09,m_10,m_11,m_12]
    print months_count
    with open('flickr_months_count_all.csv', 'a') as f:
        f.write(str(months_count) + '\n')
    '''
    years_counts = [count_2004,count_2005,count_2006,count_2007,count_2008,count_2009,count_2010,count_2011,count_2012,count_2013,count_2014,count_2015,count_2016,count_2017,count_2018]
    print years_counts
    with open('flickr_years_count_all.csv', 'a') as f:
        f.write(str(years_counts) + '\n')
    '''






def main():
   query_with_fetchmany()


if __name__ == '__main__':
    main()