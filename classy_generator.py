#!/usr/bin/env python3
# python3 -m pip install BeautifulSoup4
from poe_item_data import PoEItemData
from poe_utils import import_db, get_db_column, compress_names, quotify
from collections import defaultdict
from sys import exit

output_filename = "Partial_Classy.filter"

class Color:
	def __init__(self, r, g, b, a = None):
		self.__r = r
		self.__g = g
		self.__b = b
		self.__a = a

	def __repr__(self):
		code = 'ColorR:'+self.__r+'G:'+self.__g+'B:'+self.__b
		if a is not None:
			code += 'A:'+self.__a
		return code

	def get_color(self):
		colors = [self.__r, self.__g, self.__b]
		a = self.__a
		if a is not None:
			colors.append(a)
		return colors

	def __str__(self):
		return ' '.join(str(c) for c in self.get_color())

class ClassyGenerator:
	__default_output_filename = 'filter.txt'
	__template = 3*' '+"""#Gear - {requirement} {category_name}{option}
	Rarity {rarity}
	BaseType {items}
	SetTextColor {coloring}"""+11*' '+"""#{rarity} "Junk"

"""
	__class_version_template = ' ({the_class})\n\tClass {the_class}'
	colors = {'normal': Color(190, 190, 190), 'magic' : Color(120, 120, 230)}
	rarities = ['normal', 'magic']
	tab_len = 4
	comment_prefix = "### {text}\n\n"
	__filter = None

	def __init__(self, filtr = None):
		self.database = None
		self.database = PoEItemData('armour')
		self.base_types = self.database.get_items()
		self.category_name = self.database.data_type.upper()
		self.current_class = None
		self.extra_base_types = []
		self.__dict = self.__filter
		self.__filter = filtr
		if not self.is_filter('antnee'): # no warranty in weapon/map precedence
			for item_class in ['weapon', 'jewelry', 'currency']:
				self.extra_base_types.extend(PoEItemData(item_class).get_items())
			# UTF-8 CSV files in db subdirectory = additional base_types
			# NOTE: don't use capital letters in the first line's attributes
			for key, extra_table in import_db('temporary_db').items():
				self.extra_base_types.extend([name.title() for name in get_db_column('name', extra_table)])
		self.hidden_classes = [] # if no current_class

	def run(self, filename = __default_output_filename):
		self.content = ''
		status = []
		for rarity in self.rarities:
			shield_class = 'Shield'
			self.current_class = None
			self.category_name = 'ARMOR'
			self.hidden_classes = shield_class
			status.append(self.set_content(True, rarity))
			self.current_class = shield_class
			status.append(self.set_content(True, rarity))
		save_file = open(filename, 'w')
		save_file.write(self.content.expandtabs(self.tab_len))
		save_file.close()
		if all(x == 0 for x in status):
			return 0
		return 1

	@property
	def database(self):
		return self.__database

	@database.setter
	def database(self, value):
		self.__database = value
		if value is not None:
			self.base_types = self.database.get_items()
			self.category_name = self.database.data_type.upper()
			# inform new database about required_classes
			try:
				self.hidden_classes = self.hidden_classes.copy()
			except AttributeError:
				pass # database is defined before hidden_classes

	@property
	def hidden_classes(self):
		return self.__hidden_classes

	@hidden_classes.setter
	def hidden_classes(self, classes):
		self.__hidden_classes = []
		if isinstance(classes, str):
			classes = [ classes ]
		for c in classes:
			if self.database.get_items(c):
				self.__hidden_classes.append(c)
		# IMPORTANT: don't touch base_types
		self.database.required_classes = set(self.database.get_classes()) - set(self.hidden_classes)

	@property
	def current_class(self):
		return self.__current_class

	@current_class.setter
	def current_class(self, value):
		if value is None:
			value = ''
		self.__current_class = value

	def is_filter(self, name):
		if self.__filter is not None:
			return self.__filter == name
		return False

	def display_lead(self, blink_bool):
		if blink_bool:
			return 'Show'
		else:
			return 'Hide'

	def display_title(self, text):
		self.content += self.comment_prefix.format(text=text)

	def set_content(self, lead, rarities = rarities, requirements = None):
		if self.database is None:
			print("Set a database first before calling {0}".format(self.set_content.__name__))
			return 0
		if requirements is None:
			requirements = self.database.get_requirements()

		# names' compression
		items_to_display = defaultdict(str)
		if not self.category_name:
			self.category_name = self.database.data_type.upper()
		if self.current_class:
			base_types = self.database.get_items(self.current_class)
		else:
			base_types = self.base_types
		for requirement in requirements:
			items_to_display[requirement] = ''
			items = self.database.get_items_by_requirement(requirement, self.current_class)
			if items:
				# IMPORTANT: precedence => remove previously filtered items
				base_types = [b for b in base_types if b not in items]
				# extend conflicting database
				conflict_base_types = base_types
				if not self.current_class:
					conflict_base_types.extend(self.extra_base_types)
				# compress names
				items_to_display[requirement] = ' '.join(quotify(c) for c in compress_names(items, conflict_base_types))
		# inform about unconsumed base_types by requirement
		if base_types:
			bt = base_types
			if not self.current_class:
				hidden_set = set({})
				for h in self.hidden_classes: # removed unused hidden_classes items
					hidden_set = hidden_set | set(self.database.get_items(h))
				bt = list(set(base_types) - hidden_set)
			print("{number} armor(s) {armor_names} unmatched by {requirement}".format(number=len(bt), armor_names=', '.join(quotify(b, '\s') for b in bt), requirement=' or '.join(requirements)))

		# template assignment
		template = self.display_lead(lead) + self.__template
		option = ''
		if self.current_class:
			option=self.__class_version_template.format(the_class = self.current_class)

		if isinstance(rarities, str):
			rarities = [rarities]
		for rarity in rarities:
			for requirement in requirements:
				if items_to_display[requirement]:
					self.content += template.format( requirement = requirement
																				 , option = option
																				 , category_name = self.category_name
																				 , the_class = PoEItemData.abbrev_classes(self.current_class)
																				 , rarity = rarity.capitalize()
																				 , items = items_to_display[requirement]
																				 , coloring = str(self.colors[rarity])
																				 )
		return 0

if __name__ == '__main__':
	# generate code for the Antnee's Classy Filter
	classy = ClassyGenerator('antnee')
	status = classy.run(output_filename)
	exit(status)
