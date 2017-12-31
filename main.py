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

url = "https://records-ws.nbnatlas.org/occurrences/index/download?reasonTypeId=10&q=*:*&fq=genus:Anser&lat=53.371107&lon=-1.560963&radius=200.0&qa=none"
f = urllib2.urlopen(url)
data = f.read()
with open("data.zip", "wb") as code:
    code.write(data)

path_to_zip_file = "./data.zip"
path_to_file = "./"
zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
zip_ref.extractall(path_to_file)
zip_ref.close()

# https://species-ws.nbnatlas.org/search?q={mallard}
# Read in the csv file and store the coordiantes in a list

l1 = []
l2 = []
yearL = []
new_list1 = []
new_list2 = []
new_yearL = []
# os.mkdir("./csvss")
with open("./data.csv", 'rU') as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)
    data = defaultdict(lambda: [header])
    _ = data[header[34][:34]]
    for row in reader:
        data[row[34][:34]].append(row)
    for file_name, rows in data.items():
        with open(file_name, 'w') as f:
            for row in rows:
                f.write(str(row) + '\n')
checker = False
for key, rows in groupby(csv.reader(open("./data.csv")),
                         lambda row: row[34]):
    with open("%s.csv" % key, "w") as output:
        if checker!=False:
            for row in rows:
                output.write(",".join(row) + "\n")      

os.remove('data.csv')
os.remove('citation.csv')
os.remove('headings.csv')
# Initialize grid of points 
grid_simplex_object = grid_simplex.grid_simplex(100,100) 
zig_zag_homology_object = zig_zag_homology.zig_zag_homology(grid_simplex_object.simplices)

directoryPath = '/Users/thomasedwards/Desktop/WorkPhDAT/spatial_temporal_topology_library/'
file_list = subprocess.check_output(['find',directoryPath,'-name','*.csv']).split('\n')[:-1]


for i, fileCSV in enumerate(file_list):
    print i
    csvfile = open(fileCSV, 'rU')
    mycsv = csv.reader(csvfile)
    for row in mycsv:
        coord1 = row[22]
        coord2 = row[23]
        if(coord1 != "" and coord2 != ""):
            l1.append(coord1)
            l2.append(coord2)

    for item in l1:
        new_list1.append(float(item))

    for item in l2:
        new_list2.append(float(item))


    #Define projection for the British National Grid
    bng = pyproj.Proj(init='epsg:27700')


    #do british projection
    bx,by = bng(new_list1,new_list2)

    m1, m2 = bx, by

    xmin = min(m1)
    xmax = max(m1)
    ymin = min(m2)
    ymax = max(m2)

    #Apply KDE to the coordiantes and prinyt the results on a grid
    X, Y = numpy.mgrid[xmin:xmax:100j, ymin:ymax:100j]
    positions = numpy.vstack([X.ravel(), Y.ravel()])
    values = numpy.vstack([m1, m2])
    kernel = stats.gaussian_kde(values, bw_method='silverman')
    kdeOutputArray = numpy.reshape(kernel(positions).T, X.shape)

    #Calculate the mean
    summ = 0
    count = 0
    for x in range (0, len(kdeOutputArray)):
        for y in range (0, len(kdeOutputArray[0])):
            summ = summ+kdeOutputArray[x][y]
            count = count+1

    mean = summ/count

    #Turn the points on in the grid
    a = numpy.zeros((len(kdeOutputArray), len(kdeOutputArray[0])), dtype=int)
    for x in range (0, len(kdeOutputArray)):
        for y in range (0, len(kdeOutputArray[0])):
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