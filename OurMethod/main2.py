__author__ = 'shreyarajpal'

from random import uniform, choice
from pprint import pprint
# from randomGraphGenerator import ProblemInstance
from generateConstraints import constraints
from mStep import mStep

# Add in documentation as you have more of it.

f = open('results_ourmethodv5.txt', 'w')


class GraphEM:
    def __init__(self, flag, n, edges, workers, graph, observations, trueDAG, trueDiff, numNodes, c):
        """Description of the class variables:
		self.n: Number of nodes in the graph
		self.edges: A list of undirected edges (represented as tuples) in the
			graph.
		self.workers: A set of worker indices.
		"""

        print "Our Method2", numNodes, c

        if flag:
            self.n = 0
            self.edges = []
            self.workers = set()
            graph = self.readGraph('graphSpecification.txt')
            observations = self.readObservations('observations.txt')

        else:
            self.n = n
            self.edges = edges
            self.workers = workers

        # print observations.keys()

        edgeDifficulty, new_graph = self.EM_v1(graph, observations)

        trueEdges = set()
        for k, v in trueDAG.items():
            for i in v:
                trueEdges.add((k, i))

        newEdges = set(new_graph.keys())

        f.write("%d, %.4f\n" % (n, len(newEdges.intersection(trueEdges)) / (1.0 * len(trueEdges))))
        print "Main 2", "%d, %.4f\n" % (n, len(newEdges.intersection(trueEdges)) / (1.0 * len(trueEdges)))

        return

    def readGraph(self, graphFile):
        """Reads the graph provided in the graphFile. The format of the graph
		file should be the following: The first line should contain the number
		of nodes (n) in the graph. Note that the nodes should be zero indexed,
		so that the actual node indices go up to (n-1). The n lines following
		the first should should contain a comma separated list of the nodes
		that share an edge with the node. For example, the following lines
		show a triangular graph:
		3
		1,2
		0,2
		0,1
		Input Args:-
		graphFile: the location of the input file.
		Output Args:-
		graphObj: Returns the graph object as a dictionary where key represents
			the node index, and the value is a set of neighbouring
			nodes.
		"""

        with open(graphFile) as f:
            self.n = int(f.readline().rstrip())
            graphObj = {i: [] for i in xrange(self.n)}

            for i in xrange(self.n):
                graphObj[i] = [int(x) for x in f.readline().rstrip().split(',')]
                [self.edges.append((i, x)) for x in graphObj[i]]

        return graphObj

    def readObservations(self, obsFile):
        """Reads fuzzy observations about the directions of the graph. The
		observations are specified in the following format: let an observation
		be generated by worker k (or the random noise variable k). The observ-
		ations provided by this worker should be written like:
		k, {from node-index}, {to node-index}
		Input Args:-
		obsFile: Path to observation file
		Output Args:-
		observations: A dicitionary with 2*m keys (m is the number of edges),
			where both directions of edges are present in the dicti-
			onary as a tuple of ({from node}, {to node}). The values
			are a list of of workers/random variables that produce
			that observation.
		"""



        observations = {}
        for e in self.edges:
            observations[e] = []
            observations[(e[1], e[0])] = []

        with open(obsFile) as f:
            for line in f:
                (worker, fromNode, toNode) = [int(x) for x in line.rstrip().split(',')]
                observations[(fromNode, toNode)].append(worker)
                self.workers.add(worker)

        return observations

    # def EM(self, graph, observations):
    # 	"""Performs the standard EM algorithm. In the E step, we estimate the
    # 	directions of the edges, and then perform cycle breaking. In the M
    # 	step, we re-estimate edge difficulties and worker skills.
    # 	Input Args:-
    # 	graph: Graph returned by the readGraph function.
    # 	observations: Observations returned by the readObseervations function.
    # 	Output Args:-
    # 	graph: The graph as a list of edge-tuples. Edges in the correct
    # 		direction.
    # 	workerError: A dictionary with key=workerID, and value=skill paramter.
    # 	edgeDifficulty: A dictionary with key=edge tuple, and value=difficulty
    # 		of that edge.
    # 	"""

    # 	# Initializing worker skill and edge difficulty.

    def Estep_v1(self, graph, observations, difficulties):
        """
		Error Function: Beronoulli trial, with easiness = d
		"""

        determined_edges = {}

        for e in self.edges:
            reverse_e = (e[1], e[0])
            if e in determined_edges.keys() or reverse_e in determined_edges.keys():
                continue
            d = difficulties[e]

            forward_prob = 1
            for x in observations[e]:
                forward_prob *= 1.0 * d
            for x in observations[reverse_e]:
                forward_prob *= 1.0 * (1 - d)

            backward_prob = 1
            for x in observations[reverse_e]:
                backward_prob *= 1.0 * d
            for x in observations[e]:
                backward_prob *= 1.0 * (1 - d)

            if forward_prob > backward_prob:
                determined_edges[e] = forward_prob * 1.0 / (forward_prob + backward_prob)
            else:
                determined_edges[reverse_e] = backward_prob * 1.0 / (forward_prob + backward_prob)

        # Cycle Breaking
        determined_edges = self.breakCycles(graph, determined_edges)
        # determined_edges = self.breakCycles2(determined_edges)

        return determined_edges

    def breakCycles(self, graph, determined_edges):

        # Find if cycles exist

        cs = constraints(graph)
        for loop in cs.loops:

            minigraphEdges = []

            # Check if cycle
            miniGraph = {}
            for e in loop:
                if e[0] not in miniGraph.keys():
                    miniGraph[e[0]] = []
                if e[1] not in miniGraph.keys():
                    miniGraph[e[1]] = []
                if e in determined_edges.keys():
                    miniGraph[e[0]].append(e[1])
                    minigraphEdges.append(e)
                else:
                    miniGraph[e[1]].append(e[0])
                    minigraphEdges.append((e[1], e[0]))

            flag = True

            for k, v in miniGraph.items():
                if len(v) != 1:
                    flag = False
                    break

            if flag:
                # print "Cycle"
                # print miniGraph

                # Break Cycle

                # minVal = 10
                # breakAwayEdge = 0
                # for e in minigraphEdges:
                # 	if determined_edges[e] < minVal:
                # 		breakAwayEdge = e
                # 		minVal = determined_edges[e]

                # print breakAwayEdge

                breakAwayEdge = choice(minigraphEdges)

                newVal = 1 - determined_edges[breakAwayEdge]

                del determined_edges[breakAwayEdge]
                determined_edges[(breakAwayEdge[1], breakAwayEdge[0])] = newVal

        return determined_edges

    def breakCycles2(self, determined_edges):

        sorted_edges = sorted(determined_edges, key=determined_edges.get)
        final_edges = {}

        while(True):
            if len(sorted_edges)==0:
                break

            edge = sorted_edges[-1]
            sorted_edges = sorted_edges[:-1]

            final_edges[edge] = determined_edges[edge]
            if not self.checkIfAcyclic(final_edges):
                reverse_edge = (edge[1], edge[0])
                del final_edges[edge]
                final_edges[reverse_edge] = 1 - determined_edges[edge]

        return final_edges


    def checkIfAcyclic(self, determined_edges):
        graph = self.graphFromEdges(determined_edges, directed=True)
        for i in xrange(self.n):
            if i not in graph.keys():
                graph[i] = []
        degrees = {k:len(v) for k,v in graph.items()}

        topological_sort = []


        while(True):
            if len(graph)==0:
                flag = True
                break

            min_degree_node = sorted(degrees, key=degrees.get)[0]

            if len(graph[min_degree_node])!=0:
                flag = False
                break

            topological_sort.append(min_degree_node)
            del graph[min_degree_node]
            for v in graph.values():
                if min_degree_node in v: v.remove(min_degree_node)

            degrees = {k:len(v) for k,v in graph.items()}

        return flag




    def graphFromEdges(self, edges, directed=True):

        graph = {}

        for e in edges:
            if e[0] not in graph.keys():
                graph[e[0]] = []
            graph[e[0]].append(e[1])

            if not directed:
                if e[1] not in graph.keys():
                    graph[e[1]] = []
                graph[e[1]].append(e[0])

        return graph



    # def Mstep_v1(self, directed_graph, observations):
    def Mstep_v1(self, undir_graph, directed_edges, observations):

        # print directed_graph, observations
        # return

        difficulties = mStep(undir_graph, directed_edges, observations)

        # difficulties = {}

        # for e in self.edges:
        # 	reverse_e = (e[1], e[0])

        # 	if e in directed_graph.keys():
        # 		true_side = e
        # 		false_side = reverse_e
        # 	else:
        # 		true_side = reverse_e
        # 		false_side = e

        # 	diff = (len(observations[true_side])+0.0001)*1.0/(len(observations[true_side])+len(observations[false_side]))
        # 	difficulties[true_side] = diff
        # 	difficulties[false_side] = diff

        return difficulties.difficulties

    def EM_v1(self, graph, observations):
        """Performs the standard EM algorithm.
		v1: The accuracy function is a function of difficulty only, and the
			is of the form 1/(1+d).
		In the E step, we estimate the directions of the edges, and then
		perform cycle breaking. In the M step, we re-estimate edge
		difficulties and worker skills.
		Input Args:-
		graph: Graph returned by the readGraph function.
		observations: Observations returned by the readObservations function.
		Output Args:-
		graph: The graph with edges in the correct direction. The format of
			the graph is similar to the input graph, except that each line
			index is the 'from' node, and only 'to' nodes are listed in each
			line.
		edgeDifficulty: A dictionary with key=edge tuple, and value=difficulty
			of that edge.
		"""

        # Initializing edge difficulty.
        edgeDifficulty = {x: uniform(0, 1) for x in self.edges}

        old_graph = 0
        iter = 0
        while (True):

            new_graph = self.Estep_v1(graph, observations, edgeDifficulty)
            print "E step"
            # edgeDifficulties = self.Mstep_v1(new_graph, observations)
            edgeDifficulties = self.Mstep_v1(graph, new_graph.keys(), observations)
            print "M step"

            if new_graph == old_graph:
                break
            else:
                old_graph = new_graph

            iter += 1

        return edgeDifficulty, new_graph

    # for w in [5, 10, 20, 100]:
    # for numNodes in [5, 10, 20, 50, 100]:
    # 	for c in xrange(10):
    # 		pi = ProblemInstance(numNodes, 0.5, 50)
    # 		undirected_graph = {k:[x for x in pi.graph[k]] for k in pi.graph.keys()}
    # 		for k in sorted(undirected_graph.keys()):
    # 			for v in undirected_graph[k]__:
    # 				undirected_graph[v].append(k)
    # 		graph_em = GraphEM(False, numNodes, pi.bidirectionalEdges, 50, undirected_graph, pi.observations, pi.graph, pi.difficulties)
    # graph_em = GraphEM(True, 0, 0, 0, 0, 0, 0, 0)

# pi = ProblemInstance(20, 0.5, 20)

# undirected_graph = {k:[x for x in pi.graph[k]] for k in pi.graph.keys()}
# for k in sorted(undirected_graph.keys()):
# 	for v in undirected_graph[k]:
# 		undirected_graph[v].append(k)

# graph_em = GraphEM(False, 20, pi.bidirectionalEdges, 20, undirected_graph, pi.observations, pi.graph, pi.difficulties, 20, 0)
