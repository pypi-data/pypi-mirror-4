#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**views.py**

**Platform:**
	Windows, Linux, Mac Os X.

**Description:**
	This module defines the :class:`umbra.components.factory.projectsExplorer.projectsExplorer.ProjectsExplorer`
	Component Interface class View.

**Others:**

"""

#**********************************************************************************************************************
#***	External imports.
#**********************************************************************************************************************
import logging
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QAbstractItemView

#**********************************************************************************************************************
#***	Internal imports.
#**********************************************************************************************************************
import foundations.core as core
import foundations.exceptions
import umbra.ui.views
from umbra.globals.constants import Constants

#**********************************************************************************************************************
#***	Module attributes.
#**********************************************************************************************************************
__author__ = "Thomas Mansencal"
__copyright__ = "Copyright (C) 2008 - 2012 - Thomas Mansencal"
__license__ = "GPL V3.0 - http://www.gnu.org/licenses/"
__maintainer__ = "Thomas Mansencal"
__email__ = "thomas.mansencal@gmail.com"
__status__ = "Production"

__all__ = ["LOGGER", "Projects_QTreeView"]

LOGGER = logging.getLogger(Constants.logger)

#**********************************************************************************************************************
#***	Module classes and definitions.
#**********************************************************************************************************************
class Projects_QTreeView(umbra.ui.views.Abstract_QTreeView):
	"""
	This class is used to display Projects.
	"""

	@core.executionTrace
	def __init__(self, parent, model=None, readOnly=False):
		"""
		This method initializes the class.

		:param parent: Object parent. ( QObject )
		:param model: Model. ( QObject )
		:param readOnly: View is read only. ( Boolean )
		"""

		LOGGER.debug("> Initializing '{0}()' class.".format(self.__class__.__name__))

		umbra.ui.views.Abstract_QTreeView.__init__(self, parent, readOnly)

		# --- Setting class attributes. ---
		self.__treeViewIndentation = 15

		self.setModel(model)

		Projects_QTreeView.__initializeUi(self)

	#******************************************************************************************************************
	#***	Attributes properties.
	#******************************************************************************************************************
	@property
	def treeViewIndentation(self):
		"""
		This method is the property for **self.__treeViewIndentation** attribute.

		:return: self.__treeViewIndentation. ( Integer )
		"""

		return self.__treeViewIndentation

	@treeViewIndentation.setter
	@foundations.exceptions.exceptionsHandler(None, False, foundations.exceptions.ProgrammingError)
	def treeViewIndentation(self, value):
		"""
		This method is the setter method for **self.__treeViewIndentation** attribute.

		:param value: Attribute value. ( Integer )
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "treeViewIndentation"))

	@treeViewIndentation.deleter
	@foundations.exceptions.exceptionsHandler(None, False, foundations.exceptions.ProgrammingError)
	def treeViewIndentation(self):
		"""
		This method is the deleter method for **self.__treeViewIndentation** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "treeViewIndentation"))

	#******************************************************************************************************************
	#***	Class methods.
	#******************************************************************************************************************
	@core.executionTrace
	def __initializeUi(self):
		"""
		This method initializes the Widget ui.
		"""

		self.setAutoScroll(True)
		self.setIndentation(self.__treeViewIndentation)
		self.setRootIsDecorated(False)
		self.setDragDropMode(QAbstractItemView.DragOnly)

		self.header().hide()

		self.setSortingEnabled(True)
		self.sortByColumn(0, Qt.AscendingOrder)

		self.__setDefaultUiState()

		# Signals / Slots.
		self.model().modelReset.connect(self.__setDefaultUiState)

	@core.executionTrace
	def __setDefaultUiState(self):
		"""
		This method sets the Widget default ui state.
		"""

		LOGGER.debug("> Setting default View state!")

		if not self.model():
			return

		self.expandAll()

	@core.executionTrace
	@foundations.exceptions.exceptionsHandler(None, False, Exception)
	def setModel(self, model):
		"""
		This method reimplements the **umbra.ui.views.Abstract_QTreeView.setModel** method.
		
		:param model: Model to set. ( QObject )
		"""

		LOGGER.debug("> Setting '{0}' model.".format(model))

		if not model:
			return

		umbra.ui.views.Abstract_QTreeView.setModel(self, model)
