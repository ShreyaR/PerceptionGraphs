from cvxopt import solvers, matrix, log
from generateConstraints import constraints
from scipy.optimize import minimize
import numpy as np
from pprint import pprint

class mStep:

	def __init__(self, undirGraph, dirEdges, observations):
		"""
		Input Parameters:
		-----------------------
		undirGraph: dictionary representing undirected graph. The keys are
			nodes, and the values are lists of nodes.
		dirEdges: list of tuples, where each tuple is a directed edge. 1st
			element of tuple is source node, and 2nd element is sink node.
		observations: given by workers when asked to provide directions of
			edges. Represented as a dictionary. Keys are directed edge tuples,
			and values are lists of workers who voted for that directed edge.
		"""
		self.undirG = undirGraph
		self.dirEdges = dirEdges
		self.observations = observations
		probConstraints = constraints(undirGraph, dirEdges)
		self.G, self.h, self.constraintVariablesToEdges = (np.array(probConstraints.G),
														   np.array(probConstraints.h),
														   probConstraints.constraintVariablesToEdges)

		self.numConstraints = probConstraints.numTripletConstraints
		self.n = (len(self.constraintVariablesToEdges) +
				  len(probConstraints.constraintVariablesToPseudoEdges))

		#Constraints
		self.constraints = self.getConstraints()

		#Bounds
		self.bounds = [(0,1) for i in xrange(len(self.constraintVariablesToEdges))]

		d = self.performMStep()

		self.difficulties = {}

		for k, v in self.constraintVariablesToEdges.items():
			self.difficulties[v] = d.x[k]
			self.difficulties[(v[1], v[0])] = d.x[k]

	def getConstraints(self):

		constraints = []
		for i in xrange(self.numConstraints):
			c = {'type': 'ineq'}
			pos_ind = np.where(self.G[i,:]==-1)[0][0]
			neg_ind = np.where(self.G[i,:]==1)[0][0]
			c['fun'] = lambda x: x[pos_ind] - x[neg_ind]
			constraints.append(c)

		return constraints

	def performMStep(self):

		def getObjectiveFuncValue(x):
			logLikelihood = 0
			for k, v in self.constraintVariablesToEdges.items():
				edge = v
				reverseEdge = (edge[1], edge[0])
				difficulty = x[k]
				if difficulty == 0:
					difficulty = 0.0001
				if difficulty == 1:
					difficulty = 0.9999
				logLikelihood -= (len(self.observations[edge]) * log(difficulty)
								  + len(self.observations[reverseEdge]) * log(1 - difficulty))

			return logLikelihood

		def getJacobian(x):
			derivativeOfLL = np.zeros(self.n)
			for k, v in self.constraintVariablesToEdges.items():
				edge = v
				reverseEdge = (edge[1], edge[0])
				difficulty = x[k]
				if difficulty == 0:
					difficulty = 0.0001
				if difficulty == 1:
					difficulty = 0.9999
				derivativeOfLL[k] = -1 * (len(self.observations[edge]) / difficulty
										  - len(self.observations[reverseEdge]) / (1.0 - difficulty))
			return derivativeOfLL

		return minimize(getObjectiveFuncValue,
						np.ones(self.n)*0.5,
						method='SLSQP',
						jac=getJacobian,
						bounds=self.bounds,
						constraints=self.constraints,
						options={'disp':False, 'maxiter':20})
