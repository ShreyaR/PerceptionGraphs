from random import uniform, choice, seed, random
from pprint import pprint

class ProblemInstance:

	def __init__(self, n, graph_density, num_of_workers, treeChildren):
		"""
		:param n: Number of nodes in the graph
		:param graph_density: ?
		:param num_of_workers: Number of workers that attempt direction prediction in graph
		:param treeChildren: Maximum number of children that a node can have.
		:return: NULL
		"""

		self.directedEdgeList = [] #List of all directed edges in the graph, where each edge is represented as a tuple
		self.undirectedEdgeList = [] #List of all undirected edges. So both (i,j), (j,i) present in the list.
		self.dirGraph = {i:[] for i in xrange(n)} #Directed graph represented as dictionary.
		self.undirGraph = {i:[] for i in xrange(n)} #Undirected graph represented as dictionary.
		self.easiness = {} #Dictionary, where keys=directed edges, values=difficulty value between 0 and 1.
		siblings = {i:[] for i in xrange(n)}

		availableNodes = range(1,n)

		# seedval = int(random()*10000)
		# seedval = 8525
		# print seedval
		# seed(seedval)

		# Create tree structure
		for i in xrange(n):
			numberOfChildren = choice(range(1, treeChildren))
			for j in availableNodes[:numberOfChildren]:
				self.directedEdgeList.append((i,j))
				self.undirectedEdgeList.append((i,j))
				self.undirectedEdgeList.append((j,i))
				self.dirGraph[i].append(j)
				self.undirGraph[i].append(j)
				self.undirGraph[j].append(i)
				self.easiness[(i,j)] = uniform(0.5,1)
			siblings[i] += availableNodes[:numberOfChildren]
			availableNodes = availableNodes[numberOfChildren:]

			# Creating loop edges
			for j in xrange(len(siblings[i])):
				for k in range(j+1, len(siblings[i])):
					# prob = uniform(0,1)
					# if prob>graph_density:
					node1 = siblings[i][j]
					node2 = siblings[i][k]
					self.undirectedEdgeList.append((node1,node2))
					self.undirectedEdgeList.append((node2,node1))
					self.undirGraph[node1].append(node2)
					self.undirGraph[node2].append(node1)
					if self.easiness[(i,node1)]<self.easiness[(i,node2)]:
						self.directedEdgeList.append((node1,node2))
						self.dirGraph[node1].append(node2)
						self.easiness[(node1,node2)] = uniform(self.easiness[(i,node1)],
							self.easiness[(i,node2)])
					else:
						self.directedEdgeList.append((node2,node1))
						self.dirGraph[node2].append(node1)
						self.easiness[(node2,node1)] = uniform(self.easiness[(i,node2)],
							self.easiness[(i,node1)])

		self.observations = {e:[] for e in self.undirectedEdgeList}
		self.assignWorkerResponses(num_of_workers)

		return

	def assignWorkerResponses(self, num_of_workers):
		#Assume each worker attempts each edge

		for w in xrange(num_of_workers):
			for e in self.directedEdgeList:
				accuracy = self.easiness[e]
				coin_toss = uniform(0,1)
				if coin_toss <= accuracy:
					self.observations[e].append(w)
				else:
					self.observations[(e[1],e[0])].append(w)
		return
