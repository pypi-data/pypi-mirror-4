#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**nodes.py**

**Platform:**
	Windows, Linux, Mac Os X.

**Description:**
	This module defines the :class:`sibl_gui.components.core.templatesOutliner.templatesOutliner.TemplatesOutliner`
	Component Interface class nodes.

**Others:**

"""

#**********************************************************************************************************************
#***	Future imports.
#**********************************************************************************************************************
from __future__ import unicode_literals

#**********************************************************************************************************************
#***	External imports.
#**********************************************************************************************************************
from PyQt4.QtCore import Qt

#**********************************************************************************************************************
#***	Internal imports.
#**********************************************************************************************************************
import foundations.verbose
import sibl_gui.ui.nodes

#**********************************************************************************************************************
#***	Module attributes.
#**********************************************************************************************************************
__author__ = "Thomas Mansencal"
__copyright__ = "Copyright (C) 2008 - 2013 - Thomas Mansencal"
__license__ = "GPL V3.0 - http://www.gnu.org/licenses/"
__maintainer__ = "Thomas Mansencal"
__email__ = "thomas.mansencal@gmail.com"
__status__ = "Production"

__all__ = ["LOGGER", "SoftwareNode"]

LOGGER = foundations.verbose.installLogger()

#**********************************************************************************************************************
#***	Module classes and definitions.
#**********************************************************************************************************************
class SoftwareNode(sibl_gui.ui.nodes.GraphModelNode):
	"""
	This class factory defines :class:`sibl_gui.components.core.templatesOutliner.templatesOutliner.TemplatesOutliner`
		Component Interface class Model software node.
	"""

	__family = "Software"
	"""Node family. ( String )"""

	def __init__(self,
				name=None,
				parent=None,
				children=None,
				roles=None,
				nodeFlags=int(Qt.ItemIsSelectable | Qt.ItemIsEnabled),
				attributesFlags=int(Qt.ItemIsSelectable | Qt.ItemIsEnabled),
				iconSize=None,
				iconPlaceholder=None,
				**kwargs):
		"""
		This method initializes the class.

		:param name: Node name.  ( String )
		:param parent: Node parent. ( GraphModelNode )
		:param children: Children. ( List )
		:param roles: Roles. ( Dictionary )
		:param nodeFlags: Node flags. ( Integer )
		:param attributesFlags: Attributes flags. ( Integer )
		:param iconSize: Icon size.  ( String )
		:param iconPlaceholder: Icon placeholder.  ( QIcon )
		:param \*\*kwargs: Keywords arguments. ( \*\* )
		"""

		LOGGER.debug("> Initializing '{0}()' class.".format(self.__class__.__name__))

		sibl_gui.ui.nodes.GraphModelNode.__init__(self,
												name,
												parent,
												children,
												roles,
												nodeFlags,
												iconSize,
												iconPlaceholder,
												**kwargs)

		SoftwareNode.__initializeNode(self, attributesFlags)

	#******************************************************************************************************************
	#***	Class methods.
	#******************************************************************************************************************
	def __initializeNode(self, attributesFlags=int(Qt.ItemIsSelectable | Qt.ItemIsEnabled)):
		"""
		This method initializes the node.
		
		:param attributesFlags: Attributes flags. ( Integer )
		"""

		self["release"] = sibl_gui.ui.nodes.GraphModelAttribute(name="release",
															flags=int(Qt.ItemIsSelectable | Qt.ItemIsEnabled))
		self["version"] = sibl_gui.ui.nodes.GraphModelAttribute(name="version",
															flags=int(Qt.ItemIsSelectable | Qt.ItemIsEnabled))
