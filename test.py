from EMWithCycleBreaking.randomGraphGenerator import ProblemInstance
from EMWithCycleBreaking.main import GraphEM as Baseline
from OurMethod.main import GraphEM as OurMethod

numWorkers = 20
# for numNodes in [5, 10, 15, 20, 25]:
for numNodes in [5, 10, 15, 20, 50]:

	for c in xrange(10):

		pi = ProblemInstance(numNodes, 0.5, 20)

		undirected_graph = {k:[x for x in pi.graph[k]] for k in pi.graph.keys()}
		for k in sorted(undirected_graph.keys()):
			for v in undirected_graph[k]:
				undirected_graph[v].append(k)

		flag = True
		try:
			graph_em2 = OurMethod(False, numNodes, pi.bidirectionalEdges, numWorkers, undirected_graph, pi.observations, pi.graph, pi.difficulties, numNodes, c)
		except TypeError:
			flag = False
			continue
		
		if flag:
			graph_em1 = Baseline(False, numNodes, pi.bidirectionalEdges, numWorkers, undirected_graph, pi.observations, pi.graph, pi.difficulties, numNodes, c)