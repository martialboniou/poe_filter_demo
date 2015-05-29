#!/usr/bin/env python3
# python3 -m pip install BeautifulSoup4
from bs4 import BeautifulSoup
import re

def parse_rows(rows):
	""" Get data from rows """
	results = []
	rowspan = 1 # default
	rowspan_checked = False
	for row in rows:
		table_headers = row.find_all('th')
		if table_headers:
			if not rowspan_checked:
				if table_headers[0] is not None:
					try:
						rowspan = int(table_headers[0].attrs["rowspan"])
					except KeyError as e:
						print('rowspan not found in table header')
				rowspan_checked = True
			results.append([headers.get_text() for headers in table_headers])
		table_data = row.find_all('td')
		if table_data:
			results.append([data.get_text() for data in table_data])
	if rowspan > 1:
		return multi_join(results, rowspan)
	return results

def multi_join(listing, lines):
	# lines = number of lines to join
	acc = []
	l = []
	counter = 0
	for it in listing:
		counter += 1
		l.extend(it)
		if counter >= lines:
			acc.append(l)
			l = []
			counter = 0
	return acc

def re_list_filter( segment, lst ):
	regex = re.compile(".*(" + segment + ").*")
	return [m.group(0) for l in lst for m in [regex.search(l)] if m]
