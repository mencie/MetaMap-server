import graph
import util
import machine


config = '''# Inputs!
graph_file = %(folder)s/%(title)s_input
data_format = edge_factored

# Seeds!
seed_file = %(folder)s/%(title)s_seed

# Labels!
gold_labels_file = %(folder)s/%(title)s_gold

# Tests!
test_file = %(folder)s/%(title)s_gold

# Parameters that were never explained!
iters = 10
verbose = false
prune_threshold = 0

# Algorithm things! (algos: lp_zgl, adsorption, mad)
algo = mad
mu1 = 1
mu2 = 1e-2
mu3 = 1e-2
beta = 2

# Outputs!
output_file = %(folder)s/%(title)s_out
'''

# Does all required work to make a set of junto files given the
# pickle-formatted input, the title. Optionally, one can specify a
# folder in which the junto files will be placed, the random numbers
# to be used, the threshold of instances needed for each protocol to be
# included, whether or not to return the underlying graph, and whether
# to construct multiple test files from the given input.
def make_junto(filename, title, folder='.', threshold=0, ret=False):
	
	if not '_spread' in filename:
		print 'Spreading file...\n'
		filename = util.spread(filename)
	
	print 'Making graph...'
	g = graph.make_graph(filename)
	
	if threshold:
		print '\nTrimming...'
		g['procedures'] = util.trim(g['procedures'], threshold)
	
	print '\nConstructing junto files...'
	graph.to_junto(g, title)
	
	with open(title + '_config', 'w') as f:
		f.write(config % {'title': title, 'folder': folder})
	
	print '\n...Done'
	if ret:
		return g

# Does all required work to test the test cases in the (pickled) testing
# file 
def do_test(outfile, testfile):
	
	if not '_spread' in testfile:
		print 'Spreading file...\n'
		testfile = util.spread(testfile)
	
	print 'Making graph...'
	g = graph.make_graph(testfile)
	procs = g['procedures']
	
	print '\nReading output...'
	learned = machine.read_out(outfile)
	
	print '\nApplying to input file...'
	results = machine.guess(learned, procs)
	
	machine.summarize(results)
	machine.matrix(results)