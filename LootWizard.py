#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections import defaultdict
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *
import re
import fileinput
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QTreeView, QHBoxLayout, QVBoxLayout, QScrollArea, QAction, qApp, QWidget, QApplication, QMainWindow, QPushButton, QFormLayout, QFileDialog, QMessageBox, QCheckBox, QSizePolicy, QDialog)
from PyQt5.QtGui import *
#requires: PyQt5, pygments

# FIXME: early ALPHA version; works with same length keywords
keywords = ('Show', 'Hide')
reserved = '|'.join(keywords) # will be extended
smartblock_separator = ' - '

# - Lexer
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

# - View
class LootWizard(QMainWindow):

	def __init__(self):
		super (LootWizard, self).__init__()
		self.hide()
		self._upToDateMessage = 'is up-to-date'
		self.initUI()

	def kill_on_init(self):
		QTimer.singleShot(0, app.quit)

	def initUI(self):
		data_found = False
		try:
			self.__getFileinfo(sys.argv[1])
		except (IndexError, FileNotFoundError):
			directory = QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0]
			directory += "/My Games/Path of Exile"
			fname = QFileDialog.getOpenFileName(None, 'Open file', directory)
			if fname[0]:
				try:
					self.__getFileinfo(fname[0])
				except FileNotFoundError:
					pass
				else:
					data_found = True
		else:
			data_found = True
		if not data_found:
			self.kill_on_init()
		else:
			self.initWindowUI()

	def initWindowUI(self):
		self.resetButton = QPushButton("Reset")
		self.resetButton.setEnabled(False)
		self.resetButton.clicked.connect(self.reset)
		self.orphanButton = SquareButton("+")
		self.orphanButton.hide()
		self.overwriteButton = QPushButton("Overwrite")
		self.overwriteButton.setStyleSheet("background-color: #EFC795")
		self.overwriteButton.setEnabled(False)
		self.overwriteButton.clicked.connect(self.overwrite)
		self.forceCheckBox = QCheckBox("&Always inherit")
		self.forceCheckBox.setToolTip('Smartblocks inherit from virtual blockgroups.<br/>Check me to change from a <b>smartblock</b> parent.')
		self.forceCheckBox.hide()
		hbox = QHBoxLayout()
		hbox2 = QHBoxLayout()
		hbox2.addWidget(self.forceCheckBox)
		hbox.addLayout(hbox2)
		hbox.addWidget(self.orphanButton)
		hbox.addStretch(1)
		hbox.addWidget(self.overwriteButton)
		hbox.addWidget(self.resetButton)
		vbox = QVBoxLayout()
		self.setWindowTitle('Loot Wizard')
		self.view = QTreeView()
		self.setCentralWidget(QWidget())
		self.scrollLayout = QFormLayout()
		self.scrollWidget = QWidget()
		self.scrollWidget.setLayout(self.scrollLayout)
		self.orphanDialog = OrphanDialog(self)
		self.orphanButton.clicked.connect(self.openOrphans)
		vbox.addWidget(self.view)
		vbox.addLayout(hbox)
		self.scrollLayout.addRow(self.view)
		self.centralWidget().setLayout(vbox)
		self.model = SmartblockModel(self.file_content, self)
		self.statusBar().showMessage(self.file_info.fileName() + ' ' + self._upToDateMessage)
		self.forceCheckBox.stateChanged.connect(self.switchforce)
		self.view.setModel(self.model)
		self.view.expandAll()
		self.view.setAlternatingRowColors(True)
		self.resize(300, 600)
		self.show()

	def inform(self, flag, external_call = False, end_process = False):
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
				message = self._upToDateMessage
		self.statusBar().showMessage(self.file_info.fileName() + ' ' + message)
		self.resetButton.setEnabled(reset_flag)
		self.overwriteButton.setEnabled(flag)

	def displayOrphan(self, display = True):
		# self.displayButton(self.orphanButton, display)
		pass

	def displayInheritance(self, display = True):
		self.displayButton(self.forceCheckBox, display)

	def displayButton(self, btn, display = True):
		if display:
			btn.show()
		else:
			btn.hide()

	def switchforce(self, state):
		self.model.forceInheritance = state == Qt.Checked

	def overwrite(self):
		self.overwriteButton.setEnabled(False)
		self.resetButton.setEnabled(False) # TODO: disable from elsewhere ?!
		if self.model.save(self.file_info.absoluteFilePath()):
			self.inform(False, False, True)

	def reset(self):
		self.model.resetStatus()

	def __getFileinfo(self, filename):
		self.file_content = ''.join(fileinput.input(filename))
		self.file_info = QFileInfo(filename)

	def openOrphans(self):
		self.orphanDialog.show()

