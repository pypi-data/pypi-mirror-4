###############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import os
import random
import csv


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
        lines = file(fullpath).readlines()
        return [unicode(line.strip()) for line in lines]

    def readCSV(self, filename, delimiter=','):
        """Read in lines from file. Filename is relative to the module.

        Returned lines are stripped.
        """
        fullpath = os.path.join(self.path, filename)
        f = file(fullpath)
        reader = csv.reader(f, delimiter=delimiter)
        return list(reader)

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

