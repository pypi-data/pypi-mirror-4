import os
from os.path import join, dirname, abspath
import warnings

from coopr.pyomo import *
from coopr.opt import *
import pyutilib.th as unittest
from coopr.pyomo.tests.io import model_types
from coopr.pyomo.tests.io.writer_test_cases import testCases

thisDir = dirname(abspath( __file__ ))

# These are usually due to a bug in the latest version of the thirdparty solver
# Tests will be expected to fail. If they do not, that means the solver has been fixed
# and that particular case should no longer exist in the list of expected failures
ExpectedFailures = []
ExpectedFailures.append( ('cbc',
                          'lp',
                          model_types.duals_maximize,
                          "For a maximization problem where a variable is pushed to its "\
                          "lower bound, Cbc reports the reduced cost as a positive number. In "\
                          "practice this should be reported as a negative number. A ticket has "\
                          "been filed at:\nhttps://projects.coin-or.org/Cbc/ticket/125") )
ExpectedFailures.append( ('pico',
                          'nl',
                          model_types.duals_maximize,
                          "Pico classifies certain models with equality constraints as infeasible when "\
                          "using the NL file interface. A ticket has been filed.") )
ExpectedFailures.append( ('pico',
                          'nl',
                          model_types.duals_minimize,
                          "Pico classifies certain models with equality constraints as infeasible when "\
                          "using the NL file interface. A ticket has been filed.") )
ExpectedFailures.append( ('pico',
                          'nl',
                          model_types.inactive_index_LP,
                          "Pico reports the wrong objective function value.") )
ExpectedFailures.append( ('scip',
                          'nl',
                          model_types.simple_SOS2,
                          "SCIP (scipampl) does not recognize sos2 constraints inside NL files. "\
                          "A ticket has been filed.") )

def check_expected_failures(test_case, model_class):
    # If this situation is an expected failure then return the message why
    for case in ExpectedFailures:
        if (case[0] == test_case.name) and (case[1] == test_case.io) and (case[2] is model_class):
            return True, case[3]
    return False, ""

def CreateTestMethod(test_case, modelClass,symbolic_labels=False):
    
    # We do not want to test the plugin case on a model
    # class it is not capable of handling
    if modelClass().validateCapabilities(test_case) is False:
        return None

    def writer_test(self):
        # Instantiate the model class
        model_class = modelClass()
        save_filename = join(thisDir,test_case.name+"_"+test_case.io+"_"+model_class.descrStr()+".test.results")
        # cleanup possibly existing old test files
        try:
            os.remove(save_filename)
        except OSError:
            pass
        
        # Skip this test if the solver is not available on the system
        if test_case.available is False:
            #print test_case
            self.skipTest('Solver unavailable: '+test_case.name+' ('+test_case.io+')')
            return

        test_case.initialize()
        opt = test_case.solver

        if test_case.io == 'nl':
            self.assertEqual(opt.problem_format(), ProblemFormat.nl)
        elif test_case.io == 'lp':
            self.assertEqual(opt.problem_format(), ProblemFormat.cpxlp)
        elif test_case.io == 'python':
            self.assertEqual(opt.problem_format(), None)

        # check that the solver plugin is at least as capable as the
        # test_case advertises, otherwise the plugin capabilities need to be change
        # or the test case should be removed
        if not all(opt.has_capability(tag) is True for tag in test_case.capabilities):
            self.fail("Actual plugin capabilities are less than that of the "\
                      "of test case for the plugin: "+test_case.name+' ('+test_case.io+')')

        # Create the model instance and send to the solver
        model_class.generateModel()
        model = model_class.model
        self.assertTrue(model is not None)
        # Generates canonical repn for those writers that need it
        if test_case.io != 'nl':
            model.preprocess()

        # make sure we don't try to extract rc or dual suffixes from integer programs
        for suffix in test_case.import_suffixes:
            setattr(model,suffix,Suffix(direction=Suffix.IMPORT))

        # solve
        results = opt.solve(model,symbolic_solver_labels=symbolic_labels)
        model.load(results)
        model_class.saveCurrentSolution(save_filename,
                                        suffixes=test_case.import_suffixes)

        # There are certain cases where the latest solver version has a bug
        # so this should not cause a coopr test to fail
        is_expected_failure, failure_msg = check_expected_failures(test_case,modelClass)

        # validate the solution returned by the solver 
        rc = model_class.validateCurrentSolution(suffixes=test_case.import_suffixes)
        
        if is_expected_failure:
            if rc[0] is True:
                self.fail("\nThis test was marked as an expected failure but no failure occured. "\
                          "The reason given for the expected failure is:\n\n****\n"+failure_msg+"\n****\n\nPlease remove "\
                          "this case as an expected failure if the above issue has been corrected in "\
                          "the latest version of the solver.")
            else:
                warnings.warn( "\n\n**This test is failing but it has been marked as an expected failure "\
                               "due to a bug in the solver.\nSolver: %s\nWriter: %s\nModel:  %s\n"\
                                % (test_case.name,test_case.io,model_class.descrStr()) )
        elif rc[0] is False:
            self.fail("Solution mismatch for plugin "+test_case.name+' ('+test_case.io+") "\
                      "and problem type "+model_class.descrStr()+"\n"+rc[1]+"\n"+str(results.Solution(0)))

        # cleanup if the test passed
        try:
            os.remove(save_filename)
        except OSError:
            pass

    return writer_test

