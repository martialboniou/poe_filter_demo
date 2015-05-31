#!/usr/bin/env python3
# python3 -m pip install BeautifulSoup4
from bs4 import BeautifulSoup, NavigableString, CData
import re

def parse_multiline(element):
	""" Get data from a row & regroup tag-separated
	    string (<br/>, ...) in a list
	"""
	res = []
	for data in element:
		content = []
		for x in data.strings:
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
			table_el = row.find_all(el)
			line = []
			if table_el:
				try:
					rowspan = int(table_el[0].attrs["rowspan"])
				except KeyError as e:
					rowspan = 1
				line = parse_multiline(table_el)
				rowsp = rowspan
				while rowsp > 1:
					try:
						next_row = next(irows)
						table_el = next_row.find_all(el)
						if table_el:
							line.extend(parse_multiline(table_el))
					except StopIteration as e:
						pass
					rowsp -= 1
				res.append(line)
	return res

def tokenize_name(n):
	return n.split() # default = whitespace

def match_name(pattern, n):
	if pattern == "Nubuck":
		if re.match(".*({pattern}).*".format(pattern=pattern), n) is not None:
			print("essai: "+str(n))
			print("test: "+str(re.match(".*({pattern}).*".format(pattern=pattern), n) is not None))

	match = re.match(".*({pattern}).*".format(pattern=pattern), n) is not None
	return match

def find_unique_matchers(n, conflict_ns):
	tokens = tokenize_name(n)
	# FIXME: short hack! here
	if len(tokens) > 2: # 3 words items max!
		tokens.append(tokens[0]+" "+tokens[1])
		tokens.append(tokens[1]+" "+tokens[2])
	# end short hack!
	matches = []
	matched = False
	for token in tokens:
		matched = False
		if not token:
			continue
		for cn in conflict_ns:
			if match_name(token, cn):
				matched = True
				break
		if not matched:
			matches.append(token)
	if matches == []:
		return n
	return matches

def compress_names(ns, all_ns):
	comp_ns = []
	unique_ns = [] # list -> list
	other_ns = [n for n in all_ns if not n in ns]
	for n in ns:
		uniques = find_unique_matchers(n, other_ns)
		if isinstance(uniques, str):
			comp_ns.append(n)
		else:
			unique_ns.append(uniques)
	## occur_list = [item for sublist in unique_ns for item in sublist]
	# TODO: eliminate inside matchers
	tok_ns = []
	for u in unique_ns:
		occ, token = 1, ''
		max_occ = len(u)
		l_limit = max([len(x) for x in u])
		alone = False
		for t in u:
			occ_t = len([sub for sub in unique_ns if t in sub])
			if occ_t == max_occ: # all
				alone = True
				token = t
			len_t = len(t)
			if occ_t > occ or (occ_t == occ and len_t < l_limit):
				token = t
				l_limit = len_t
				occ = occ_t
		if not token:
			token = u[0] # first by default

		tok_ns.append(token)
	comp_ns.extend(list(set(tok_ns)))
	return comp_ns
