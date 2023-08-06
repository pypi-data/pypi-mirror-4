#
# Get the directory where this script is defined, and where the baseline
# files are located.
#
import os
import sys
import string
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")

this_test_directory = dirname(abspath(__file__))+os.sep

benders_example_dir = dirname(dirname(dirname(dirname(dirname(abspath(__file__))))))+os.sep+"examples"+os.sep+"pyomo"+os.sep+"benders"+os.sep

coopr_bin_dir = dirname(dirname(dirname(dirname(dirname(dirname(dirname(abspath(__file__))))))))+os.sep+"bin"+os.sep

def filter_fn(line):
    tmp = line.strip()
    return tmp.startswith('WARNING') and 'CBC' in tmp

#
# Import the testing packages
#
import pyutilib.misc
import pyutilib.th as unittest
import pyutilib.subprocess
import coopr.plugins.solvers

cplex = None
cplex_available = False
try:
    cplex = coopr.plugins.solvers.CPLEX(keepfiles=True)
    cplex_available = (not cplex.executable() is None) and cplex.available(False)
except pyutilib.common.ApplicationError:
    cplex_available=False

gurobi = None
gurobi_available = False
try:
    gurobi = coopr.plugins.solvers.GUROBI(keepfiles=True)
    gurobi_available = (not gurobi.executable() is None) and gurobi.available(False)
except pyutilib.common.ApplicationError:
    gurobi_available=False

glpk = None
glpk_available = False
try:
    glpk = coopr.plugins.solvers.GLPK(keepfiles=True)
    glpk_available = (not glpk.executable() is None) and glpk.available(False)
except pyutilib.common.ApplicationError:
    glpk_available=False

@unittest.category('smoke')
class TestBenders(unittest.TestCase):

    def setUp(self):
        if os.path.exists(this_test_directory+'benders_cplex.out'):
            os.remove(this_test_directory+'benders_cplex.out')
        # IMPT: This step is key, as Python keys off the name of the module, not the location.
        #       So, different reference models in different directories won't be detected.
        #       If you don't do this, the symptom is a model that doesn't have the attributes
        #       that the data file expects.
        if "ReferenceModel" in sys.modules:
            del sys.modules["ReferenceModel"]

    @unittest.skipIf(not cplex_available, "The 'cplex' executable is not available")
    def test_benders_cplex(self):
        import subprocess
        out_file = open(this_test_directory+"benders_cplex.out",'w')
        os.chdir(benders_example_dir)
        subprocess.Popen(["lbin","python",benders_example_dir+"runbenders"],stdout=out_file).wait()
        os.chdir(this_test_directory)
        self.assertFileEqualsBaseline(this_test_directory+"benders_cplex.out", this_test_directory+"benders_cplex.baseline", tolerance=1e-7, filter=filter_fn)


if __name__ == "__main__":
    unittest.main()
