from randomGraphGenerationV2 import ProblemInstance
from randomGraphGenerationV3 import ProblemInstance as ProblemInstance2
from EMWithCycleBreaking.main import GraphEM as Baseline
from OurMethod.main import GraphEM as OurMethod
from OurMethod.main3 import GraphEM as OurMethod3
from pprint import pprint
from OurMethod.generateConstraints import constraints
from random import random

numWorkers = 20
numNodes = 20
numChildren = 4

for numNodes, numChildren in zip([5,10,15,20,50], [3,3,4,5,8]):
# for numNodes, numChildren in zip([35], [6]):
# for numWorkers in [5, 10, 15, 20, 50, 100]:
# for numChildren in [4, 7, 10, 13, 16, 19]:
	# for c in xrange(5):
	for c in xrange(5):

		pi = ProblemInstance(numNodes, 0.5, 10, numChildren)
		pi2 = ProblemInstance2(numNodes, 0.5, 10, numChildren)
		# pprint(pi.dirGraph)
		# for k,v in pi.observations.items():
		# 	print("(%d, %d): %d" % (k[0], k[1], len(v)))
		#
		# pprint(pi.easiness)

		# seedval = int(random()*1000)
		seedval = 572
		# print seedval
		OurMethod(False, numNodes, pi.undirectedEdgeList, numWorkers, pi.undirGraph, pi.observations,
							 pi.dirGraph, pi.easiness, numNodes, c, seedval, 17)
		# break
		OurMethod3(False, numNodes, pi2.undirectedEdgeList, numWorkers, pi2.undirGraph, pi2.observations,
							 pi2.dirGraph, pi2.easiness, numNodes, c, seedval, 18)
