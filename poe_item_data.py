#!/usr/bin/env python3
from collections import defaultdict
from urllib.request import Request, urlopen
from urllib.error import URLError
from functools import *
from poe_utils import *

class PoEItemData():
	__default_format = 'utf-8'
	__default_url = "http://www.pathofexile.com/item-data"
	__default_headers = {}
	__default_headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
	__attribute_list = ['str', 'dex', 'int', 'str/int', 'str/dex', 'int/dex']
	__attribue_map = {'armour': {'str': 'Armour', 'dex': 'Evasion Rating', 'int': 'Energy Shield'},
			'weapon':{'str': 'Req_Str', 'dex': 'Req_Dex', 'int': 'Req_Int'}}
	__name_attribute = 'Name'
	__requirements = [x.upper() for x in __attribute_list]
	__rq_tables_generated = False # FIXME: bad design

	def __init__(self, item_family = 'armour'):
		self.tables = defaultdict(list) # Class -> Row
		self.rq_tables = defaultdict(lambda : defaultdict(list)) # Req -> Class -> Name
		self.__fetch_data(item_family)
		self.__classes = set([]) # all classnames encountered
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
			table_rows = parse_rows(rows) # implicits are concatenated
			self.tables[table_class] = table_rows

	def __generate_rq_tables(self):
		table_requirements = defaultdict(list)
		if self.data_type in list(self.__attribue_map.keys()):
			for attr in self.__attribute_list:
				table_requirements[attr] = [self.__attribue_map[self.data_type][c] for c in attr.split('/')]
		else:
			print('Please, define rules to walk the database')
			exit(1)

		for table_class, table in self.tables.items():
			# - HEADER
			# position of name
			p_name = self.__get_name_position(table_class)
			if p_name is None:
				continue
			# attribute (ex: 'Energy Shield' or 'Req Int'...)
			attribute_vlist = []
			# attributs -> position of requirements
			attr_pos = defaultdict(list)
			# attributs -> position of related requirements
			related_attr_pos = defaultdict(list)
			for a,v in table_requirements.items():
				attr_pos[a] = [table[0].index(rq_v) for rq_v in v]
				attribute_vlist.extend(v)
				attribute_vlist = list(set(attribute_vlist)) # remove dup
			# all requirements in header
			attribute_plist = [table[0].index(rq_v) for rq_v in attribute_vlist]
			for a, v in table_requirements.items():
				related_attr_pos[a] = [aa for aa in attribute_plist if aa not in attr_pos[a]]
			# - DATA
			for data in table[1:]:
				name = data[p_name]
				for attr in self.__attribute_list:
					if all(int(data[pos]) > 0 for pos in attr_pos[attr]):
						if all(int(data[pos]) == 0 for pos in related_attr_pos[attr]):
							self.rq_tables[attr.upper()][table_class].append(name)
							break
			self.__rq_tables_generated = True

	def get_items(self, item_class = ''):
		if not item_class:
			item_classes = self.get_classes()
		else:
			item_classes = [ item_class ]
		res = []
		for i_class in item_classes:
			res.extend(self.__get_items(i_class))
		return res

	def __get_items(self, item_class):
		p = self.__get_name_position(item_class)
		if p is not None:
			return [x[p] for x in self.tables[item_class][1:]]
		return []

	def __get_name_position(self, item_class):
		res = None
		attribute=self.__name_attribute
		table_header = self.tables[item_class][0]
		try:
			res = table_header.index(attribute)
		except ValueError as e:
			print('An error occured while fetching {attribute} in the table header of {classname}'.format(attribute=attribute, classname=item_class))
		return res

	def get_items_by_requirement(self, requirement, item_class = ''):
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
			return None
			# return re_list_filter(pattern, var)
		return var

	def get_requirements(self, pattern = ''):
		return self.__get_variable_by_pattern(self.__requirements, pattern)

	def get_classes(self, pattern = ''):
		return self.__get_variable_by_pattern(list(self.__classes), pattern)
