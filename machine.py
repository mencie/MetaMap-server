

# Reads an output file from the junto program of the format:
# <node name>TAB<gold label> <gold score>TAB<seed label> <seed score>
# 		TAB[<estimated label> <estimated score>]+TAB
# 		<test node? (true/false)>TAB<mean reciprocal rank>
def read_out(outfile):
	with open(outfile, 'r') as f:
		items = f.readlines()
	
	# Split, find concept nodes
	items = [item.split('\t') for item in items if item.startswith('C')]
	
	learned = {}
	for item in [item for item in items if len(item[3].split(' ')) > 2]:
		labels = zip(item[3].split(' ')[::2], item[3].split(' ')[1::2])
		labels = filter(lambda item: item[0] != '__DUMMY__', labels)
		
		learned[item[0]] = sorted(labels, key=lambda x: x[1])
	
	return learned

# Averages the labels of all concepts from a given input procedure.
# Returns a list of concepts ranked by their likelihood.
def guess_one(learned, proc):
	labels = {}
	
	for conc in [t for t in proc.get_edge_titles() if t in learned]:
		for tup in learned[conc]:
			if tup[0] in labels:
				labels[tup[0]][0] += float(tup[1])
				labels[tup[0]][1] += 1
			else:
				labels[tup[0]] = [float(tup[1]), 1]
	
	result = []
	for lab in labels:
		result.append((lab, labels[lab][0]/labels[lab][1]))
	
	return [item[0] for item in sorted(result, key=lambda x: x[1],
			reverse=True)]

# Takes a list of procedures and results from the adsorption algorithm.
# Finds the top three guesses for each procedure and calculates the
# percent correct after the first, second, and third guesses.
def guess(learned, tests):
	results = []
	
	k = 1
	print 'Starting...'
	
	for item in tests:
		d = { 'actual': item.label, 'guess': guess_one(learned, item) }
		results.append(d)
		
		if k%100 == 0:
			print 'On %dth item.' % k
		k += 1
	
	print '...Done.'
	
	return results

# Summarizes output data by specifying the number correct within the
# first, second, and third guesses.
def summarize(results):
	
	correct = [0, 0, 0]
	total = 0
	
	for item in results:
		total += 1
		
		k=0
		while k < min(3, len(item['guess'])):
			if item['actual'] == item['guess'][k]:
				correct[k] += 1
				break
			k += 1
	
	percent = []
	for k in range(3):
		percent.append( float(sum(correct[:k+1]))/total )
	
	print ''
	print '--------------RESULTS--------------'
	print 'Total: %d\n' % total
	print 'Guess:            one   two   three'
	print 'Total correct:    %-6d%-6d%-6d' % tuple(correct)
	print 'Percent correct:  %-6.2f%-6.2f%-6.2f' % tuple(percent)
	print '-----------------------------------'
	print ''

# Prints confusion matrix for output data
def matrix(results):
	
	# Find all protocols
	labeled = set([proc['actual'] for proc in results])
	guessed = set([g for g in proc['guess'] for proc in results])
	prot = sorted([item for item in labeled | guessed])
	
	mat = [[0]*len(prot) for k in range(len(prot))]
	
	for item in results:
		if item['guess']:
			actual = prot.index(item['actual'])
			guess = prot.index(item['guess'][0])
			mat[actual][guess] += 1
	
	print ' '*14 + 'Predicted:'
	print ' '*14 + '%-6s'*len(prot) % tuple(prot)
	print 'Actual: %-6s'%prot[0] + '%-6s'*len(prot)%tuple(mat[0])
	for k in range(1, len(prot)):
		print ' '*8 + '%-6s'%prot[k] + '%-6s'*len(prot)%tuple(mat[k])