import pickle
from urllib2 import urlopen


'''WORKS WITH _SPREAD FILES ONLY'''
# Loads the given pickle file and trims irrelevant or non-existent
# protocols
def load(filename):
	with open(filename, 'r') as f:
		items = pickle.load(f)
	
	empty_anot = '{\n  "Negations": [], \n  "Mappings": []\n}'
	
	return [ item for item in items if item['protocol']
			not in ['', 'OTHER', 'RESEARCH', None] and
			item['annotations'] != empty_anot ]

# Trims the procedures such that no protocol that appears less than
# threshold times is represented. -1 to list. Takes graph nodes.
def trim(nodes, threshold):
	count = {}
	
	for p in nodes:
		if p.label in count:
			count[p.label] += 1
		else:
			count[p.label] = 1
	
	if threshold == -1:
		sort = sorted([(key, count[key]) for key in count],
				key=lambda thing: thing[1], reverse=True)
		for thing in sort:
			print '%s\t%d' % thing
		threshold = input('Enter threshold to use: ')
	
	small = []
	
	for p in nodes:
		if count[p.label] > threshold:
			small.append(p)
	
	return small

# Returns a random number sequence from random.org.
def rand(max):
	address = 'http://www.random.org/sequences/' + \
			'?min=0&max=%d&col=1&format=plain&rnd=new'
	
	ints = urlopen(address % max).read()
	
	return [int(num) for num in ints.split()]

'''WORKS WITH _SPREAD FILES ONLY'''
# Prints or returns a list of protocols in the file and the number
# of procedures that use that protocol.
def count_prot(filename, output=True, ret=False):
	items = load(filename)
	d = {}
	
	for item in items:
			if item['protocol'] in d:
				d[item['protocol']] += 1
			else:
				d[item['protocol']] = 1
	
	things = [(key, d[key]) for key in d]
	
	if output:
		for pair in sorted(things, key=lambda x: x[1], reverse=True):
			print '%s occurs %d times.' % pair
	
	if ret:
		return sorted(things, key=lambda x: x[1], reverse=True)

# Spreads multiple protocols in a procedure out over multiple procedures
def spread(filename):
	with open(filename, 'r') as f:
		items = pickle.load(f)
	new = []
	
	for item in items:
		for p in item['protocols']:
			item['protocol'] = p['name']
			new.append(item)
	
	if '.' in filename:
		parts = filename.rsplit('.', 1)
		newfname = parts[0] + '_spread.' + parts[1]
	else:
		newfname = filename + '_spread'
	
	with open(newfname, 'w') as f:
		pickle.dump(new, f)
	
	return newfname

# Spreads and trims a file so that only protocols preformed a certain
# number of times remain.
def trim(filename, threshold):
	
	if not '_spread' in filename:
		print 'Spreading...'
		filename = spread(filename)
	
	print 'Counting...'
	count = count_prot(filename, False, True)
	allowed = [thing[0] for thing in count if thing[1] > threshold]
	
	print 'Trimming...'
	items = load(filename)
	
	new = [item for item in items if item['protocol'] in allowed]
	
	if '.' in filename:
		pieces = filename.rsplit('.',1)
		newfname = pieces[0] + '_trim.' + pieces[1]
	else:
		newfname = filename + '_trim'
	
	with open(newfname, 'w') as f:
		pickle.dump(new, f)