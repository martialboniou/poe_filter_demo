#!/usr/bin/env python3
import unittest
from poe_utils import list_replace, list_replace_all, parse_multiline, parse_rows, match_name, quotify, find_unique_matchers, compress_names
from bs4 import BeautifulSoup

class TestPoEUtils(unittest.TestCase):

	def SetUp(self):
		pass

	def test_simple_list_replace(self):
		a = [1, 1, 2, 3]
		z = [4, 1, 2, 3]
		list_replace(a, 1, 4)
		self.assertEqual(a, z)

	def test_list_list_replace(self):
		a = [1, 3, 1, 3, 2]
		z = [4, 1, 3, 2]
		list_replace(a, [1, 3], 4)
		self.assertEqual(a, z)

	def test_list_list_list_replace(self):
		a = [1, 2, 3, 1, 2, 3]
		z = [4, 5, 6, 1, 2, 3]
		list_replace(a, [1, 2, 3], [4, 5, 6])
		self.assertEqual(a, z)

	def test_simple_list_replace_all(self):
		a = [1, 2, 1]
		z = [3, 2, 3]
		list_replace_all(a, 1, 3)
		self.assertEqual(a, z)

	def tests_list_list_replace_all(self):
		a = [1, 1, 2, 3, 2, 3, 4]
		z = [5, 5, 4]
		list_replace_all(a, [3, 1, 2], 5)
		self.assertEqual(a, z)

	def tests_list_list_list_replace_all(self):
		a = [1, 2, 3, 2, 3]
		z = [5, 6, 2, 3]
		list_replace_all(a, [3, 1, 2], [5, 6])
		self.assertEqual(a, z)

	def test_simple_parse_multiline(self):
		simple_element = '<td>Level<br/>XP Bar</td><td>100<br/>99%</td>'
		simple_soup = BeautifulSoup(simple_element)
		a = parse_multiline(simple_soup)
		z = [["Level", "XP Bar"], ["100", "99%"]]
		self.assertEqual(a, z)

	def test_advanced_parse_multiline(self):
		# not well-formed tables at pathofexile.com/item-data bad-formed require this
		simple_element = '<td>Minimum Strength<br/>Maximum Strength</td><td>1 to 50</td>'
		simple_soup = BeautifulSoup(simple_element)
		a = parse_multiline(simple_soup, True) # True => <number> to <number> as <br/>
		z = [["Minimum Strength", "Maximum Strength"], ["1", "50"]]
		self.assertEqual(a, z)

	def test_simple_row_parse_rows(self):
		simple_table = """<tbody>
	<tr>
		<th class="name">Name</th><th>Rank</th>
	</tr>
	<tr class="even"
		><td class="name">John</td><td>1</td>
	</tr>
</tbody>"""
		simple_soup = BeautifulSoup(simple_table)
		simple_rows = simple_soup.findAll('tr')
		a = parse_rows(simple_rows)
		z = [["Name", "Rank"], ["John", "1"]]
		self.assertEqual(a, z)

	def test_multirow_parse_rows(self):
		rowspan_table = """<tbody>
	<tr>
		<th class="name" rowspan="2">Name</th><th>Rank</th>
	</tr>
	<tr>
		<th>Level</th>
	</tr>
	<tr class="even">
		<td class="name" rowspan="2">John</td><td>1</td>
	</tr>
	<tr>
		<td>100</td>
	</tr>
</tbody>"""
		br_in_rowspan_soup = BeautifulSoup(rowspan_table, False)
		rowspan_rows = rowspan_soup.findAll('tr')
		a = parse_rows(rowspan_rows)
		z = [["Name", "Rank", "Level"], ["John", "1", "100"]]
		self.assertEqual(a, z)

	def test_multirow_parse_rows(self):
		br_in_rowspan_table = """<tbody>
	<tr>
		<th class="name" rowspan="2">Name</th><th>Rank</th><th>Class</th>
	</tr>
	<tr>
		<th>Stats</th><th>Values</th>
	</tr>
	<tr class="even">
		<td class="name" rowspan="2">Jessica</td><td>2</td><td>Priest</td>
	</tr>
	<tr>
		<td>Level<br/>XP Bar</td><td>100<br/>99%</td>
	</tr>
</tbody>"""
		br_in_rowspan_soup = BeautifulSoup(br_in_rowspan_table)
		br_in_rowspan_rows = br_in_rowspan_soup.findAll('tr')
		a = parse_rows(br_in_rowspan_rows)
		z = [["Name", "Rank", "Class", "Stats", "Values"], ["Jessica", "2", "Priest", ["Level", "XP Bar"], ["100", "99%"]]]
		self.assertEqual(a, z)

	def test_match_name(self):
		sentence = "This is my thrusting sword"
		self.assertTrue(match_name('thrust', sentence))

	def test_dummy_quotify(self):
		text = 'John'
		a = quotify(text)
		z = '"John"'
		self.assertEqual(a, z)

	def test_simple_quotify(self):
		texts = ['John Bigboote', 'Betty']
		a = [quotify(text, '\s') for text in texts]
		z = ['"John Bigboote"', 'Betty']
		self.assertEqual(a, z)

	def test_simple_find_unique_matchers(self):
		name = "Betty Boop"
		conflict = ["Betty Page"]
		a = find_unique_matchers(name, conflict)
		z = ["Boop"]
		self.assertEqual(a, z)

	def test_advanced_find_unique_matchers(self):
		name = "Bettie Mae Page"
		conflict = ["Bettie Kunst", "Mary Jane Page", "Mae Chang"]
		a = find_unique_matchers(name, conflict)
		z = ["Mae Page", "Bettie Mae"]
		self.assertEqual(a, z)

	def test_shortest_compress_names(self):
		names = ["Bettie Mae Page"]
		conflict = ["Mary Jane Page"]
		a = compress_names(names, conflict)
		z = ["Mae"] # shortest than "Bettie"
		self.assertEqual(a, z)

	def test_simple_compress_names(self):
		names = ["Bettie Mae Page", "Betty Boop"]
		conflict = ["Bettie Kunst", "Mary Jane Page", "Bettie Mae", "Mae Chang", "Betty Lee"]
		a = compress_names(names, conflict)
		z = ["Mae Page", "Boop"]
		self.assertEqual(a, z)

	def test_advanced_compress_names(self):
		names = ["Bettie Mae Page", "Betty Boop"]
		conflict = ["Bettie Kunst", "Mary Jane Page", "Bettie Mae", "Mae Chang", "Betty Lee", "Mae Page"]
		a = compress_names(names, conflict)
		z = ["Boop", "Bettie Mae Page"]
		self.assertEqual(a, z)

	def test_complete_compress_names(self):
		names = ["Bettie Mae Page", "Bettie Kunst", "Charly Bettie"]
		conflict = ["Mary Jane Page"]
		a = compress_names(names, conflict)
		z = ["Bettie"]
		self.assertEqual(a, z)

if __name__ == '__main__':
	unittest.main()
