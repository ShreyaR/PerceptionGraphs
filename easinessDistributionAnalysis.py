from randomGraphGenerationV2 import ProblemInstance
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt


pi = ProblemInstance(100, 0.5, 10, 25)

# print np.histogram(np.array(pi.easiness.values()))

plt.hist(np.array(pi.easiness.values()), normed=False, histtype='bar')
plt.title("Distribution of edge easiness")
plt.show()