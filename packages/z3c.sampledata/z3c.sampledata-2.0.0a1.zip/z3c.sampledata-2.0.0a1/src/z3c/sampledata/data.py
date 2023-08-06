##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Sample data for the media site
"""
import os
import random
import csv
from z3c.sampledata._compat import toUnicode

class DataGenerator(object):
    """Base functionality for data generators."""

    path = os.path.dirname(__file__)

    def __init__(self, seed, path=None):
        self.random = random.Random()
        self.random.seed(seed)
        if path is not None:
            self.path = path

    def readLines(self, filename):
        """Read in lines from file. Filename is relative to the module.

        Returned lines are stripped.
        """
        fullpath = os.path.join(self.path, filename)
        with open(fullpath) as file:
            lines = file.readlines()
        return [toUnicode(line.strip()) for line in lines]

    def readCSV(self, filename, delimiter=','):
        """Read in lines from file. Filename is relative to the module.

        Returned lines are stripped.
        """
        fullpath = os.path.join(self.path, filename)
        with open(fullpath) as file:
            return list(csv.reader(file, delimiter=delimiter))

    def files(self, path):
        """Get a list of files from a path.

        Subdirectories are ignored.
        """
        files = []
        append = files.append
        if os.path.exists(path):
            for f in os.listdir(path):
                fp = os.path.join(path, f)
                if os.path.isfile(fp):
                    append(fp)
        return files

