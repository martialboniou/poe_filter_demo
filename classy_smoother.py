#!/usr/bin/env python3
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *
import re
import fileinput
import sys
#python3 -m pip install pygments

keywords = ('Show', 'Hide')
reserved = '|'.join(keywords) # will be extended

class LootFilterLexer(RegexLexer):
	name = 'LootFilter'
	aliases = ['lootfilter']
	filenames = ['*.filter']

	tokens = {
			# minimalistic
			'root': [
				(r' *\n', Text),
				(r'^#.*$', Comment.Single),
				(r'^({0})(\s*)(#.*)$'.format(reserved), bygroups(Keyword.Reserved, Text, Comment.Single)),
				(r'{0}*$'.format(reserved), Keyword.Reserved),
				(r'^\s+([$A-Za-z]+?)(\s+)(.*?)$',
             bygroups(Name.Attribute, Text, String)),
			]
	}

def run():
	content = ''
	if not sys.argv[1:]:
		print('you must enter the filter filename')
		return 1
	try:
		fi = fileinput.input(sys.argv[1])
		fi[0]
	except FileNotFoundError:
		print('{0} not found'.format(sys.argv[1]))
		return 1
	for line in fi:
		content += line
	lf = LootFilterLexer()
	tags = []
	smartblocks = [] # for fast checking
	k_lens = (len(keywords[0]), len(keywords[1]))
	tk = iter(lf.get_tokens_unprocessed(content))
	array = list(content)
	offset = 0
	# one rule: smartblocks precede Show/Hide blocks
	while True:
		try:
			i, tokenType, tokenValue = tk.__next__()
		except StopIteration:
			break
		if tokenType == Token.Comment.Single:
			m = re.match("#+\s+({0})\s*(#.*)".format(reserved), tokenValue)
			if m is not None:
				try:
					tags.insert(0, m.group(1))
					smartblocks.insert(0, m.group(2))
				except IndexError:
					pass # hmm
		if tokenType == Token.Keyword.Reserved and tokenValue in keywords:
			try:
				tk.__next__() # Space
				n, tokenType, nextTokenValue = tk.__next__() # Comment
			except StopIteration:
				break
			if tokenType == Token.Comment.Single and nextTokenValue in smartblocks:
				idx = smartblocks.index(nextTokenValue)
				try:
					tagname = tags[idx]
				except IndexError:
					print('process error')
					continue
				if tagname != tokenValue:
					if tagname == keywords[0]:
						t_len = k_lens[0]
					else:
						t_len = k_lens[1]
					i += offset
					for _ in range(0, t_len):
						array.pop(i)
					array.insert(i, tagname)
					offset -= t_len - 1
	save_file = open(sys.argv[1], 'w')
	save_file.write(''.join(array))
	save_file.close()
	return 0

if __name__ == "__main__":
	status = run()
	sys.exit(status)
