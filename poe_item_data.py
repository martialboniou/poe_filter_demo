#!/usr/bin/env python3
from sys import exit
from collections import defaultdict
from urllib.request import Request, urlopen
from urllib.error import URLError
from functools import *
from poe_utils import *

def generate_attribute(attribute_list): # attribute -> requirement
	attribute = defaultdict(list)
	for attr in attribute_list:
		attribute[attr] = ['Req '+c.capitalize() for c in attr.split('/')]
	return attribute

class PoEItemData():
	__default_format = 'utf-8'
	__default_url = "http://www.pathofexile.com/item-data"
	__default_headers = {}
	__default_headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
	__attribute_list = ['str', 'dex', 'int', 'str/int', 'str/dex', 'int/dex']
	no_requirement_tag = 'ALL'
	__classes = set([]) # all classnames encountered
	__requirements = [x.upper() for x in __attribute_list]
	__rq_tables_generated = False # FIXME: bad design

	def __init__(self, item_family = 'armour'):
		self.tables = defaultdict(list) # Class -> Row
		self.rq_tables = defaultdict(lambda : defaultdict(list)) # Req -> Class -> Name
		self.__fetch_data(item_family)
		self.__generate_tables()
		if item_family == 'armour':
			self.__generate_rq_tables()

	def __fetch_data(self, item_family):
		self.data_type = item_family
		url = self.__default_url+"/"+item_family
		req = Request(url, headers = self.__default_headers)
		try:
			resp = urlopen(req)
		except URLError as e:
			print('An error occured while fetching {url}\n\t{reason}'.format(url=url, reason=e.reason))
			exit(1)
		self.data = BeautifulSoup(resp.read().decode(self.__default_format))

	def __generate_tables(self):
		if self.data_type is None:
			return 1
		try:
			tables = self.data.findAll('table')
		except AttributeError as e:
			print('No tables found')
			return 1
		for table in tables:
			try:
				rows = table.find_all('tr')
			except AttributeError as e:
				print('Empty table')
				continue

			table_class = str(table.parent.findPrevious('h1').contents[0])
			self.__classes.add(table_class)  # remember all classnames
			table_rows  = parse_rows(rows) # implicits are concatenated
			self.tables[table_class] = table_rows

	def __generate_rq_tables(self):
		table_requirements = generate_attribute(self.__attribute_list)
		for table_class, table in self.tables.items():
			table_header, table_data = table[0], table[1:]
			try:
				p_name = table_header.index('Name')
			except ValueError as e:
				print('An error occured while fetching Name in the table header of {classname}'.format(classname=table_class))
				continue

			attribute_vlist = [] # list of all attribute headers (ex: 'Req Int'...)
			attr_pos = defaultdict(list) # attribute -> requirement position
			related_attr_pos = defaultdict(list) # attribute -> other requirement
			for a,v in table_requirements.items():
				attr_pos[a] = [table_header.index(rq_v) for rq_v in v] # position in header
				attribute_vlist.extend(v)
				attribute_vlist = list(set(attribute_vlist)) # remove dup
			attribute_plist = [table_header.index(rq_v) for rq_v in attribute_vlist] # all requirements in header
			for a, v in table_requirements.items():
				related_attr_pos[a] = [aa for aa in attribute_plist if aa not in attr_pos[a]]

			for data in table_data:
				name = data[p_name]
				for attr in self.__attribute_list:
					if all(int(data[pos]) > 0 for pos in attr_pos[attr]):
						if all(int(data[pos]) == 0 for pos in related_attr_pos[attr]):
							self.rq_tables[attr.upper()][table_class].append(name)
						break
					elif all(int(data[pos]) == 0 for pos in attribute_plist):
						self.rq_tables[self.no_requirement_tag][table_class].append(name)
						break
			self.__rq_tables_generated = True

	def get_items_by_requirement(self, requirement, item_class = '', strict = False):
		rq = self.__get_items_by_requirement(requirement, item_class)
		if not strict:
			no_rq = self.__get_items_by_requirement(self.no_requirement_tag, item_class)
			rq.extend(no_rq)
		return rq

	def __get_items_by_requirement(self, requirement, item_class = ''):
		if not self.__rq_tables_generated:
			self.__generate_rq_tables()
		rq_tabs = self.rq_tables[requirement]
		rq = []
		if item_class:
			rq = rq_tabs[item_class]
		else:
			for rq_class, rq_items in rq_tabs.items():
				rq.extend(rq_items)
		return rq

	def get_selected_items(self, action, item_class = ''):
		# TODO: refactor __generate_rq_tables
		pass

	def __get_variable_by_pattern(self, var, pattern = ''):
		if pattern:
			return re_list_filter(pattern, var)
		return var

	def get_requirements(self, pattern = ''):
		return self.__get_variable_by_pattern(self.__requirements, pattern)

	def get_classes(self, pattern = ''):
		return self.__get_variable_by_pattern(list(self.__classes), pattern)
