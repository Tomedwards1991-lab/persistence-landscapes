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

# Anser
genus = sys.argv[1]
url = "https://records-ws.nbnatlas.org/occurrences/index/download?reasonTypeId=10&q=*:*&fq=genus:" + genus + "&lat=53.371107&lon=-1.560963&radius=200.0&qa=none"
f = urllib2.urlopen(url)
data = f.read()
with open("data.zip", "wb") as code:
    code.write(data)  # nrows=5

path_to_zip_file = "./data.zip"
path_to_file = "./"
zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
zip_ref.extractall(path_to_file)
zip_ref.close()

csvfile = 'data.csv'
csv = pd.read_csv(csvfile, sep=',')
j = 0

file = open('processeddata.csv', 'w')

file.write('id,lat,lng,year,month\n')
for i in csv['Year']:
    # if data
    if (numpy.isnan(i) == False and numpy.isnan(csv['Decimal latitude (WGS84)'][j]) == False and numpy.isnan(
            csv['Decimal latitude (WGS84).1'][j]) == False and numpy.isnan(csv['Month'][j]) == False):
        # id lat lng year
        file.write(str(csv['Record ID'][j]) + "," + str(csv['Decimal latitude (WGS84)'][j]) + "," + str(
            csv['Decimal latitude (WGS84).1'][j]) + "," + str(int(csv['Year'][j])) + "," + str(
            int(csv['Month'][j])) + "\n")
    else:
        print "Data is missing"
    j = j + 1
file.close()

newcsv = 'processeddata.csv'
df = pd.read_csv(newcsv)

directory = "toprocess"
if not os.path.exists(directory):
    os.makedirs(directory)

for i, g in df.groupby('month'):
    g.to_csv('./toprocess/{}.csv'.format(i), header=False, index_label=False)

# Initialize grid of points
grid_simplex_object = grid_simplex.grid_simplex(100, 100)
zig_zag_homology_object = zig_zag_homology.zig_zag_homology(grid_simplex_object.simplices)

directoryPath = './toprocess'
file_list = subprocess.check_output(['find', directoryPath, '-name', '*.csv']).split('\n')[:-1]

l1 = []
l2 = []
yearL = []
new_list1 = []
new_list2 = []
new_yearL = []

for i, fileCSV in enumerate(file_list):
    count = 0
    csvfile = open(fileCSV, 'rU')
    mycsv = csv.reader(csvfile)
    for row in mycsv:
        coord1 = row[2]
        coord2 = row[3]
        if (coord1 != "" and coord2 != ""):
            l1.append(coord1)
            l2.append(coord2)
            count = count + 1
    print count

    if (count > 1):

        for item in l1:
            new_list1.append(float(item))

        for item in l2:
            new_list2.append(float(item))

        # Define projection for the British National Grid
        # bng = pyproj.Proj(init='epsg:27700')

        # do british projection
        # bx,by = bng(new_list1,new_list2)

        m1, m2 = new_list1, new_list2

        xmin = min(m1)
        xmax = max(m1)
        ymin = min(m2)
        ymax = max(m2)

        # Apply KDE to the coordiantes and prinyt the results on a grid
        X, Y = numpy.mgrid[xmin:xmax:100j, ymin:ymax:100j]

        positions = numpy.vstack([X.ravel(), Y.ravel()])
        values = numpy.vstack([m1, m2])
        print values
        kernel = stats.gaussian_kde(values, bw_method='silverman')
        kdeOutputArray = numpy.reshape(kernel(positions).T, X.shape)

        # Calculate the mean
        summ = 0
        count = 0
        for x in range(0, len(kdeOutputArray)):
            for y in range(0, len(kdeOutputArray[0])):
                summ = summ + kdeOutputArray[x][y]
                count = count + 1

        mean = summ / count

        # Turn the points on in the grid
        a = numpy.zeros((len(kdeOutputArray), len(kdeOutputArray[0])), dtype=int)
        for x in range(0, len(kdeOutputArray)):
            for y in range(0, len(kdeOutputArray[0])):
                if kdeOutputArray[x][y] > mean:
                    a[x][y] = 1

        grid_simplex_object.update_active_simplex(a)

        zig_zag_homology_object.update_simplex_active(grid_simplex_object.simplex_active, i)
        grid_simplex_object.plot_active_simplex()

# When fihished turn off all points in the grid.
zig_zag_homology_object.remove_all_simplex()
zig_zag_homology_object.sort_persistence()

# Print results
print "zero_dim_persistence: ", zig_zag_homology_object.zero_dim_persistence
print "one_dim_persistence: ", zig_zag_homology_object.one_dim_persistence