def addfntests(cls, tests, modelClass, symbolic_labels=False):
    for case in tests:
        test_method = CreateTestMethod(case, modelClass, symbolic_labels=symbolic_labels)
        if test_method is not None:
            if symbolic_labels is True:
                setattr(cls, "test_"+case.name+"_"+case.io+"_symbolic_labels", test_method)
            elif symbolic_labels is False:
                setattr(cls, "test_"+case.name+"_"+case.io+"_non_symbolic_labels", test_method)
            else:
                raise AssertionError("Bad value for create test method.")

class WriterTests_simple_LP(unittest.TestCase): pass
WriterTests_simple_LP = unittest.category('smoke','nightly','expensive')(WriterTests_simple_LP)
addfntests(WriterTests_simple_LP,testCases, model_types.simple_LP, symbolic_labels=False)
addfntests(WriterTests_simple_LP,testCases, model_types.simple_LP, symbolic_labels=True)

class WriterTests_block_LP(unittest.TestCase): pass
WriterTests_block_LP = unittest.category('smoke','nightly','expensive')(WriterTests_block_LP)
addfntests(WriterTests_block_LP,testCases, model_types.block_LP, symbolic_labels=False)
addfntests(WriterTests_block_LP,testCases, model_types.block_LP, symbolic_labels=True)

class WriterTests_inactive_index_LP(unittest.TestCase): pass
WriterTests_inactive_index_LP = unittest.category('smoke','nightly','expensive')(WriterTests_inactive_index_LP)
addfntests(WriterTests_inactive_index_LP,testCases, model_types.inactive_index_LP, symbolic_labels=False)
addfntests(WriterTests_inactive_index_LP,testCases, model_types.inactive_index_LP, symbolic_labels=True)

class WriterTests_simple_MILP(unittest.TestCase): pass
WriterTests_simple_MILP = unittest.category('nightly','expensive')(WriterTests_simple_MILP)
addfntests(WriterTests_simple_MILP,testCases, model_types.simple_MILP, symbolic_labels=False)
addfntests(WriterTests_simple_MILP,testCases, model_types.simple_MILP, symbolic_labels=True)

class WriterTests_simple_QP(unittest.TestCase): pass
WriterTests_simple_QP = unittest.category('nightly','expensive')(WriterTests_simple_QP)
addfntests(WriterTests_simple_QP,testCases, model_types.simple_QP, symbolic_labels=False)
addfntests(WriterTests_simple_QP,testCases, model_types.simple_QP, symbolic_labels=True)