class SquareButton(QPushButton):

	def __init__(self, label = '', parent = None):
		super(SquareButton, self).__init__(label)
		self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

	def resizeEvent(self, e):
		size = QSize(10, 10)
		size.scale(e.size(), Qt.KeepAspectRatio)
		self.setMinimumWidth(self.height())
		self.resize(size)

class OrphanDialog(QDialog):

	def __init__(self, parent = None):
		super(OrphanDialog, self).__init__(parent)

# - Model
class SmartblockModel(QAbstractItemModel):

	def __init__(self, data, inParent = None):
		super(SmartblockModel, self).__init__(inParent)
		self.data = SmartblockData(data)
		self.window = inParent
		# out of Muldini's Blockgroup Convention
		self.hasSpecialSmartblock = False # unofficial smartblock parent support
		self.forceInheritance = False
		# end - out
		self.smartblocks = self.create_smartblocks()
		self.rootItem = RootTreeItem()
		self.setupModelData()
		self.__resetCall = False
		self.__critical_message = '''Fatal error: inform the maintainer'''

	def informWindow(self, **kwargs):
		if self.window is not None:
			self.critical = None
			self.status = 'unchanged'
			self.hidden = False
			for name, value in kwargs.items():
				setattr(self, name, value)
			if self.critical is not None:
				QMessageBox.critical(self.window, "Critical", self.critical, QMessageBox.Ok)
				return
			self.window.inform(self.status == 'changed', not self.hidden)

	def __get_data(self):
		self.data.lexer = LootFilterLexer()
		self.data.fetch_data() # to get orphans or check consistency (TODO: orphans unmanaged yet)
		if self.data.updates:
			self.informWindow(status = 'changed')
		self.smartblocks = self.create_smartblocks()

	def create_smartblocks(self):
		if self.data.lexer is None:
			self.__get_data()
			return self.smartblocks
		sbs = self.data.get_smartblocks()
		smartblocks = []
		leaves = []
		smartblock_collector = defaultdict(Smartblock)
		for idx, (status, comment) in enumerate(sbs):
			name = comment[1:]
			l = name.split(smartblock_separator)
			root = l[0]
			full_l = []
			len_l = len(l)
			if len_l > 1:
				for i in range(2, len_l+1):
					full_l.append(smartblock_separator.join(l[0:i]))
			full_l.insert(0, root)
			leaves.append(name)
			parent = None
			for n, full_n in zip(l, full_l):
				if full_n in smartblock_collector.keys():
					sm = smartblock_collector[full_n]
					if sm.index is None and full_n in leaves:
						sm.index = idx # case: 'This' defined after 'This - That'
						sm.status = status
				else:
					if full_n == full_l[-1]:
						index = idx
					else:
						index = None
					# status of unreferenced nodes is None by default; updated later
					sm = Smartblock(index, (None if index is None else status, n))
					smartblock_collector[full_n] = sm
					if full_n == full_l[0]: # leaf
						smartblocks.append(sm)
				if parent is not None:
					if sm not in parent.children: # TODO: test me
						parent.addChild(sm)
				parent = sm
		return smartblocks

	def __processData(self, tree_item, node):
		for d in node.children:
			if d.isBadParent():
				self.hasSpecialSmartblock = True
			item = SmartblockTreeItem(tree_item, d)
			self.__processData(item, d) # process children first then update status
			tree_item.AddChild(item)
		smartblock = tree_item.smartblock
		if smartblock.status is None:
			for key in keywords:
				if all(n.status == key for n in node.all_children): # IMPORTANT: all_children!
					tree_item.smartblock.status = key
					break

	def setupModelData(self):
		for smart in self.smartblocks:
			if smart.isBadParent():
				self.hasSpecialSmartblock = True
			smart_item = SmartblockTreeItem(self.rootItem, smart)
			self.__processData(smart_item, smart)
			self.rootItem.AddChild(smart_item)
			self.updates = set({}) # collect indexes of smartblocks to update (faster)
			self.indexes = set({}) # collect indexes in tree model to reset   (faster)
			if self.hasSpecialSmartblock and self.window is not None:
				self.window.displayInheritance()
			if self.data.hasOrphan():
				self.window.displayOrphan()

	def index(self, row, column, parentindex):
		if not self.hasIndex(row, column, parentindex):
			return QModelIndex()
		parent_item = None
		if not parentindex.isValid():
			parent_item = self.rootItem
		else:
			parent_item = parentindex.internalPointer()
		child_item = parent_item.GetChild(row)
		if child_item:
			return self.createIndex(row, column, child_item)
		else:
			return QModelIndex()

	def parent(self, childindex):
		if not childindex.isValid():
			return QModelIndex()
		child_item = childindex.internalPointer()
		if not child_item:
			return QModelIndex()
		parent_item = child_item.GetParent()
		if parent_item == self.rootItem:
			return QModelIndex()
		return self.createIndex(parent_item.Row(), 0, parent_item)

	def rowCount(self, parentindex):
		if parentindex.column() > 0:
			return 0
		item = None
		if not parentindex.isValid():
			item = self.rootItem
		else:
			item = parentindex.internalPointer()
		return item.GetChildCount()

	def columnCount(self, parentindex):
		if not parentindex.isValid():
			return self.rootItem.ColumnCount()
		return parentindex.internalPointer().ColumnCount()

	def data(self, index, role):
		if not index.isValid():
			return QVariant()
		node = index.internalPointer()
		col = index.column()
		if role == Qt.DisplayRole:
			data = node.Data(col)
			return data
		if role == Qt.CheckStateRole:
			if node.Status(col) is None:
				return QVariant(Qt.PartiallyChecked)
			if node.Status(col) == keywords[0]:
				return QVariant(Qt.Checked)
			else:
				return QVariant(Qt.Unchecked)
		if role == Qt.SizeHintRole:
			return QSize(20, 20)
		if role == Qt.FontRole and node.Index(col) is None:
			font = QFont()
			font.setBold(True)
			return QVariant(font)
		return QVariant()

	def setData(self, index, value, role):
		if not index.isValid():
			return False
		if role == Qt.CheckStateRole:
			for checkSymbol, keyword in zip(
					[Qt.Checked, Qt.Unchecked],
					keywords):
				if value == checkSymbol:
					# refresh status and set updates
					self.refreshData(index, keyword)
					# propagate to parent
					parent_index = self.parent(index)
					if parent_index.isValid():
						self.dataChanged.emit(parent_index, index)
					# propagate to children if not reset
					self.emitDataChangedForChildren(index)
					break
		status, hidden = 'changed', False
		if self.updates:
			hidden = True
		else:
			if not self.data.updates:
				status = 'unchanged'
		self.informWindow(status = status, hidden = hidden)
		return True

	def emitDataChangedForChildren(self, index):
		count = self.rowCount(index)
		if count:
			for child_row in range(0, count):
				child_index = self.index(child_row, index.column(), index)
				self.emitDataChangedForChildren(child_index)
				self.dataChanged.emit(index, child_index)

	def flags(self, index):
		if index.column() == 0:
			return QAbstractItemModel.flags(self, index) | Qt.ItemIsUserCheckable

	def headerData(self, column, orientation, role):
		if (orientation == Qt.Horizontal and role == Qt.DisplayRole):
			try:
				return self.rootItem.Data(column)
			except IndexError:
				pass
			return QVariant()

	def refreshData(self, index, new_status, internalCall = False):
		node = index.internalPointer()
		col = index.column() # unused; for evolution purpose
		if isinstance(node, SmartblockTreeItem):
			inode = node.Index(col)
			status = node.Status(col)
			count = self.rowCount(index)
			if inode is not None:
				if status is not None:
					if node.SetStatus(new_status, col): # + update parent
						if inode in self.updates:
							self.updates.remove(inode)
							self.indexes.remove(index)
						else:
							self.updates.add(inode)
							self.indexes.add(index)
				if self.__resetCall:
					return # simple change on reset (don't ever touch the children!)
				if not internalCall and not self.forceInheritance: # + inode is not None
					return	# ie forceInheritance updates ALL children
			if count:
				for child_row in range(0, count):
					child_index = self.index(child_row, col, index)
					self.refreshData(child_index, new_status, True)

	def save(self, filename):
		if self.data.update(self.updates):
			self.updates = set({})
			self.indexes = set({})
			try:
				save_file = open(filename, 'w')
			except IOError:
				self.informWindow(critical = '''cannot write in {0}'''.format(filename))
				return False
			save_file.write(self.data.content)
			save_file.close()
			return True
		return False

	def resetStatus(self):
		# FIXME: disconnect self.window.view
		self.__resetCall = True
		role = Qt.CheckStateRole
		for index in self.indexes.copy():
			state = self.itemData(index)[role]
			new_state = Qt.Unchecked if state == Qt.Checked else Qt.Checked
			self.setData(index, new_state, role)
		if not self.updates:
			self.indexes = set({})
		else:
			self.informWindow(critical = '''bad status\nerror in {0}'''.format(self.resetStatus.__name__))
		self.__resetCall = False

