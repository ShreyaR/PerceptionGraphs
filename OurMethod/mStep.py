from cvxopt import solvers, matrix, log
from generateConstraints import constraints
from randomGraphGenerator import ProblemInstance
from random import uniform

class mStep:

	def __init__(self, undirGraph, dirEdges, observations):
		"""
		Input Parameters:
		-----------------------
		undirGraph: dictionary representing undirected graph. The keys are
			nodes, and the values are lists of nodes.
		dirEdges: set of tuples, where each tuple is a directed edge. 1st
			element of tuple is source node, and 2nd element is sink node.
		observations: given by workers when asked to provide directions of
			edges. Represented as a dictionary. Keys are directed edge tuples,
			and values are lists of workers who voted for that directed edge.
		"""
		self.undirG = undirGraph
		self.dirEdges = dirEdges
		self.observations = observations
		probConstraints= constraints(undirGraph, dirEdges)
		self.G, self.h, self.constraintVariablesToEdges = (probConstraints.G, 
			probConstraints.h, probConstraints.constraintVariablesToEdges)


		for i in xrange(19):
			print min(self.G[:,i]), max(self.G[:,i])

		# self.G = self.G.astype(double)
		# self.h = self.h.astype(double)

		self.n = (len(self.constraintVariablesToEdges) + 
			len(probConstraints.constraintVariablesToPseudoEdges))

		self.performMStep()

	def getObjectiveFuncValue(self, x):
		"""
		"""

		logLikelihood = 0
		derivativeOfLL = matrix(0, (1, self.n), 'd')

		# for edge in self.dirEdges:
		for k,v in self.constraintVariablesToEdges.items():
			edge = v
			reverseEdge = (edge[1], edge[0])
			
			difficulty = x[k]

			logLikelihood += ( len(self.observations[edge])*log(difficulty)
				+ len(self.observations[reverseEdge])*log(1-difficulty) )

			derivativeOfLL[0,k] = (len(self.observations[edge])/difficulty
				- len(self.observations[reverseEdge])/(1.0-difficulty) )

		return matrix(logLikelihood,(1,1)), derivativeOfLL

	def getH(self, x, z):

		H = matrix(0, (self.n, self.n), 'd')

		for k,v in self.constraintVariablesToEdges.items():
			edge = v
			reverseEdge = (edge[1], edge[0])
			
			difficulty = x[k]

			H[k,k] -= ( len(self.observations[edge])/(difficulty**2)
				+ len(self.observations[reverseEdge])/((1-difficulty)**2) )

		return z[0,0]*H


	def performMStep(self):

		def F(x=None, z=None):
			if x is None:
				return (0, matrix(0.99, (self.n,1)))

			if max(self.G*x - self.h) > 0:
				return None

			LL, deltaLL = self.getObjectiveFuncValue(x)

			if z is None:
				return LL, deltaLL

			H = self.getH(x,z)
			print LL.size
			print deltaLL.size
			print H.size

			return LL, deltaLL, H

		A = matrix(0, (1, self.n), 'd')
		b = matrix(0, (1,1), 'd')

		print A.size
		print b.size
		print self.G.size
		print self.h.size

		return solvers.cp(F, A=A, b=b, G=self.G, h=self.h)['x']


graph =  {'a':['b', 'c'],
		'b':['a', 'j', 'c', 'e', 'f'],
		'c':['a', 'e', 'h', 'j', 'b'],
		'e':['c', 'b', 'i'],
		'h':['c', 'f'],
		'j':['c', 'b'],
		'f':['b', 'h', 'd', 'i'],
		'd':['f'],
		'i':['e', 'f']}
directedEdges = [
				('a', 'b'),
				('a', 'c'),
				('b', 'c'),
				('b', 'j'),
				('c', 'j'),
				('b', 'e'),
				('c', 'e'),
				('b', 'f'),
				('f', 'i'),
				('i', 'e'),
				('f', 'h'),
				('h', 'c'),
				('f', 'd')
				]

observations = {}

numWorkers = 5
for e in directedEdges:
	reverseE = (e[1], e[0])

	observations[e] = []
	observations[reverseE] = []
	
	for i in xrange(numWorkers):
		if uniform(0,1) < 0.5:
			observations[e].append(i)
		else:
			observations[reverseE].append(i)

test = mStep(graph, directedEdges, observations)

# test = constraints(graph, directedEdges)
# print(test.G)
# print(test.h)