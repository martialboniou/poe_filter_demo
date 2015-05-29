#!/usr/bin/env python3
# python3 -m pip install BeautifulSoup4
from poe_item_data import PoEItemData

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

class Demo:
	__default_output_filename = 'filter.txt'
	__demo_template = '# {optional_class} - {requirement}\n\tRarity {rarity}\n\tBaseType {items}\n\tSetTextColor {coloring}\n\n'
	colors = {'normal': Color(190, 190, 190), 'magic' : Color(120, 120, 230)}
	rarities = ['normal', 'magic']
	tab_len = 4
	comment_spc_len = 4
	demo_comment_prefix = "### {text}\n\n"

	def __init__(self):
		self.armour = PoEItemData('armour')
		self.weapon = PoEItemData('weapon')

	def testing(self, filename = __default_output_filename):
		self.content = ''
		status = []
		self.display_title("Show Armour By Requirement Demo")
		status.append(self.show_all_gear_by_requirement(self.armour))
		self.display_title("Hide Weapon By Requirement Demo : STUPID! : Hide Weapon By Action coming soon")
		status.append(self.hide_class_by_attribute_requirement(self.weapon, 'One Hand', ['STR']))
		save_file = open(filename, 'w')
		save_file.write(self.content.expandtabs(self.tab_len))
		save_file.close()
		if all(x == 0 for x in status):
			return 0
		return 1

	def display_lead(self, blink_bool):
		if blink_bool:
			return 'Show'
		else:
			return 'Hide'

	def display_title(self, text):
		self.content += self.demo_comment_prefix.format(text=text)

	def display_items(self, items_list):
		return (' ').join('"{0}"'.format(item) for item in items_list)

	def set_demo_content(self, lead, database, rarities = rarities, requirements = None, item_class = ''):
		if requirements is None:
			requirements = database.get_requirements()
		if isinstance(rarities, str):
			rarities = [rarities]
		optional_class = item_class or 'Gear'
		for rarity in rarities:
			for requirement in requirements:
				items = self.display_items(database.get_items_by_requirement(requirement, item_class))
				if not items:
					return 1
				template = self.display_lead(lead) + self.comment_spc_len * ' ' + self.__demo_template
				self.content += template.format( requirement = requirement
																			 , optional_class = optional_class
																			 , rarity = rarity.capitalize()
																			 , items = items
																			 , coloring = str(self.colors[rarity])
																			 )
		return 0

	def show_all_gear_by_requirement(self, database):
			return self.set_demo_content(True, database)

	def hide_class_by_attribute_requirement(self, database, item_class, item_attribute):
		classes = database.get_classes(item_class)
		status = []
		for klass in classes:
			status.append(self.set_demo_content(False, database, 'normal', item_attribute, klass))
		if all(x == 0 for x in status):
			return 0
		return 1

if __name__ == '__main__':
	demo = Demo()
	status = demo.testing()
	exit(status)
