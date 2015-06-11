#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections import defaultdict
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *
import re
import fileinput
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QListView, QHBoxLayout, QVBoxLayout, QScrollArea, QAction, qApp, QWidget, QApplication, QMainWindow, QPushButton, QFormLayout, QFileDialog, QMessageBox)
from PyQt5.QtGui import *
#requires: PyQt5, pygments

# FIXME: early ALPHA version; works with same length keywords
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

class Classy_Smoother_Gui(QMainWindow):

	def __init__(self):
		super (Classy_Smoother_Gui, self).__init__()
		self.hide()
		self.initUI()

	def kill_on_init(self):
		QTimer.singleShot(0, app.quit)

	def initUI(self):
		data_found = False
		try:
			self.file_content = fileinput.input(sys.argv[1])
			self.file_content[0]
			self.file_info = QFileInfo(sys.argv[1])
		except (IndexError, FileNotFoundError):
			directory = QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0]
			directory += "/My Games/Path of Exile"
			fname = QFileDialog.getOpenFileName(None, 'Open file', directory)
			if fname[0]:
				try:
					self.file_content = fileinput.input(fname[0])
					self.file_content[0]
					self.file_info = QFileInfo(fname[0])
				except FileNotFoundError:
					pass
				else:
					data_found = True
		else:
			data_found = True
		if not data_found:
			self.kill_on_init()
		else:
			self.initProcess()
			self.initWindowUI()
			self.process.fetch_data() # to check if the filter is consistent

	def initProcess(self):
		lf = LootFilterLexer()
		self.process = SmartblockProcess(self.file_content)
		self.process.lexer = LootFilterLexer()
		self.smartblocks = self.process.get_smartblocks()

	def initWindowUI(self):
		self.resetButton = QPushButton("Reset")
		self.resetButton.setEnabled(False)
		self.resetButton.clicked.connect(self.reset)
		self.overwriteButton = QPushButton("Overwrite")
		self.overwriteButton.setStyleSheet("background-color: #EFC795")
		self.overwriteButton.setEnabled(False)
		self.overwriteButton.clicked.connect(self.overwrite)
		discardButton = QPushButton("Discard")
		discardButton.clicked.connect(app.quit)
		hbox = QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(self.overwriteButton)
		hbox.addWidget(self.resetButton)
		#hbox.addWidget(discardButton)
		vbox = QVBoxLayout()
		self.setWindowTitle('Classy Smoother GUI')
		self.view = QListView()
		self.setCentralWidget(QWidget())
		self.scrollLayout = QFormLayout()
		self.scrollWidget = QWidget()
		self.scrollWidget.setLayout(self.scrollLayout)
		vbox.addWidget(self.view) #(self.scrollArea)
		vbox.addLayout(hbox)
		self.scrollLayout.addRow(self.view)
		self.centralWidget().setLayout(vbox)
		self.model = QStandardItemModel(self.view)
		self.model.itemChanged.connect(self.on_item_changed)
		self.process.caller = self # to inform bad formed database
		self.statusBar().showMessage(self.file_info.fileName())
		for (check, text) in self.smartblocks:
			item = QStandardItem(text[1:]) # CAR is a comment hashtag
			item.setCheckable(True)
			if check == 'Show':
				item.setCheckState(Qt.Checked)
			self.model.appendRow(item)
		self.view.setModel(self.model)
		self.show()

	def on_item_changed(self, item):
		self.updatable(True)
		self.process.smartblock_update(item.row())

	def updatable(self, flag, external_call = False, end_process = False): # temporary hack
		reset_flag = False # hidden first
		if flag:
			if external_call:
				message = 'has non-updated changes'
			else:
				message = 'has changed'
				reset_flag = True
		else:
			if end_process:
				message = 'is saved'
			else:
				message = 'is up-to-date'
		self.statusBar().showMessage(self.file_info.fileName() + ' ' + message)
		self.resetButton.setEnabled(reset_flag)
		self.overwriteButton.setEnabled(flag)

	def overwrite(self):
		if self.process.save(self.file_info.absoluteFilePath()):
			self.updatable(False, False, True)

	def com(self, **kwargs):
		self.critical = None
		self.status = 'unchanged'
		self.hidden = False
		for name, value in kwargs.items():
			setattr(self, name, value)
		if self.critical is not None:
			QMessageBox.critical(self, "Critical", self.critical, QMessageBox.Ok)
			return
		self.updatable(self.status == 'changed', not self.hidden)

	def reset(self):
		for i in self.process.update_ix.copy():
			item = self.model.item(i)
			state = item.checkState()
			if state == Qt.Checked:
				item.setCheckState(Qt.Unchecked)
			else:
				item.setCheckState(Qt.Checked)