# - Model - Item
class BaseTreeItem(object):
	def __init__(self, inParentItem):
		self.parent = inParentItem
		self.children = []

	def AddChild(self, inChild):
		self.children.append(inChild)

	def GetChild(self, row):
		return self.children[row]

	def GetChildCount(self):
		return len(self.children)

	def GetParent(self):
		return self.parent

	def Row(self):
		if self.parent:
			return self.parent.children.index(self)
		return 0

	def ColumnCount(self):
		return 1

	def Data(self, inColumn):
		raise Exception("Override me!")

	def Copy(self, baseTreeItem):
		pass

class RootTreeItem(BaseTreeItem):
	def __init__(self):
		super(RootTreeItem, self).__init__(None) # no parent item

	def Data(self, inColumn):
		if inColumn == 0:
			return "Smartblocks"
		return ''

class SmartblockTreeItem(BaseTreeItem):
	def __init__(self, inParent, inSmartblock):
		super(SmartblockTreeItem, self).__init__(inParent)
		self.smartblock = inSmartblock

	def Data(self, inColumn):
		if inColumn == 0:
			return self.smartblock.name
		return ''

	def Status(self, inColumn):
		if inColumn == 0:
			return self.smartblock.status
		raise ValueError('no status')

	def SetStatus(self, status, inColumn):
		changed = False
		if inColumn == 0 and not isinstance(self, RootTreeItem):
			changed = self.smartblock.updateStatus(status)
			# update parent display
			self._UpdateParent(inColumn)
		else:
			raise ValueError('no status')
		return changed

	def _UpdateParent(self, inColumn):
		parent = self.GetParent()
		if isinstance(parent, RootTreeItem):
			return
		parent_index = parent.Index(inColumn)
		if parent_index is None:
			found = False
			children = parent
			for key in keywords:
				children = parent.smartblock.all_children # IMPORTANT: check all heirs!
				if all(child.status == key for child in children):
					parent.smartblock.updateStatus(key)
					found = True
					break
			if not found:
				parent.smartblock.updateStatus(None)
		parent._UpdateParent(inColumn)

	def Index(self, inColumn):
		if inColumn == 0:
			return self.smartblock.index
		raise IndexError('no index')

