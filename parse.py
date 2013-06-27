from structures import Pack

# Takes the given XML file, reads information from it, and writes the
# information in JSON format to the given output file.
def parse_xml(fxml, fjson):
	f = open(fxml, 'r')
	lines = f.readlines()
	f.close()
	
	negations, mappings = get_concepts(0, lines, 0)
	
	info = Pack(negations, mappings)
	text = info.to_json()
	
	f = open(fjson, 'w')
	f.write(text)
	f.close()
	
	return info, text

# Reads concepts from the XML file.
def get_concepts(k, lines, n):
	
	# Find and loop through negations
	negations = []
	while '</Negations>' not in lines[k]:
		if '<Negations Count="0" />' in lines[k]: break
		
		if '<Negation>' in lines[k]:
			k, neg = parse_negation(k, lines, n)
			negations.append(neg)
		
		k += 1
	
	# Next find and loop through the mappings
	mappings = []
	while k < len(lines) and not '</MMOs>' in lines[k]:
		
		if '<Mapping>' in lines[k]:
			while not '</Mapping>' in lines[k]:
				
				if '<Candidate>' in lines[k]:
					k, map = parse_candidate(k, lines, n)
					mappings.append(map)
				
				k += 1
		
		k += 1
	
	if k < len(lines)-1:
		morenegs, moremaps = get_concepts(k, lines, n+1)
		appendall(negations, morenegs)
		appendall(mappings, moremaps)
	
	return negations, mappings

# Pulls necessary information from a "<Negation>" section
def parse_negation(k, lines, n):
	neg = {}
	
	while '</Negation>' not in lines[k]:
		
		if '<NegConcPI>' in lines[k]:
			neg['Position'] = ( n, int(get_cont(lines[k+1])),
				int(get_cont(lines[k+2])) )
			k += 2
		elif '<NegConcMatched>' in lines[k]:
			neg['Match'] = get_cont(lines[k])
		
		k += 1
	
	return k, neg

# Pulls necessary concepts from a "<Mapping><Candidate>" section
def parse_candidate(k, lines, n):
	m = {}
	
	while '</Candidate>' not in lines[k]:
		
		if '<CandidateScore>' in lines[k]:
			m['Score'] = -int(get_cont(lines[k]))
		elif '<CandidateCUI>' in lines[k]:
			m['CUI'] = get_cont(lines[k])
		elif '<CandidateMatched>' in lines[k]:
			m['Match'] = get_cont(lines[k])
		elif '<CandidatePreferred>' in lines[k]:
			m['Concept'] = get_cont(lines[k])
		elif '<Sources' in lines[k]:
			k, s = get_sources(k+1, lines)
			m['Sources'] = s
		elif '<ConceptPI>' in lines[k]:
			m['Position'] = ( n, int(get_cont(lines[k+1])),
				int(get_cont(lines[k+2])) )
			k += 2
		
		k += 1
	
	return k, m

# Reads all sources starting from the first instance and ending at
# "</Sources>"
def get_sources(k, lines):
	sources = []
	while not '</Sources>' in lines[k]:
		s = get_cont(lines[k])
		sources.append(s)
		k += 1
	return k, sources

# Appends all items from source list to destination list.
def appendall(dest, source):
	for item in source:
		dest.append(item)

# Returns the content of a line between two XML tags.
def get_cont(line):
	ltag, rest = line.split('>', 1)
	content, rtag = rest.split('<', 1)
	return content