class WriterTests_simple_MIQP(unittest.TestCase): pass
WriterTests_simple_MIQP = unittest.category('nightly','expensive')(WriterTests_simple_MIQP)
addfntests(WriterTests_simple_MIQP,testCases, model_types.simple_MIQP, symbolic_labels=False)
addfntests(WriterTests_simple_MIQP,testCases, model_types.simple_MIQP, symbolic_labels=True)

class WriterTests_simple_QCP(unittest.TestCase): pass
WriterTests_simple_QCP = unittest.category('nightly','expensive')(WriterTests_simple_QCP)
addfntests(WriterTests_simple_QCP,testCases, model_types.simple_QCP, symbolic_labels=False)
addfntests(WriterTests_simple_QCP,testCases, model_types.simple_QCP, symbolic_labels=True)

class WriterTests_simple_MIQCP(unittest.TestCase): pass
WriterTests_simple_MIQCP = unittest.category('nightly','expensive')(WriterTests_simple_MIQCP)
addfntests(WriterTests_simple_MIQCP,testCases, model_types.simple_MIQCP, symbolic_labels=False)
addfntests(WriterTests_simple_MIQCP,testCases, model_types.simple_MIQCP, symbolic_labels=True)

class WriterTests_simple_SOS1(unittest.TestCase): pass
WriterTests_simple_SOS1 = unittest.category('nightly','expensive')(WriterTests_simple_SOS1)
addfntests(WriterTests_simple_SOS1,testCases, model_types.simple_SOS1, symbolic_labels=False)
addfntests(WriterTests_simple_SOS1,testCases, model_types.simple_SOS1, symbolic_labels=True)

class WriterTests_simple_SOS2(unittest.TestCase): pass
WriterTests_simple_SOS2 = unittest.category('nightly','expensive')(WriterTests_simple_SOS2)
addfntests(WriterTests_simple_SOS2,testCases, model_types.simple_SOS2, symbolic_labels=False)
addfntests(WriterTests_simple_SOS2,testCases, model_types.simple_SOS2, symbolic_labels=True)

class WriterTests_duals_maximize(unittest.TestCase): pass
WriterTests_duals_maximize = unittest.category('nightly','expensive')(WriterTests_duals_maximize)
addfntests(WriterTests_duals_maximize,testCases, model_types.duals_maximize, symbolic_labels=False)
addfntests(WriterTests_duals_maximize,testCases, model_types.duals_maximize, symbolic_labels=True)

class WriterTests_duals_minimize(unittest.TestCase): pass
WriterTests_duals_minimize = unittest.category('nightly','expensive')(WriterTests_duals_minimize)
addfntests(WriterTests_duals_minimize,testCases, model_types.duals_minimize, symbolic_labels=False)
addfntests(WriterTests_duals_minimize,testCases, model_types.duals_minimize, symbolic_labels=True)

# A "solver should fail" test, which I am archiving for now
"""
            # If the solver is not capable of handling this
            # model class then we better get a failure here
            try:
                model.load(opt.solve(model))
                model_class.saveCurrentSolution(save_filename,
                                        suffixes=test_case.import_suffixes)
            except:
                pass
            else:
                # Okay so we may get to this point if we are using a 
                # plugin like ASL which must advertise having all capabilities
                # since it supports many solvers. And its possible that
                # sending something like a discrete model to ipopt can slip
                # through the cracks without error or warning. Hopefully the test 
                # case was set up so that the solution check will turn up bad.
                if model_class.validateCurrentSolution() is True:
                    warnings.warn("Plugin "+test_case.name+' ('+test_case.io+") is not capable of handling model class "+test_model_name+" "\
                                  "but no exception was thrown and solution matched baseline.")
"""

if __name__ == "__main__":
    unittest.main()
