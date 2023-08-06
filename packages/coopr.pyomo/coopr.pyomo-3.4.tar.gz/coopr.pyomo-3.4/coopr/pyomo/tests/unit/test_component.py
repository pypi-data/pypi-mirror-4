#
# Unit Tests for components
#

import unittest
import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
from coopr.pyomo import *
import coopr.pyomo.base.component


class PyomoModel(unittest.TestCase):

    def test_component1(self):
        try:
            Component()
            self.fail("Expected DeveloperError")
        except coopr.pyomo.base.component.DeveloperError:
            pass

if __name__ == "__main__":
    unittest.main()
