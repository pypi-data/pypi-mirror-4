"""functional doctests.  This module collects all *.txt
files in the tests directory and runs them. (stolen from Ploneboard)
"""

import os, sys

import glob
import doctest
import unittest
from Globals import package_home
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

from collective.MockMailHost.config import GLOBALS

# Load products
from collective.MockMailHost.tests.MockMailHostTC import FunctionalTestCase

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def list_doctests():
    home = package_home(GLOBALS)
    return [filename for filename in
            glob.glob(os.path.sep.join([home, 'tests', '*.txt']))]

def test_suite():

    filenames = list_doctests()

    return unittest.TestSuite(
        [Suite(os.path.basename(filename),
               optionflags=OPTIONFLAGS,
               package='collective.MockMailHost.tests',
               test_class=FunctionalTestCase)
         for filename in filenames]
        )
