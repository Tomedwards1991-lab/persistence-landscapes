import math
import numpy
import grid_simplex
import zig_zag_homology
import csv
import subprocess
from scipy import stats
import pyproj
import matplotlib.pyplot as plt

# Read in the csv file and store the coordiantes in a list
l1 = []
l2 = []
yearL = []
new_list1 = []
new_list2 = []
new_yearL = []

# Initialize grid of points
grid_simplex_object = grid_simplex.grid_simplex(100, 100)
zig_zag_homology_object = zig_zag_homology.zig_zag_homology(grid_simplex_object.simplices)

directoryPath = '/Users/thomasedwards/Desktop/WorkPhDAT/spatial_temporal_topology_library/csvs'
file_list = subprocess.check_output(['find', directoryPath, '-name', '*.csv']).split('\n')[:-1]

for fileCSV in file_list:
    csvfile = open(fileCSV, 'rU')
    mycsv = csv.reader(csvfile)
    for row in mycsv:
        coord1 = row[22]
        coord2 = row[23]
        if (coord1 != "" and coord2 != ""):
            l1.append(coord1)
            l2.append(coord2)

    for item in l1:
        new_list1.append(float(item))

    for item in l2:
        new_list2.append(float(item))

    # Define projection for the British National Grid
    bng = pyproj.Proj(init='epsg:27700')

    # do british projection
    bx, by = bng(new_list1, new_list2)

    m1, m2 = bx, by

    xmin = min(m1)
    xmax = max(m1)
    ymin = min(m2)
    ymax = max(m2)

    # Apply KDE to the coordiantes and prinyt the results on a grid
    X, Y = numpy.mgrid[xmin:xmax:100j, ymin:ymax:100j]
    positions = numpy.vstack([X.ravel(), Y.ravel()])
    values = numpy.vstack([m1, m2])
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

    zig_zag_homology_object.update_simplex_active(grid_simplex_object.simplex_active, 3)
    grid_simplex_object.plot_active_simplex()

# When fihished turn off all points in the grid.
zig_zag_homology_object.remove_all_simplex()
zig_zag_homology_object.sort_persistence()

# Print results
print "zero_dim_persistence: ", zig_zag_homology_object.zero_dim_persistence
print "one_dim_persistence: ", zig_zag_homology_object.one_dim_persistence