# - Data
class SmartblockData():

	def __init__(self, lines = ''):
		self.content = lines
		self._smartblocks = []
		self._orphans = []
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
		self.updates = set({}) # smartblocks indexes to repair

	@property
	def orphans(self):
		return self._orphans

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
							self._smartblocks.append(local_smartblock)
							self._known_states.append(local_state)
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
				if tokenType == Token.Comment.Single:
					self.block_locations[nextTokenValue].append(index)
					if nextTokenValue not in self._smartblocks and nextTokenValue not in self._orphans: # collect orphans too
						self._orphans.append(nextTokenValue)
					# ensure the Show/Hide block is as declared
					if nextTokenValue in self._smartblocks and tokenValue != self._known_states[self._smartblocks.index(nextTokenValue)]:
						self.updates.add(self._smartblocks.index(nextTokenValue))
			try:
				index, tokenType, tokenValue = self.walker.__next__()
			except StopIteration:
				break
		self.__known_data = True
		#print(str(self._orphans))

	def get_locations(self, index):
		try:
			key = self._smartblocks[index]
		except IndexError:
			return []
		return self.block_locations[key]

	def update(self, updates):
		if not self.__known_data:
			self.fetch_data()
		tag_positions = defaultdict(list)
		new_states = self._known_states.copy()
		# normal update
		for i in updates:
			# update known states
			if new_states[i] == keywords[0]:
				new_states[i] = keywords[1]
			else:
				new_states[i] = keywords[0]
			tag_positions[new_states[i]].extend(self.get_locations(i))
		# repair case
		for i in self.updates - updates:
			test = tag_positions[self._known_states[i]]
			test.extend(self.get_locations(i))
		# reset when update ok
		if self.update_content(tag_positions):
			self.updates = set({})
			self._known_states = new_states
			return True
		return False

	def update_content(self, tag_positions):
		# tag_positions: new_label -> [positions]
		# FIXME: hide and show => same size / no offset implemented
		content = list(self.content) # as mutable string; TODO: use bytearray ASAP
		for label in keywords:
			previous_label = keywords[1] if label == keywords[0] else keywords[0]
			p_len = len(previous_label)
			for pos in tag_positions[label][::-1]: # reverse => no offset per cycle
				for _ in range(0, p_len):
					try:
						content.pop(pos)
					except IndexError:
						return False
				for c in label[::-1]:
					try:
						content.insert(pos,c)
					except IndexError:
						return False
		self.content = ''.join(content)
		return True

	def hasOrphan(self):
		return not not self._orphans

