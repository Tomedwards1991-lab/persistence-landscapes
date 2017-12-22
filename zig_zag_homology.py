import dionysus
import numpy


class zig_zag_homology:
    def __init__(self, st):
        self.simplices = st
        del st

        self.simplex_active = [0] * (len(self.simplices))

        self.simplex_zz_index = dict()
        for s in self.simplices:
            self.simplex_zz_index[s] = None

        self.zz = dionysus.ZigzagPersistence()

        self.zero_dim_persistence = []
        self.one_dim_persistence = []

    def update_simplex_active(self, nsa, t):
        for i in range(len(nsa)):
            if ((self.simplex_active[i] == 0) and (nsa[i] == 1)):  # Add this simplex.
                s = self.simplices[i]
                sb = [self.simplex_zz_index[sbi] for sbi in s.boundary]
                ind, d = self.zz.add(sb, t)

                self.simplex_zz_index[s] = ind
                self.simplex_active[i] = 1

                if d is not None:  # Death
                    if (d != t):
                        print "Interval (A) (%d, %d)" % (d, t), ", Dimension (add) - ", s.dimension() - 1

                        if ((s.dimension() - 1) == 0):
                            self.zero_dim_persistence.append([d, t])
                        elif ((s.dimension() - 1) == 1):
                            self.one_dim_persistence.append([d, t])

        for i in range(len(nsa) - 1, -1, -1):
            if ((self.simplex_active[i] == 1) and (nsa[i] == 0)):  # Remove this simplex.
                s = self.simplices[i]
                d = self.zz.remove(self.simplex_zz_index[s], t)
                del self.simplex_zz_index[s]
                self.simplex_active[i] = 0

                if d is not None:  # Death
                    if (d != t):
                        print "Interval (R) (%s, %s)" % (d, t), ", Dimension (remove) - ", s.dimension()

                        if (s.dimension() == 0):
                            self.zero_dim_persistence.append([d, t])
                        elif (s.dimension() == 1):
                            self.one_dim_persistence.append([d, t])

    def remove_all_simplex(self):
        simplex_active_remove = [0] * (len(self.simplices))
        self.update_simplex_active(simplex_active_remove, float('Inf'))

    def sort_persistence(self):
        self.zero_dim_persistence.sort(key=lambda row: row[0])
        self.one_dim_persistence.sort(key=lambda row: row[0])