class SmartblockProcess():

	def __init__(self, lines = ['']):
		self.content = ''.join(lines)
		self._smartblocks = []
		self._known_states = []
		self.caller = None
		self.lexer = None

	@property
	def lexer(self):
		return self.__lexer

	@lexer.setter
	def lexer(self, value):
		self.__lexer = value
		self.__known_header = False
		self.__known_data = False
		self.__update_ix = set({}) # smartblocks indexes to update
		self.__repair_ix = set({}) # smartblocks indexes to repair
		self.__critical_message = '''Fatal error: inform the maintainer'''

	def get_smartblocks(self):
		if self.lexer is None:
			return []
		if not self.__known_header:
			self._smartblocks = []
			self._known_states = []
			self.block_locations = defaultdict(list)
			k_lens = (len(keywords[0]), len(keywords[1]))
			self.walker = iter(self.lexer.get_tokens_unprocessed(self.content))
			offset = 0
			# walk through the comment header (stop at the first Show/Hide block)
			# one rule: smartblocks precede Show/Hide blocks
			while True:
				try:
					index, tokenType, tokenValue = self.walker.__next__()
				except StopIteration:
					break
				if tokenType == Token.Comment.Single:
					m = re.match("#+\s+({0})\s*(#.*)".format(reserved), tokenValue)
					if m is not None:
						try:
							local_index = m.start(1)
							local_state, local_smartblock = m.group(1), m.group(2)
						except IndexError:
							pass # hmm
						else:
							local_smartblock = local_smartblock.strip() # remove whitespaces left by bad editors
							self._smartblocks.insert(0,  local_smartblock)
							self._known_states.insert(0, local_state)
							self.block_locations[local_smartblock] = [index + local_index]
				if tokenType == Token.Keyword.Reserved and tokenValue in keywords:
					break
			self.__known_header = True
		return zip(self._known_states, self._smartblocks)

	def fetch_data(self):
		if not self.__known_header:
			self.get_smartblocks()
		if self.__known_data:
			return
		index, tokenType, tokenValue = next(self.walker)
		# walk through the Show/Hide blocks
		while True:
			if tokenType == Token.Keyword.Reserved and tokenValue in keywords:
				try:
					self.walker.__next__() # Space
					_, tokenType, nextTokenValue = self.walker.__next__() # Comment
				except StopIteration:
					break
				nextTokenValue = nextTokenValue.strip() # remove whitespaces left by bad editors
				if tokenType == Token.Comment.Single and nextTokenValue in self._smartblocks:
					self.block_locations[nextTokenValue].append(index)
					# ensure the Show/Hide block is as declared
					if tokenValue != self._known_states[self._smartblocks.index(nextTokenValue)]:
						self.smartblock_update(nextTokenValue, True) # else force internal error
						if self.caller is not None:
							self.caller.com(status = 'changed')
			try:
				index, tokenType, tokenValue = self.walker.__next__()
			except StopIteration:
				break
		self.__known_data = True

	def smartblock_update(self, index, force_update = False):
		if isinstance(index, str):
			try:
				index = self._smartblocks.index(index.strip())
			except ValueError:
				return
		# internal error => filter to repair
		if force_update:
			self.__repair_ix.add(index)
		else:
			if index in self.update_ix:
				self.__update_ix.remove(index)
			else:
				self.__update_ix.add(index)
		if self.caller is None:
			return
		hidden = not not self.update_ix
		status = "changed" if not not self.__repair_ix or hidden else "unchanged"
		self.caller.com(status = status, hidden = hidden)

	@property
	def update_ix(self):
		return self.__update_ix

	def get_locations(self, index):
		try:
			key = self._smartblocks[index]
		except IndexError:
			self.caller.com(critical = self.__critical_message)
			return []
		return self.block_locations[key]

	def save(self, filename):
		if self.update():
			try:
				save_file = open(filename, 'w')
			except IOError:
				self.caller.com(critical = '''cannot write in {0}'''.format(filename))
				return False
			save_file.write(self.content)
			save_file.close()
			return True
		return False

	def update(self):
		if not self.__known_data:
			self.fetch_data()
		tag_positions = defaultdict(list)
		new_states = self._known_states.copy()
		# normal update
		for i in self.update_ix:
			# update known states
			if new_states[i] == keywords[0]:
				new_states[i] = keywords[1]
			else:
				new_states[i] = keywords[0]
			tag_positions[new_states[i]].extend(self.get_locations(i))
		# repair case
		for i in self.__repair_ix - self.update_ix:
			tag_positions[self._known_states[i]].extend(self.get_locations(i))
		# reset when update ok
		if self.update_content(tag_positions):
			self.__update_ix = set({})
			self.__repair_ix = set({})
			self._known_states = new_states
			return True
		return False

	def update_content(self, tag_positions):
		# tag_positions: new_label -> [positions]
		# FIXME: hide and show => same size / no offset implemented
		content = list(self.content) # as mutable string
		for label in keywords:
			previous_label = keywords[1] if label == keywords[0] else keywords[0]
			p_len = len(previous_label)
			for pos in tag_positions[label][::-1]: # reverse => no offset per cycle
				for _ in range(0, p_len):
					try:
						content.pop(pos)
					except IndexError:
						self.caller.com(critical = self.__critical_message)
						return False
				for c in label[::-1]:
					try:
						content.insert(pos,c)
					except IndexError:
						self.caller.com(critical = self.__critical_message)
						return False
		self.content = ''.join(content)
		return True


if __name__ == '__main__':
	app = QApplication(sys.argv)
	csg = Classy_Smoother_Gui()
	sys.exit(app.exec_())