# - Data - Item
class Smartblock():

	def __init__(self, inIndex, inSmartblockData):
		self.__children = []
		self.status = inSmartblockData[0]
		self.name = inSmartblockData[1]
		self.index = inIndex # None if virtual group

	def isBadParent(self):
		# unofficial: real smartblock as virtual node
		return self.index is not None and len(self.children) > 0

	@property
	def children(self):
		return self.__children

	@children.setter
	def children(self, inSmartblock):
		self.__children.append(inSmartblock)

	def addChild(self, inSmartblock): # interface
		self.children = inSmartblock

	@property
	def heirs(self):
		# unofficial: get subchildren when no virtual group (as siblings)
		children = self.children
		for child in self.children:
			if child.index is not None:
				children = child.heirs + children
		return children

	all_children = heirs

	def updateStatus(self, status):
		if self.status != status:
			self.status = status
			return True
		return False

	def count(self):
		return len(self.children)

	def __str__(self): # NOTE: unused (written for tests!)
		return "Smartblock{"+"{0}{1}{2}{3}".format(
				self.name, '' if self.index is None else '[index='+str(self.index)+']',
				'' if not self.children else '({0})'.format('|'.join([str(c) for c in self.children])),
				'' if self.status is None else ' -> {0}'.format(self.status)
				)+"}"

if __name__ == '__main__':
	app = QApplication(sys.argv)
	lf = LootWizard()
	sys.exit(app.exec_())
