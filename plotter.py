import matplotlib.pyplot as plt

# with open('results_ourmethod.txt') as f:
with open('results_ourmethodv2.txt') as f:
	results = {}

	for line in f:
		print line
		n,acc = line.rstrip().split(',')
		n = int(n)
		acc = float(acc)
		
		if n not in results.keys():
			results[n] = []
		results[n].append(acc)

# for w in results.keys():

x = []
y = []

for k in sorted(results.keys()):
	x.append(k)
	v = results[k]
	y.append(sum(v)/len(v))

plt.plot(x,y)

plt.title("Average Accuracy of EM with different node sizes")
plt.xlabel('Number of nodes in the graph')
plt.ylim([0.0,1.0])
plt.ylabel('Fraction of correctly predicted edge directions')
plt.show()

