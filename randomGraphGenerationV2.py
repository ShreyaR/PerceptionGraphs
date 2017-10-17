from random import uniform, choice
from pprint import pprint

class ProblemInstance:

	def __init__(self, n, graph_density, num_of_workers, treeChildren):

		self.graphEdges = []
		self.graph = {i:[] for i in xrange(n)}
		self.bidirectionalEdges = []
		self.difficulties = {}
		siblings = {i:[] for i in xrange(n)}

		# Create tree structure

		availableNodes = range(1,n)

		for i in xrange(n):
			numberOfChildren = choice(range(1, treeChildren))
			for j in availableNodes[:numberOfChildren]:
				self.graphEdges.append((i,j))
				self.bidirectionalEdges.append((i,j))
				self.bidirectionalEdges.append((j,i))
				self.graph[i].append(j)
				self.difficulties[(i,j)] = uniform(0,1)
			siblings[i] += availableNodes[:numberOfChildren]
			availableNodes = availableNodes[numberOfChildren:]

			for j in xrange(len(siblings[i])):
				for k in range(j+1, len(siblings[i])):
					# prob = uniform(0,1)
					# if prob>graph_density:
					node1 = siblings[i][j]
					node2 = siblings[i][k]
					self.bidirectionalEdges.append((node1,node2))
					self.bidirectionalEdges.append((node2,node1))
					if self.difficulties[(i,node1)]<self.difficulties[(i,node2)]:
						self.graphEdges.append((node1,node2))
						self.graph[node1].append(node2)
						self.difficulties[(node1,node2)] = uniform(0, 
							self.difficulties[(i,node2)])
					else:
						self.graphEdges.append((node2,node1))
						self.graph[node2].append(node1)
						self.difficulties[(node2,node1)] = uniform(0, 
							self.difficulties[(i,node1)])


		self.observations = {e:[] for e in self.bidirectionalEdges}
		self.assignWorkerResponses(num_of_workers)

		return

	def assignWorkerResponses(self, num_of_workers):
		#Assume each worker attempts each edge

		for w in xrange(num_of_workers):
			for e in self.graphEdges:
				diff = self.difficulties[e]
				accuracy = diff
				coin_toss = uniform(0,1)
				if coin_toss <= accuracy:
					self.observations[e].append(w)
				else:
					self.observations[(e[1],e[0])].append(w)
		return
