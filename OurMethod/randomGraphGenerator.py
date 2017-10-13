from random import uniform

class ProblemInstance:

	def __init__(self, n, graph_density, num_of_workers):

		self.graphEdges = []
		self.graph = {i:[] for i in xrange(n)}

		for i in xrange(n):
			for j in xrange(i+1, n):
				rand = uniform(0,1)
				if rand <= graph_density:
					self.graph[i].append(j)
					self.graphEdges.append((i,j))

		self.difficulties = {e:0 for e in self.graphEdges}
		self.assignEdgeDifficulties()

		self.bidirectionalEdges = []
		[self.bidirectionalEdges.append((e[1], e[0])) for e in self.graphEdges]
		[self.bidirectionalEdges.append(e) for e in self.graphEdges]
		
		self.observations = {e:[] for e in self.bidirectionalEdges}
		self.assignWorkerResponses(num_of_workers)

		return

	def assignEdgeDifficulties(self):

		for e in self.graphEdges:
			self.difficulties[e] = uniform(0,1)

		return

	def assignWorkerResponses(self, num_of_workers):
		#Assume each worker attempts each edge

		for w in xrange(num_of_workers):
			for e in self.graphEdges:
				diff = self.difficulties[e]
				accuracy = 1.0/(1+diff)
				coin_toss = uniform(0,1)
				if coin_toss <= accuracy:
					self.observations[e].append(w)
				else:
					self.observations[(e[1],e[0])].append(w)
		return
