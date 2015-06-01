#!/usr/bin/env python3
# python3 -m pip install BeautifulSoup4
from bs4 import BeautifulSoup, NavigableString, CData
import re
import sys

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
			table_el = row.find_all(el)
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
						table_el = next_row.find_all(el)
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
	match = re.match(".*({pattern}).*".format(pattern=pattern), n) is not None
	return match

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
	comp_ns = []
	unique_ns = [] # list -> list
	for n in ns:
		uniques = find_unique_matchers(n, other_ns)
		if isinstance(uniques, str):
			comp_ns.append(n)
		else:
			unique_ns.append(uniques)
	tok_ns = []
	unique_ns.sort(key=unique_sorter)
	occ_tok_ns = []
	for u in unique_ns:
		occ, token = 1, ''
		max_occ = len(u)
		l_limit = max([len(x) for x in u])
		if any(w for w in occ_tok_ns if w[1] in u):
			continue # jump if it contains the best candidate
		for t in u:
			occ_t = len([sub for sub in unique_ns if t in sub])
			if occ_t == max_occ: # all
				token = t
			len_t = len(t)
			if occ_t > occ or (occ_t == occ and len_t < l_limit):
				token = t
				l_limit = len_t
				occ = occ_t
		if not token:
			token = u[0] # first by default
		occ_tok_ns.append([occ, token])
	occ_tok_ns.sort(key=occurence_sorter, reverse=True) # [(occurence, item)] -> sorted [item]
	tok_ns = [x[-1] for x in occ_tok_ns]
	tok_ns.extend(comp_ns)
	return tok_ns
