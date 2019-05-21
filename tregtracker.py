import numpy as np
import matplotlib.pyplot as plt



def return_center (x,y):
    sumx = 0.0
    sumy = 0.0

    for n in x:
        sumx += n

    for n in y:
        sumy += n

    centerx = sumx / len(x)
    centery = sumy / len(y)
    coords = {"x": centerx, "y": centery}
    return coords

def find_object (array, num):
    allx = []
    ally = []
    arrayrows = len(array)
    arraycolumns = len(array[0])

    for x in range(arraycolumns):
        for y in range(arrayrows):
            if array[x][y] == num:
                allx.append(x)
                ally.append(y)

    return allx,ally


def returnuniqueobjects (array):

    list = np.unique(array)
    list = list.tolist()
    if 0 in list:
        list.remove(0)
    return list


def centersfortimeslice(array):

    timeslicecenters = {}
    listOfObjects = returnuniqueobjects(array)

    for value in listOfObjects:
        x, y = find_object(array, value)
        center = return_center(x, y)
        timeslicecenters[value] = center
    return timeslicecenters

def main():
    timeslices = {}
    timeslice1  = np.array([[2, 2, 0], [0, 0, 0], [0, 1, 1]])
    timeslice2 = np.array([[2, 2, 2], [0, 0, 0], [0, 1, 1]])

    timeslices["1"] = timeslice1
    timeslices["2"] = timeslice2

    for ts in timeslices.keys():
        values = centersfortimeslice(timeslices[ts])
        print values
        for i in values.keys():
            plt.scatter(values[i]['x'], values[i]['y'])
            plt.annotate(str(i) + " slice" + str(ts), (values[i]['x'],  values[i]['y']))

    plt.show()


main()
