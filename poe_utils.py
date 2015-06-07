#!/usr/bin/env python3
# python3 -m pip install BeautifulSoup4
from collections import defaultdict
from bs4 import BeautifulSoup, NavigableString, CData
from os import listdir
from os.path import dirname, abspath, exists, isfile, join
import csv
import re

def list_replace(l, x, y, once = True):
	enc = []
	idx = []
	if not isinstance(x, list):
		x = [x]
	len_x = len(x)
	if not isinstance(y, list):
		y = [y]
	else:
		y.reverse()
	while True:
		# check full x match in l
		for i, v in enumerate(l):
			if v in x:
				if v not in enc:
					enc.append(v)
					idx.append(i)
		if idx and (len(idx) == len_x):
			for i_i, ix in enumerate(idx):
				l.pop(ix-i_i) # compensate pop
			for k in y:
				l.insert(idx[0], k)
			if once:
				break
			enc = []
			idx = []
		else:
			break

def list_replace_all(l, x, y):
	list_replace(l, x, y, False)

def unique_sorter(item):
	return (len(item[0]), item)

def occurence_sorter(item):
	return (item[0], item)

def parse_multiline(element, poe_implicit_split = False):
	""" Get data from a row & regroup tag-separated
	    string (<br/>) in a list
	    poe_implicit_split: <number>( to )<number>
	    for Implicit Mods extraction (optional)
	"""
	res = []
	for data in element:
		content = []
		for x in data.strings:
			if poe_implicit_split:
				to_block = re.split(" to (?=\d)", x)
				if len(to_block) > 1:
					content.append(to_block)
					continue
			content.append(x)
		if len(content) == 1:
			content = content[0]
		if not content:
			content = ''
		res.append(content)
	return res

def parse_rows(rows):
	""" Get data from rows """
	res = []
	rowspan = 1
	irows = iter(rows)
	for row in irows:
		for el in ['th', 'td']:
			table_el = row.findAll(el)
			line = []
			if table_el:
				try:
					rowspan = int(table_el[0].attrs["rowspan"])
				except KeyError as e:
					rowspan = 1
				line = parse_multiline(table_el, True)
				rowsp = rowspan
				while rowsp > 1:
					try:
						next_row = next(irows)
						table_el = next_row.findAll(el)
						if table_el:
							line.extend(parse_multiline(table_el, True))
					except StopIteration as e:
						pass
					rowsp -= 1
				res.append(line)
	return res

def tokenize_name(n):
	return n.split() # default = whitespace

def shorten_name(n):
	""" Singularize or remove 's from a name
	"""
	if n[-2:] == "'s":
		return n[:-2]
	if n[-1] == "s" and n[-3:-1] not in ["ou", "ri"]: # + heuristic for readability
		return n[:-1]
	return None

def match_name(pattern, n):
	return re.match(".*({pattern}).*".format(pattern=pattern), n) is not None

def quotify(word, pattern = ''):
	if not pattern or match_name(pattern, word):
		return '"{0}"'.format(word)
	return word

def find_unique_matchers(n, conflict_ns):
	tokens = tokenize_name(n)
	# FIXME: short hack! here
	if len(tokens) > 2: # 3 words items max!
		tokens.append(tokens[0]+" "+tokens[1])
		tokens.append(tokens[1]+" "+tokens[2])
	# end short hack!
	sn = shorten_name(n)
	if sn is not None:
		tokens = [sn] + tokens # add a short fullname too
	all_tokens = tokens
	for token in tokens:
		short_token = shorten_name(token)
		if short_token is not None:
			all_tokens = [short_token] + all_tokens
	matches = []
	matched = False
	for token in all_tokens:
		matched = False
		if not token:
			continue
		for cn in conflict_ns:
			if match_name(token, cn):
				matched = True
				break
		if not matched:
			matches.append(token)
	if not matches:
		return n
	matches.sort(key=len)
	return matches

def compress_names(ns, other_ns):
	uncomp_ns = [] # list of uncompressible names
	unique_ns = [] # list -> tokens list
	for n in ns:
		uniques = find_unique_matchers(n, other_ns)
		if isinstance(uniques, str):
			uncomp_ns.append(n)
		else:
			unique_ns.append(uniques)
	tok_ns = []
	unique_ns.sort(key=unique_sorter)
	occ_tok_ns = []
	max_occ = len(ns)
	ruler = False # switch if only one solution
	for u in unique_ns:
		occ, token = 1, ''
		l_limit = max([len(x) for x in u])
		if any(w for w in occ_tok_ns if w[1] in u):
			continue # jump if it contains the best candidate
		for t in u:
			occ_t = len([sub for sub in unique_ns if any(x for x in sub if match_name(t,x))])
			if occ_t == max_occ: # rule em all (ex: Round match all items in STR/DEX Shield)
				token = t
				ruler = True
				break
			len_t = len(t)
			if occ_t > occ or (occ_t == occ and len_t < l_limit):
				token = t
				l_limit = len_t
				occ = occ_t
		if ruler:
			break
		if not token:
			token = u[0] # first by default
		occ_tok_ns.append([occ, token])
	if ruler:
		return [token] # skip uncomp_ns as token is surely inside
	occ_tok_ns.sort(key=occurence_sorter, reverse=True) # [(occurence, item)] -> sorted [item]
	tok_ns = [x[-1] for x in occ_tok_ns]
	# ensure tok_ns keeps shortest only (say, no ['Spike', 'Spiked'])
	double_tns = [x for x in tok_ns for y in tok_ns if x != y and match_name(y, x)]
	tok_ns = [t for t in tok_ns if t not in double_tns]
	# ensure uncompressible ones cannot be reduced too
	# (say, no ['Flesh', 'Fleshripper'] from 'Flesh and Spirit' and Axe)
	matched_uns = [x for x in uncomp_ns if any(y for y in tok_ns if match_name(y, x))]
	unc_ns = [t for t in uncomp_ns if t not in matched_uns]
	tok_ns.extend(unc_ns)
	return tok_ns

def import_db(subdir_name, extension = 'csv'):
	tables = defaultdict(list)
	db_dir = join(dirname(abspath(__file__)), subdir_name)
	if not exists(db_dir):
		print('file not found in {0}'.format(db_dir))
		return tables
	for f in listdir(db_dir):
		filename = join(db_dir, f)
		if isfile(filename) and f.endswith('.'+extension):
			len_ext = 1 + len(extension) if extension != '' else 0
			category = f[:len(f)-len_ext].title().replace('_', ' ')
			tables[category] = []
			with open(filename, 'r', encoding='utf-8') as csvfile:
				try:
					dialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters=";,")
				except:
					print("not well-formed {0} import file".format(category))
				else:
					csvfile.seek(0)
					reader = csv.reader(csvfile, dialect)
					for line in reader:
						if line:
							tables[category].append(line)
	return tables

def get_db_column(attribute, table):
	try:
		idx = table[0].index(attribute)
	except (ValueError, IndexError):
		return []
	res = []
	for row in table[1:]:
		try:
			element = row[idx]
		except IndexError:
			continue
		res.append(element)
	return res
