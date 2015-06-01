#!/usr/bin/env python3
# python3 -m pip install BeautifulSoup4
from poe_item_data import PoEItemData
from poe_utils import compress_names
from collections import defaultdict

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
	__armor_template = '#Gear - {requirement} Armor\n\tRarity {rarity}\n\tBaseType {items}\n\tSetTextColor {coloring}'+11*' '+'#{rarity} "Junk"\n\n'
	__class_template = '#Gear - {requirement} Armor ({the_class})\n\tClass {the_class}\n\tBaseType {items}\n\tRarity {rarity}\n\tSetTextColor {coloring}'+11*' '+'#{rarity} "Junk"\n\n'
	colors = {'normal': Color(190, 190, 190), 'magic' : Color(120, 120, 230)}
	rarities = ['normal', 'magic']
	tab_len = 4
	comment_prefix = "### {text}\n\n"
	__filter = None

	def __init__(self, filter = None):
		self.armour = PoEItemData('armour')
		self.base_types = self.armour.get_items()
		self.__dict = self.__filter
		self.__filter = filter
		if not self.is_filter('antnee'): # no warranty in weapon/map precedence
			for item_class in ['weapon', 'jewelry', 'currency']:
				self.base_types.extend(PoEItemData(item_class).get_items())
			self.base_types.extend(['Arena Pit']) # temporary: maps, maraketh weapons...

	def run(self, filename = __default_output_filename):
		self.content = ''
		status = []
		for rarity in self.rarities:
			status.append(self.set_content(True, self.armour, rarity))
			status.append(self.set_content(True, self.armour, rarity, None, 'Shield'))
		save_file = open(filename, 'w')
		save_file.write(self.content.expandtabs(self.tab_len))
		save_file.close()
		if all(x == 0 for x in status):
			return 0
		return 1

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

	def display_items(self, items_list):
		return (' ').join('"{0}"'.format(item) for item in items_list)

	def set_content(self, lead, database, rarities = rarities, requirements = None, item_class = ''):
		if requirements is None:
			requirements = database.get_requirements()

		# names' compression
		items_to_display = defaultdict(str)
		base_types = self.base_types if not item_class else database.get_items(item_class)
		for requirement in requirements:
			items_to_display[requirement] = ''
			items = database.get_items_by_requirement(requirement, item_class)
			if items:
				base_types = [bt for bt in base_types if bt not in items]
				items_to_display[requirement] = self.display_items(compress_names(items, base_types))

		# template assignment
		template = self.display_lead(lead) + 3 * ' '
		if not item_class:
			template += self.__armor_template
		else:
			template += self.__class_template

		if isinstance(rarities, str):
			rarities = [rarities]
		for rarity in rarities:
			for requirement in requirements:
				if items_to_display[requirement]:
					self.content += template.format( requirement = requirement
																				 , the_class = item_class
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
