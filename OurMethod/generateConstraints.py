from cvxopt import solvers, matrix, spdiag, log

from pprint import pprint

class constraints:

	def __init__(self, undirG, dirG, undirEdges, dirEdges):
		"""
		undirG: Undirected underlying graph. Useful for identifying cycles or
			loops in the graph.
		dirG: Directed graph obtained from the E step of the algorithm. Useful
			for defining constraints over the loop.
		"""

		self.undirG = undirG
		self.dirG = dirG
		self.undirEdges = undirEdges
		self.dirEdges = dirEdges

		# loops = self.getLoops(self.undirG)

	def getLoops(self, graph):
		"""
		Input Parameters:
		-----------------------
		graph: undirected graph
		Output Parameters:
		-----------------------
		cycles: List of sets, where each set contains edges (as tuples) that
			form a cycle.
		"""
		cycles = []

		# Initializing T and X
		tree = {}
		examinedEdges = set()
		unexaminedNodes = [x for x in graph.keys()]

		# Starting while loop
		root = unexaminedNodes[0]
		tree[unexaminedNodes[0]] = []
		treeNodes = [unexaminedNodes[0]]
		currentNode = unexaminedNodes[0]

		while(True):

			for e in graph[currentNode]:

				if (currentNode, e) in examinedEdges:
					continue

				if e in tree.keys(): # find cycle path
					pathToV1 = self.recursiveFindPath(tree, root, e, {root})
					pathToV2 = self.recursiveFindPath(tree, root, currentNode,
						{root})
					pathToV1.symmetric_difference_update(pathToV2)
					pathToV1.add((currentNode, e))
					cycles.append(pathToV1)

				else:
					tree[currentNode].append(e)
					tree[e] = [currentNode]
					treeNodes.append(e)

				examinedEdges.add((currentNode, e))
				examinedEdges.add((e, currentNode))

			treeNodes.remove(currentNode)
			unexaminedNodes.remove(currentNode)

			if len(set(unexaminedNodes).intersection(set(treeNodes)))==0:
				break

			currentNode = treeNodes[-1]

		return cycles

	def recursiveFindPath(self, tree, currentRoot, vertex, visitedNodes):

		if vertex==currentRoot:
			return set()

		for child in tree[currentRoot]:

			if child in visitedNodes:
				continue

			if child==vertex:
				return {(currentRoot, vertex)}
			else:
				visitedNodes.add(child)
				subTreeResult = self.recursiveFindPath(tree, child, vertex, 
					visitedNodes)

				if subTreeResult==False:
					continue
				else:
					subTreeResult.add((currentRoot,child))
					return subTreeResult

		return False

	def getConstraints(self, cycles, directedEdges):
		"""
		Input Parameters:
		-----------------------
		cycles: output of the self.getLoops function
		directedEdges: a list of tuples of directed edges in no particular
			order. For each edge, the first node in tuple is the source, and
			the second node is the sink.
		Return Values:
		-----------------------
		constraints: Set of tuples, where each tuple represents a constraint.
			For a constraint like e_1 < e_2, the tuple will be (e_1, e_2), 
			where e_1 and e_2 are the indices of edges. For the actual edge
			represented by the index, look up either 
			inverseEdgesToConstraintVariables or 
			inversePsuedoEdgesToConstraintVariables.
		inverseEdgesToConstraintVariables: Maps constraint variable to directed
			edge tuple.
		inversePsuedoEdgesToConstraintVariables: Maps comstraint variable to
			directed psuedo-edge tuple.
		"""
		

		edgesToConstraintVariables = {directedEdges[i]:i for i in 
			xrange(len(directedEdges))}

		psuedoEdgesToConstraintVariables = {}
		constraints = set()
		psuedoEdges = {}

		for loop in cycles:
			
			# Find source and sink of loop.

			vertices = set()
			for e in loop:
				vertices.add(e[0])
				vertices.add(e[1])

			miniGraph = {x:[] for x in vertices}

			for e in loop:
				if e in directedEdges:
					miniGraph[e[0]].append(e[1])
				else:
					miniGraph[e[1]].append(e[0])

			sink = 0
			source = 0

			for k,v in miniGraph.items():
				if len(v)==0:
					sink = k
				if len(v)==2:
					source = k

			# Get both parallel paths of cycle from source to sink.

			parallelPath1 = [source]
			parallelPath2 = [source]

			nextNode1 = miniGraph[source][0]
			parallelPath1.append(nextNode1)
			while(nextNode1!=sink):
				nextNode1 = miniGraph[nextNode1][0]
				parallelPath1.append(nextNode1)

			nextNode2 = miniGraph[source][1]
			parallelPath2.append(nextNode2)
			while(nextNode2!=sink):
				nextNode2 = miniGraph[nextNode2][0]
				parallelPath2.append(nextNode2)

			# Create triplet constraints for loops

			constraintsFromPath1 = len(parallelPath1) - 2
			constraintsFromPath2 = len(parallelPath2) - 2

			for i in xrange(constraintsFromPath1):
				tripletEdge = (parallelPath1[0], parallelPath1[i+2])
				edge1 = (parallelPath1[0], parallelPath1[i+1])
				if edge1 in directedEdges:
					edge1 = edgesToConstraintVariables[edge1]
				else:
					edge1 = psuedoEdgesToConstraintVariables[edge1]
				edge2 = edgesToConstraintVariables[(parallelPath1[i+1], 
					parallelPath1[i+2])]
				if tripletEdge not in directedEdges:
					if tripletEdge not in psuedoEdges:
						edgeInd = len(psuedoEdges)
						constraintVarInd = (len(directedEdges) + 
							len(psuedoEdges))
						psuedoEdges[tripletEdge] = "e%d" % (edgeInd)
						psuedoEdgesToConstraintVariables[tripletEdge] = constraintVarInd
					constraints.add((edge1, 
						psuedoEdgesToConstraintVariables[tripletEdge]))
					constraints.add((edge2,
						psuedoEdgesToConstraintVariables[tripletEdge]))
				else:
					constraints.add((edge1, 
						edgesToConstraintVariables[tripletEdge]))
					constraints.add((edge2, 
						edgesToConstraintVariables[tripletEdge]))

			for i in xrange(constraintsFromPath2):
				tripletEdge = (parallelPath2[0], parallelPath2[i+2])
				edge1 = (parallelPath2[0], parallelPath2[i+1])
				if edge1 in directedEdges:
					edge1 = edgesToConstraintVariables[edge1]
				else:
					edge1 = psuedoEdgesToConstraintVariables[edge1]
				edge2 = edgesToConstraintVariables[(parallelPath2[i+1], 
					parallelPath2[i+2])]
				if tripletEdge not in directedEdges:
					if tripletEdge not in psuedoEdges:
						edgeInd = len(psuedoEdges)
						constraintVarInd = (len(directedEdges) + 
							len(psuedoEdges))
						psuedoEdges[tripletEdge] = "e%d" % (edgeInd)
						psuedoEdgesToConstraintVariables[tripletEdge] = constraintVarInd
					constraints.add((edge1, 
						psuedoEdgesToConstraintVariables[tripletEdge]))
					constraints.add((edge2,
						psuedoEdgesToConstraintVariables[tripletEdge]))
				else:
					constraints.add((edge1, 
						edgesToConstraintVariables[tripletEdge]))
					constraints.add((edge2, 
						edgesToConstraintVariables[tripletEdge]))

		return (constraints, self.inverseOne2OneMap(edgesToConstraintVariables), 
			self.inverseOne2OneMap(psuedoEdgesToConstraintVariables))

	def inverseOne2OneMap(self, map):
		inverseMap = {}
		for k,v in map.items():
			inverseMap[v] = k
		return inverseMap

	def getAbMatrices(self, constraintSet, numberOfEdges):
		"""
		Input Parameters:
		-----------------------
		constraintSet: 1st return value of the getConstraints function. 
		numberOfEdges: Total number of true and psuedo directed edges in the
			constraintSet.

		Output Parameters:
		-----------------------
		G, h: GX <= h. Of type cvx matrix.
		"""
		G = matrix(0, (len(constraintSet),numberOfEdges))
		h = matrix(0, (len(constraintSet), 1))

		count = 0
		for i in constraintSet:
			G[count, i[0]] = 1
			G[count, i[1]] = -1
			count += 1

		print(G)
		print(h)

		return G, h



test = constraints(0, 0, 0, 0)
tree = {'a':['b', 'c'],
		'b':['a'],
		'c':['a', 'e', 'h', 'j'],
		'e':['c'],
		'h':['c', 'f'],
		'j':['c'],
		'f':['h', 'd', 'i'],
		'd':['f'],
		'i':['f']}
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

# print test.recursiveFindPath(tree, 'a', 'f', {'a'})
cycles = test.getLoops(graph)
cSet, x1, x2 = test.getConstraints(cycles, directedEdges)
test.getAbMatrices(cSet, len(x1)+len(x2))

# print cycles
# print len(cycles)
