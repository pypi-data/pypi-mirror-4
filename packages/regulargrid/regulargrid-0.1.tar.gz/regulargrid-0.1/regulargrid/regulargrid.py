import scipy
import numpy
import itertools

class RegularGrid(object):
	def __init__(self, limits, breaks, values):
		assert len(breaks) == len(limits), [len(breaks), len(limits)]
		
		gridall = []
		j = 0
		for i, (l, b) in enumerate(zip(limits, breaks)):
			assert numpy.all(b > l[0]), [b, l[0]]
			assert numpy.all(b < l[1]), [b, l[1]]
			grid = numpy.array([l[0]] + list(b) + [l[1]])
			gridall.append(grid)
			assert numpy.all(grid[1:] > grid[:-1]), 'breaks need to be ascending'
		self.grid = gridall
		assert values.shape == tuple([len(b)+2 for b in breaks]), [values.shape, [len(b)+2 for b in breaks]]
		#assert len(values) == numpy.product([len(b)+2 for b in breaks])
		self.values = values
	
	def __call__(self, pos):
		# find relevant edges between which pos is situated
		indices = []
		edge_values = []
		# compute distance to lower edge in unity units
		y = []
		for p, breaks in zip(pos, self.grid):
			i = numpy.searchsorted(breaks, p) - 1
			if i == -1:
				assert p == breaks[0], (p, breaks[0])
				# got the last break point, but we don't want that
				i = 0

			indices.append(i)
			y.append((p - breaks[i]) / (breaks[i+1] - breaks[i]))
		
		# find relevant values
		# each i and i+1 represents a edge
		edges = itertools.product(*[[i, i+1] for i in indices])
		value = 0.
		for edge_indices in edges:
			#j = 0 # addressing of grid
			weight = 1.
			#for ei, i, breaks, yi in zip(edge_indices, indices, self.grid, y):
				#j = j * len(breaks) + ei
			for ei, i, yi in zip(edge_indices, indices, y):
				weight *= (1 - yi) if ei == i else yi
			value += self.values[edge_indices] * weight
		return value
	
