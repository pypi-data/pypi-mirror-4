import sys
import re
import textwrap

from pyutilib.component.core import *

from coopr.pyomo.check.hooks import *


class IModelChecker(Interface):
    def check(self, runner, script, info):
        """
        Check a particular piece of Python information for errors.

        Provides the primary interface for checking some code for problems,
        according to the particular subclass's definition. 
        
        @param runner the ModelCheckRunner instance that has dispatched
                      this call to check().
        @param script the ModelScript instance being checked.
        @param info the data to check. Depending on the subclass, info
                    can be the raw text of a Python script, the entire AST
                    of the script, or a particular node in that AST.
        """

    def beginChecking(self, runner, script):
        """
        Start checking the given script from the given runner.
        """

    def endChecking(self, runner, script):
        """
        Finish checking the given script from the given runner.
        """

    def problem(self, script = None, message = "Error", lineno = None):
        """
        Write a problem to the console. The format varies and can be
        changed in subclasses; by default, this method prints the following:

        [CheckerName] script.py:line: Error

        @param script the ModelScript instance being checked. Must be passed
                      to have the file name and line number printed.
        @param message the error to display.
        @param lineno the line number on which the error occurred.
        """

class PyomoModelChecker(SingletonPlugin):
    implements(IModelChecker, inherit=True)

    _prehooks = ExtensionPoint(IPreCheckHook)
    _posthooks = ExtensionPoint(IPostCheckHook)

    def __init__(self):
        self._currentRunner = None
        self._currentScript = None

    def _check(self, runner, script, info):
        self._runner = runner
        self._script = script
        
        for prehook in self._prehooks:
            prehook.precheck(runner, script, info)

        try:
            self.check(runner, script, info)
        except Exception:
            e = sys.exc_info()[1]
            print(self.checkerLabel() + "ERROR during check call!")
            raise e

        for posthook in self._posthooks:
            posthook.postcheck(runner, script, info)

        self._runner = None
        self._script = None

    def check(self, runner, script, info):
        # Should be `pass` - checkers are not guaranteed to call
        # superclass when running their own check() methods
        pass

    def _beginChecking(self, runner, script):
        self._currentRunner = runner
        self._currentScript = script

        try:
            self.beginChecking(runner, script)
        except Exception:
            print(self.checkerLabel() + "ERROR during pre-check call!")

    def beginChecking(self, runner, script):
        pass

    def _endChecking(self, runner, script):
        try:
            self.endChecking(runner, script)
        except Exception:
            print(self.checkerLabel() + "ERROR during pre-check call!")

        self._currentRunner = None
        self._currentScript = None

    def endChecking(self, runner, script):
        pass

    def _checkerName(self):
        match = re.search("<class '([a-zA-Z0-9_\.]+)'>", str(self.__class__))
        return match.group(1).split(".")[-1]

    def _checkerPackage(self):
        match = re.search("<class '([a-zA-Z0-9_\.]+)'>", str(self.__class__))
        return match.group(1).split(".")[-3]
        
    def checkerLabel(self):
        return "[" + self._checkerPackage() + "::" + self._checkerName() + "] "

    def checkerDoc(self):
        return ""

    def problem(self, message = "Error", runner = None, script = None, lineno = None):
        if script is None:
            script = self._currentScript
        if runner is None:
            runner = self._currentRunner

        output = self.checkerLabel()

        if script is not None:
            output += script.filename() + ":"
            if lineno is not None:
                output += str(lineno) + ":"
        else:
            output += "<unknown>:"

        output += " " + message

        print(output)

        try:
            if runner.verbose:
                if len(self.checkerDoc()) > 0:
                    lines = textwrap.dedent(self.checkerDoc()).split("\n")
                    lines = filter((lambda x : len(x) > 0), lines)
                    for line in lines:
                        print(self.checkerLabel() + line)
                print
        except Exception:
            print(self.checkerLabel() + "ERROR during verbose info generation")
            print

class ImmediateDataChecker(PyomoModelChecker):
    pass

class IterativeDataChecker(PyomoModelChecker):
    pass

class ImmediateTreeChecker(PyomoModelChecker):
    pass

class IterativeTreeChecker(PyomoModelChecker):
    pass

from coopr.pyomo.check.checkers import *
