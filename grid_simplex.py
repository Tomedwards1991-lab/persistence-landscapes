import numpy
import dionysus
import matplotlib.pyplot as plt


class grid_simplex:
    def __init__(self, num_x, num_y):
        self.num_x = num_x
        self.num_y = num_y
        del num_x, num_y

        self.simplices = []
        self.simplex_active = []

        self.xy_2_simplex = dict()  # map from (x,y) tuples to integers.
        self.simplex_2_xy = dict()  # map from integers to (x,y) tuples.

        self.construct_simplex()

        return None

    def construct_simplex(self):
        # Add 0-simplices
        count = 0
        for j in range(self.num_y):
            for i in range(self.num_x):
                self.simplices.append(dionysus.Simplex([count]))
                self.xy_2_simplex[(i, j)] = count
                self.simplex_2_xy[count] = (i, j)
                count = count + 1

        # Add 1-simplices
        for j in range(self.num_y - 1):
            for i in range(self.num_x - 1):
                self.simplices.append(dionysus.Simplex([self.xy_2_simplex[(i, j)], self.xy_2_simplex[(i + 1, j)]]))
                self.simplices.append(dionysus.Simplex([self.xy_2_simplex[(i, j)], self.xy_2_simplex[(i, j + 1)]]))
                self.simplices.append(dionysus.Simplex([self.xy_2_simplex[(i, j)], self.xy_2_simplex[(i + 1, j + 1)]]))

        i = self.num_x - 1
        for j in range(self.num_y - 1):
            self.simplices.append(dionysus.Simplex([self.xy_2_simplex[(i, j)], self.xy_2_simplex[(i, j + 1)]]))

        j = self.num_y - 1
        for i in range(self.num_x - 1):
            self.simplices.append(dionysus.Simplex([self.xy_2_simplex[(i, j)], self.xy_2_simplex[(i + 1, j)]]))

        # Add 2-simplices
        for j in range(self.num_y - 1):
            for i in range(self.num_x - 1):
                self.simplices.append(dionysus.Simplex(
                    [self.xy_2_simplex[(i, j)], self.xy_2_simplex[(i + 1, j)], self.xy_2_simplex[(i + 1, j + 1)]]))
                self.simplices.append(dionysus.Simplex(
                    [self.xy_2_simplex[(i, j)], self.xy_2_simplex[(i, j + 1)], self.xy_2_simplex[(i + 1, j + 1)]]))

        self.simplex_active = [0] * len(self.simplices)

    def update_active_simplex(self, active):
        if (active.shape[0] != self.num_x or active.shape[1] != self.num_y):
            print "Incorrect active array size."
            return

        self.simplex_active = [0] * len(self.simplices)
        for i in range(len(self.simplices)):  # For each simplex.
            dv = [active[self.simplex_2_xy[v][0], self.simplex_2_xy[v][1]] for v in self.simplices[i].vertices]
            if (min(dv) == 1):
                self.simplex_active[i] = 1

    def plot_active_simplex(self):
        # Plot 2-simplices
        for i in range(len(self.simplices)):
            if (self.simplices[i].dimension() == 2):
                vl = [v for v in self.simplices[i].vertices]
                if (all([self.simplex_active[v] for v in vl])):
                    x0 = self.simplex_2_xy[vl[0]][0]
                    y0 = self.simplex_2_xy[vl[0]][1]
                    x1 = self.simplex_2_xy[vl[1]][0]
                    y1 = self.simplex_2_xy[vl[1]][1]
                    x2 = self.simplex_2_xy[vl[2]][0]
                    y2 = self.simplex_2_xy[vl[2]][1]
                    plt.fill([x0, x1, x2], [y0, y1, y2], 'g', alpha=0.5)

        # Plot 1-simplices
        for i in range(len(self.simplices)):
            if (self.simplices[i].dimension() == 1):
                vl = [v for v in self.simplices[i].vertices]
                if (all([self.simplex_active[v] for v in vl])):
                    x0 = self.simplex_2_xy[vl[0]][0]
                    y0 = self.simplex_2_xy[vl[0]][1]
                    x1 = self.simplex_2_xy[vl[1]][0]
                    y1 = self.simplex_2_xy[vl[1]][1]
                    plt.plot([x0, x1], [y0, y1], 'b', linewidth=3.5)

        # Plot 0-simplices
        for i in range(len(self.simplices)):
            if (self.simplices[i].dimension() == 0):
                vl = [v for v in self.simplices[i].vertices]
                if (all([self.simplex_active[v] for v in vl])):
                    x = self.simplex_2_xy[vl[0]][0]
                    y = self.simplex_2_xy[vl[0]][1]
                    plt.plot(x, y, 'ro', markersize=8)

        plt.axis([0 - self.num_x / 50., self.num_x - 1 + self.num_x / 50., 0 - self.num_y / 50.,
                  self.num_y - 1 + self.num_y / 50.])
        plt.show()