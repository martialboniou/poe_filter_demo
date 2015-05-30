#!/usr/bin/env python3
# python3 -m pip install BeautifulSoup4
from bs4 import BeautifulSoup, NavigableString, CData

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
