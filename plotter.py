import matplotlib.pyplot as plt

with open('results_ourmethodv18.txt') as f:
# with open('results_baselinev18.txt') as f:
# with open('results_ourmethodv3.txt') as f:
# with open('results_ourmethodv3.txt') as f:
	results = {}

	for line in f:
		n, acc, _, _ = line.rstrip().split(',')
		# n, _, _, acc = line.rstrip().split(',')
		# n, acc, _ = line.rstrip().split(',')
		n = int(n)
		acc = float(acc)
		
		if n not in results.keys():
			results[n] = []
		results[n].append(acc)

x = []
y = []

for k in sorted(results.keys()):
	x.append(k)
	v = results[k]
	y.append(sum(v)/len(v))

baseline ,= plt.plot(x,y, label="Old Error Model")

with open('results_ourmethodv17.txt') as f:
	# with open('results_ourmethodv3.txt') as f:
	# with open('results_ourmethodv3.txt') as f:
	results = {}

	for line in f:
		n, acc, _, _ = line.rstrip().split(',')
		# n, _, _, acc = line.rstrip().split(',')
		# n, acc, _ = line.rstrip().split(',')
		n = int(n)
		acc = float(acc)

		if n not in results.keys():
			results[n] = []
		results[n].append(acc)

x = []
y = []


for k in sorted(results.keys()):
	x.append(k)
	v = results[k]
	y.append(sum(v) / len(v))

# ourmethod ,= plt.plot(x, y, label="Our Method")
ourmethod ,= plt.plot(x, y, label="New Error Model")

# plt.title("Average Accuracy of EM with different observations")
# plt.title("Average accuracy of predicted edge directions with different observations")
plt.title("Comparison of the old and new error model")
# plt.title("Average MAP error of predicted difficulties with different graph sizes")
# plt.title("Average MAP error of predicted difficulties with different observations")
# plt.title("Average MAP error of predicted difficulties with different graph densities")
# plt.title("Average accuracy of predicted edge directions with different graph densities")
plt.xlabel('Number of nodes in the graph')
# plt.xlabel('Number of observations per edge')
# plt.xlabel('(Max) Number of neighbours per node')
plt.ylim([0.0,1.0])
# plt.ylim([0.05,0.15])
# plt.ylabel('MAP error of predicted edge easiness')
plt.ylabel('Acuracy of predicted edge directions')
plt.legend(handles=[baseline, ourmethod])
plt.show()

