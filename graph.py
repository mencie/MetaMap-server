import pickle
import json
import util


'''WORKS WITH _SPREAD FILES ONLY'''
# Creates a graph from the given data file. Labels procedure nodes with
# the appropriate protocol, and creates concept nodes for all concepts
# encountered. Uses Node class to store data.
def make_graph(pickle_file):
	items = util.load(pickle_file)
	
	procedures = []
	concepts = {}
	
	print 'Starting...'
	for k in range(len(items)):
		
		try:
			annot = json.loads(items[k]['annotations'])
		except ValueError:
			print '\nIndex %d has no annotaions.' % k
			
			while k < len(items):
				if 'annotations' not in items[k]:
					print 'Index %d has no annotations.' % k
				k += 1
			
			print '\nQuitting...\n'
			return
		
		if (k+1) % 100 == 0:
			print 'On %dth item.' % (k+1)
		
		new = Node( str(k) )
		new.add_label( items[k]['protocol'] )
		
		for conc in annot['Mappings']:
			name = conc['CUI'] + ('_neg' if conc['Negated'] else '')
			
			if name not in concepts.keys():
				concepts[name] = Node(conc['CUI'])
			
			new.add_edge(concepts[name], 1)
		
		procedures.append(new)
	
	print '...Done.'
	
	return { 'procedures': procedures, 'concepts': concepts }

# Storage format for a graph. Offers options to title, label, and add
# edges to nodes. Automatically creates a corresponding edge from the
# given node back to the source node.
class Node:
	
	# Makes a new Node with the provided title
	def __init__(self, title):
		self.title = title
		self.edges = {}
		self.label = None
	
	# Adds the provided node to this node's edges, with the provided
	# weight.. Also adds this node to the provided node's edges.
	def add_edge(self, node, weight):
		self.edges[node.title] = { 'node': node, 'weight': weight }
		if self.title not in node.edges.keys():
			node.add_edge(self, weight)
	
	# Sets the node to have the provided label
	def add_label(self, label):
		self.label = label
	
	# Returns a list of nodes to which this one has an edge.
	def get_edges(self):
		return [ edge['node'] for edge in self.edges.values() ]
	
	# Returns a list of the titles of the nodes to which this one has
	# an edge.
	def get_edge_titles(self):
		return self.edges.keys()

# Takes a graph (such as the output from make_graph) and converts it to
# .csv format given the output filename. Graph is directed with all
# edges pointing from procedure nodes to concept nodes.
def to_csv(g, outfile):
	data = ''
	
	for proc in g['procedures']:
		for edgetitle in proc.get_edge_titles():
			data += '%s;%s\n' % (proc.title, edgetitle)
	
	if not outfile.endswith('.csv'):
		outfile += '.csv'
	
	with open(outfile, 'w') as f:
		f.write(data)

# Takes a graph (such as the output from make_graph) and converts it to
# junto-readable files, including:
# <title>_input: <source node>TAB<target node>TAB<edge weight (1.0)>
# <title>_seed: <node>TAB<label>TAB<confidence (1.0)>
# <title>_gold: <node>TAB<label>TAB<confidence (1.0)>
# The test parameter is a list which contains the indices of all
# evaluation (procedure) nodes. Any node with an index not in this
# list is a seed node.
def to_junto(g, title):
	input = []
	seed = []
	gold = []
	form = '%s\t%s\t1.0\n'
	
	nodes = g['procedures']
	
	for k in range(len(nodes)):
		
		for edgetitle in nodes[k].get_edge_titles():
			input.append( form % (nodes[k].title, edgetitle) )
		
		gold.append( form % (nodes[k].title, nodes[k].label) )
		seed.append( form % (nodes[k].title, nodes[k].label) )
	
	with open(title + '_input', 'w') as f:
		f.write(''.join(input))
	
	with open(title + '_seed', 'w') as f:
		f.write(''.join(seed))
	
	with open(title + '_gold', 'w') as f:
		f.write(''.join(gold))