#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**recursiveRemove.py

**Platform:**
	Windows, Linux, Mac Os X.

**Description:**
	Recursion delete.

**Others:**

"""

#**********************************************************************************************************************
#***	Future imports.
#**********************************************************************************************************************
from __future__ import unicode_literals

#**********************************************************************************************************************
#***	Encoding manipulations.
#**********************************************************************************************************************
import sys

def _setEncoding():
	"""
	This definition sets the Application encoding.
	"""

	reload(sys)
	sys.setdefaultencoding("utf-8")

_setEncoding()

#**********************************************************************************************************************
#***	External imports.
#**********************************************************************************************************************
import os

#**********************************************************************************************************************
#***	Module attributes.
#**********************************************************************************************************************
__author__ = "Thomas Mansencal"
__copyright__ = "Copyright (C) 2008 - 2013 - Thomas Mansencal"
__license__ = "GPL V3.0 - http://www.gnu.org/licenses/"
__maintainer__ = "Thomas Mansencal"
__email__ = "thomas.mansencal@gmail.com"
__status__ = "Production"

__all__ = ["recursiveRemove", "remove"]

#**********************************************************************************************************************
#***	Module classes and definitions.
#**********************************************************************************************************************
def recursiveRemove(rootDirectory, pattern):
	"""
	This definition recursively deletes the matching items.

	:param rootDirectory: Directory to recurse. ( String )
	:param pattern: Pattern to match. ( String )
	"""

	if not os.path.exists(rootDirectory):
		return

	for root, dirs, files in os.walk(rootDirectory, followlinks=True):
		for item in files:
			itemPath = os.path.join(root, item).replace("\\", "/")
			if pattern in item:
				remove(itemPath)

def remove(item):
	"""
	This definition deletes given item.
	:param item: Item to delete. ( String )
	"""

	print("{0} | Removing file: '{1}'".format(remove.__name__, item))
	try:
		os.remove(item)
	except:
		print("{0} | '{1}' file removing failed!".format(remove.__name__, item))

if __name__ == "__main__":
	arguments = map(unicode, sys.argv)
	recursiveRemove(arguments[1], arguments[2])
