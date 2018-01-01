import sys
import math
import numpy
import grid_simplex
import zig_zag_homology
import csv
from itertools import groupby
import subprocess
from scipy import stats
import pyproj
import matplotlib.pyplot as plt
import os
import urllib2
import zipfile
from collections import defaultdict
import pandas as pd

#Anser
genus = sys.argv[1]
url = "https://records-ws.nbnatlas.org/occurrences/index/download?reasonTypeId=10&q=*:*&fq=genus:"+genus+"&lat=53.371107&lon=-1.560963&radius=200.0&qa=none"
f = urllib2.urlopen(url)
data = f.read()
with open("data.zip", "wb") as code:
    code.write(data)#nrows=5

path_to_zip_file = "./data.zip"
path_to_file = "./"
zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
zip_ref.extractall(path_to_file)
zip_ref.close()

csvfile = 'data.csv'
csv = pd.read_csv(csvfile, sep=',')
j = 0

file = open('processeddata.csv','w')

file.write('id,lat,lng,year\n')
for i in csv['Year']:
    # if data
    if(numpy.isnan(i) == False and numpy.isnan(csv['Decimal latitude (WGS84)'][j]) == False and numpy.isnan(csv['Decimal latitude (WGS84).1'][j]) == False):
        #id lat lng year
        file.write(str(csv['Record ID'][j]) + "," + str(csv['Decimal latitude (WGS84)'][j])+ "," +str(csv['Decimal latitude (WGS84).1'][j]) + "," +str(int(csv['Year'][j])) + "\n")
    else:
        print "Data is missing"
    j = j + 1
file.close()