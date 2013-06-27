import json

'''
# Wrapper class for a dictionary. Provides methods to properly store
# position, CUI, match, concept, score, source, and negation
# information.
class Concept:
	
	def __init__(self):
		self.dict = {}
	
	def set_position(self, n, position, length):
		self.dict['Position'] = n, int(position), int(length)
	
	def set_cui(self, cui):
		self.dict['CUI'] = cui
	
	def set_match(self, name):
		self.dict['Match'] = name
	
	def set_concept(self, name):
		self.dict['Concept'] = name
	
	def set_score(self, score):
		self.dict['Score'] = -int(score)
	
	def set_sources(self, sources):
		self.dict['Sources'] = sources
	
	def make_neg(self):
		self.dict['Negated'] = True
	
	def get_dict(self):
		return self.dict
	
	def is_neg(self):
		return 'Negated' in self.dict.keys() \
			and self.dict['Negated'] == True
	
	def get_position(self):
		return self.dict['Position']
	
	# Returns a string representation of the object.
	def str(self):
		s = ''
		for key in self.dict:
			s += key + ': ' + str(self.dict[key]) + '\n'
		return s
'''

# Class to store the mapping and negation information in a single
# object. Strips the overlaying "concept" class.
class Pack:
	
	def __init__(self, negations, mappings):
		
		self.maps = {}
		self.negs = negations
		
		negList = [n['Position'] for n in negations]
		for m in mappings:
			if m['Position'] in negList:
				m['Negated'] = True
			else:
				m['Negated'] = False
			self.add(m)
		self.trim_mappings()
	
	# Add a Concept mapping to the object. Strips the Concept wrapper
	# and adds the underlying dictionary.
	def add(self, m):
		id = m['Position']
		
		del m['Position']
		
		if id not in self.maps.keys():
			self.maps[id] = [m]
		else:
			self.maps[id].append(m)
	
	# Removes duplicate concepts from mappings
	def trim_mappings(self):
		
		for key in self.maps.keys():
			cuis = set([conc['CUI'] for conc in self.maps[key]])
			
			for elem in self.maps[key][:]:
				if elem['CUI'] in cuis:
					cuis.remove(elem['CUI'])
				else:
					self.maps[key].remove(elem)
	
	# Returns a string containing JSON-formatted data from the object.
	def to_json(self):
		copyConc = {}
		copyNegs = []
		
		for key in self.maps.keys():
			copyConc[str(key)] = []
			for map in self.maps[key]:
				copyConc[str(key)].append(map)
		
		for neg in self.negs:
			copyNegs.append(neg)
		
		for neg in copyNegs:
			neg['Position'] = str(neg['Position'])
		
		return json.dumps({'Concepts': copyConc,
			'Negations': copyNegs}, sort_keys=True, indent=4)
