import numpy
import grid_simplex
import zig_zag_homology

# Initialize grid of points
grid_simplex_object = grid_simplex.grid_simplex(5, 10) # a gird of size 5 by 10
zig_zag_homology_object = zig_zag_homology.zig_zag_homology(grid_simplex_object.simplices)


# For times 1, 2 and 3 turn on and off different points in the grid. Plot grid at each time step.
a = numpy.zeros((5,10), dtype=int)
a[2,5] = 1
a[3,5] = 1
a[2,4] = 1
a[3,4] = 1
grid_simplex_object.update_active_simplex(a)
time = 1
zig_zag_homology_object.update_simplex_active(grid_simplex_object.simplex_active, time)
grid_simplex_object.plot_active_simplex()


a = numpy.zeros((5,10), dtype=int)
a[1,9] = 1
a[2,5] = 1
a[3,5] = 1
a[2,4] = 1
a[2,6] = 1
grid_simplex_object.update_active_simplex(a)
time = 2
zig_zag_homology_object.update_simplex_active(grid_simplex_object.simplex_active, time)
grid_simplex_object.plot_active_simplex()

a = numpy.zeros((5,10), dtype=int)
a[2,5] = 1
a[3,5] = 1
a[2,4] = 1
a[2,6] = 1
a[2,7] = 1
a[3,7] = 1
a[4,7] = 1
a[4,6] = 1
grid_simplex_object.update_active_simplex(a)
time = 3
zig_zag_homology_object.update_simplex_active(grid_simplex_object.simplex_active, time)
grid_simplex_object.plot_active_simplex()


# When fihished turn off all points in the grid.
zig_zag_homology_object.remove_all_simplex()
zig_zag_homology_object.sort_persistence()


# Print results
print "zero_dim_persistence: ", zig_zag_homology_object.zero_dim_persistence
print "one_dim_persistence: ", zig_zag_homology_object.one_dim_persistence