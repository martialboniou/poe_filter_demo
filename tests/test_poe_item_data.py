#!/usr/bin/env python3
import unittest
from poe_item_data import PoEItemData


class TestPoEItemData(unittest.TestCase):

	def SetUp(self):
		self.database = PoEItemData('armour')

	def test_simple_abbrev_classes(self):
		class_names = ["One Hand Mace", "One Hand Axe", "Boots", "One Hand Sword", "Thrusting One Hand Sword"]
		new_class_names = ["One Hand", "Boot"]
		cn = PoEItemData.abbrev_classes(class_names)
		self.assertEqual(cn, new_class_names)

	def test_advanced_abbrev_classes(self):
		class_names = ["One Hand Sword"]
		precedence = ["Thrusting", "Two Hand Sword"]
		new_class_names = ["Sword"]
		cn = PoEItemData.abbrev_classes(class_names, precedence)
		self.assertEqual(cn, new_class_names)

if __name__ == '__main__':
	unittest.main()
