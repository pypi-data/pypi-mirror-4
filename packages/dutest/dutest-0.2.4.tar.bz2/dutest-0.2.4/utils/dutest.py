#!/usr/bin/env python
# -*- coding: UTF-8 -*-

r"""An object-oriented API to test doctests using unittest runners.

Module providing classes which extend doctest module so
as to achieve better integration with unittest.

It is different from the Pyhton 2.4 doctest unittest API because:

  * A new unitest.TestLoader descendant now allows to load instances
    of TestCases for doctests using unittest-style, supports building
    complex test suites in a more natural way, and eases the use of
    specialized instances of TestCase built out of doctest examples.
  
  * Other loaders allow users to extract TestCase instances out of 
    TestCase descendants and doctests (and any other format) in a 
    single step.
    
  * In this case unittest.TestResult instances report whether
    individual examples have been successfully executed, or otherwise
    have failed or raised an unexpected exception. Formerly TestResult
    objects contained the whole report outputted by doctest module.
    
  * Test analysis require no further parsing to retrieve detailed
    information about failures.
  
  * A whole new unittest API for doctest adds object orientation and
    eliminates functions with big signatures.
  
  * It is not necessary to use DocTestRunner output streams in order
    to collect test results.
  
  * A new hierarchy of doctest TestCases is now 
    possible so for example, setUp and tearDown may
    be redefined across a hierarchy of TestCases 
    instead of providing this methods as parameters to
    a function (breaking OOP philosophy and logic); or
    maybe even failures and errors can be represented in a
    custom way.
  
  * Allows to perform regression testing over tests written
    using doctest.
    
  * Fixes a minor bug related with specifying different verbosity
    levels from the command line to unittest.TestProgram (alias main).
    
  * Loads by default test cases for doctests plus those
    formerly loaded by unittest.TestLoader

It is similar to the Pyhton 2.4 doctest unittest API because:

  * Provides integration with TestProgram and unittest test runners.
    
  * Allows to parameterize doctest behavior via doctest options


A fuller explanation can be found in the following article:

    "Doctest and unittest... now they'll live happily together", O. Lang
    (2008) The Python Papers, Volume 3, Issue 1, pp. 31:51


Note: The contents of this module were first implemented by the module
oop.utils.testing contained in `PyOOP package`_.

.. _PyOOP package: http://pypi.python.org/pypi/PyOOP

"""

# Copyright (C) 2008-2012 Olemis Lang
# 
# This module is free software, and you may redistribute it and/or modify
# it under the same terms as Python itself, so long as this copyright message
# and disclaimer are retained in their original form.
# 
# IN NO EVENT SHALL THE AUTHOR BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
# SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF
# THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
# 
# THE AUTHOR SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
# AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
# SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.

__all__ = 'DocTestCase', 'DocTestSuite', 'DocTestLoader', 'main', \
          'defaultTestLoader', 'defaultTestRunner', \
          'PackageTestLoader', 'MultiTestLoader', 'REGEX', 'UNIX'

__metaclass__ = type

#------------------------------------------------------
#    Pattern matching strategies
#------------------------------------------------------

from re import compile as REGEX
from fnmatch import translate

UNIX = lambda pattern: REGEX(translate(pattern))

#------------------------------------------------------
#    unittest interface to doctest module
#------------------------------------------------------

from sys import stderr, modules

import doctest
from unittest import TestCase
import unittest

from inspect import ismodule
from StringIO import StringIO
import os

try:
    import pkg_resources
except ImportError:
    __has_resources = False
except:
    raise
else:
    __has_resources = True

# Hide this module from tracebacks written into test results.
__unittest = True

class _Doc2UnitTestRunner(doctest.DocTestRunner):
    r"""An adapter class which allows to invoke transparently a
    doctest runner from inside a unittest run. Besides it reports
    the match made for each Example instance into separate
    TestResult objects.
    
    Note: Users should not use this class directly. It is present
            here as an implementation detail.
    """
    def __init__(self, checker=None, verbose=None, optionflags=0,
                 result= None):
        doctest.DocTestRunner.__init__(self, checker, verbose,
                                       optionflags)
        self.result= result
    def summarize(verbose= None): 
        pass
    def run(self, test, compileflags=None, out=None, 
            clear_globs=True):
        doctest.DocTestRunner.run(self, test, compileflags, out,
                                  clear_globs)
    
    def __cleanupTC(self, tc, result): pass
                
    def report_start(self, out, test, example):
        result= self.result
        if not result or result.shouldStop:
            return
        tc= example.tc
        tc.ok= True
        test.globs['__tester__']= tc
        result.startTest(tc)
        try:
            tc.setUp()
        except KeyboardInterrupt:
            raise
        except:
            result.addError(tc, tc._exc_info())
            tc.ok= False
    def report_success(self, out, test, example, got):
        tc= example.tc
        if not tc.ok:        # example is Ok but setUp failed
            return
        result= self.result
        if (not result) or result.shouldStop:
            return
        try:
            tc.tearDown()
        except KeyboardInterrupt:
            raise
        except:
            result.addError(tc, tc._exc_info())
        else:
            result.addSuccess(tc)
    def report_failure(self, out, test, example, got):
        tc= example.tc
        if not tc.ok:        # example is Ok but setUp failed
            return
        result= self.result
        if not result or result.shouldStop:
            return
        msg = 'Example expected\n%s \n...but test outputted...\n%s'% \
                                                (example.want, got)
        try:
            tc.ok= False
            buff = StringIO()
            doctest.DocTestRunner.report_failure(self, buff.write, 
                                                 test, example, got)
            
            msg = buff.getvalue().split('\n', 2)[2]
            buff.close()
            buff = None
        finally:
            try:
                tc.tearDown()
            except KeyboardInterrupt:
                raise
            except:
                # Errors take precedence over failures
                result.addError(tc, tc._exc_info())
            else:
                result.addFailure(tc, (tc.failureException, 
                        msg,
                        None))
    def report_unexpected_exception(self, out, test, example, 
                                    exc_info):
        tc= example.tc
        if not tc.ok:        # example is Ok but setUp failed
            return
        result= self.result
        if not result or result.shouldStop:
            return
        try:
            tc.ok= False
            tc.tearDown()
        except KeyboardInterrupt:
            raise
        except:
            if issubclass(exc_info[0], tc.failureException):
                # Report faulty tearDown only if failure was detected
                result.addError(tc, tc._exc_info())
            else:
                result.addError(tc, exc_info)
        else:
            if issubclass(exc_info[0], tc.failureException):
                result.addFailure(tc, exc_info)
            else:
                result.addError(tc, exc_info)

class DocTestCase(unittest.TestCase):
    r"""A class whose instances represent tests over DocTest 
    instance's examples.
    """
    def __init__(self, dt, idx= 0):
        r"""Create an instance that will test a DocTest instance's
        example (the idx-th according to its examples member)
        """
        self.ok= True
        self._dt= dt
        ex= dt.examples[idx]
        self._ex= ex
        ex.tc= self
        self._testMethodDoc= '%s (line %s)'% (dt.name, 
                self.lineno is not None and self.lineno or '?')
    
    @property
    def lineno(self):
        if self._dt.filename:
            if self._dt.lineno is not None and \
                                         self._ex.lineno is not None:
                return self._dt.lineno + self._ex.lineno + 1
            elif self._ex.lineno is not None:
                return self._ex.lineno+ 1
            else:
                return None
        else:
            return self._ex.lineno+ 1
    
    @property
    def _testMethodName(self):
        return "%s line %s"% (self._dt.name, self.lineno)
    
    def defaultTestResult(self):
        return TestResult()
    
    def id(self):
        return "Test "+ self._methodName
    
    def __repr__(self):
        return "<%s test=%s line=%s>"% \
                                (unittest._strclass(self.__class__), 
                                self._dt.name, self.lineno)
    
    def run(self, result=None):
        raise NotImplementedError, "doctest module doesn't allow to "\
                                   "test single examples"
    
    def debug(self):
        r"""Run the test without collecting errors in a TestResult"""
        raise NotImplementedError, "doctest module doesn't allow to "\
                                   "test single examples"
    
    @property
    def globalns(self):
      r"""The global namespace used to execute the interactive 
      examples enclosed by this suite.
      """
      return self._dt.globs

class DocTestSuite(unittest.TestSuite):
    r"""This test suite consists of DocTestCases derived from a single
    DocTest instance.
    """
    docRunnerClass= _Doc2UnitTestRunner
    docTestCaseClass= DocTestCase
    def __init__(self, dt, optionflags=0, checker=None, runopts=None):
        if runopts is None:
            runopts = dict()
        unittest.TestSuite.__init__(self)
        self._dt= dt
        self.dt_opts, self.dt_checker, self.dt_ropts = \
                        optionflags, checker, runopts
        for idx in xrange(len(dt.examples)):
            unittest.TestSuite.addTest(self, \
                                       self.docTestCaseClass(dt, idx))
    
    def addTest(self, test):
        raise RuntimeError, "No test can be added to this Test Suite."
    
    def run(self, result):
        self.docRunnerClass(optionflags= self.dt_opts, 
                checker=self.dt_checker, verbose=False, \
                result= result).run(self._dt, **self.dt_ropts)
        return result
    
    def debug(self):
        r"""Run the tests without collecting errors in a TestResult"""
        self.run(None)
        return result
    
    @property
    def globalns(self):
      r"""The global namespace used to execute the interactive 
      examples enclosed by this suite.
      """
      return self._dt.globs

class DocTestLoader(unittest.TestLoader):
    r"""This class loads DocTestCases and returns them wrapped in a
    TestSuite
    """
    doctestSuiteClass= DocTestSuite
    def __init__(self, dt_finder= None, globs=None, extraglobs=None, 
                 **opts):
        super(DocTestLoader, self).__init__()
        self._dtf= dt_finder or doctest.DocTestFinder()
        self.globs, self.extraglobs, self.opts= globs, extraglobs, opts
    
    def loadTestsFromTestCase(self, testCaseClass):
        r"""Return a suite of all DocTestsCases contained in 
        testCaseClass
        """
        raise NotImplementedError
    
    def loadTestsFromModule(self, module):
        r"""Return a suite of all DocTestCases contained in the given 
        module
        """
        return self.loadTestsFromObject(module)
    
    def loadModuleFromName(self, name):
        parts_copy = name.split('.')
        while parts_copy:
            try:
                module = __import__('.'.join(parts_copy))
                return module
            except ImportError:
                del parts_copy[-1]
                if not parts_copy: raise
    
    def findObjectByName(self, name, module=None):
        parts = name.split('.')
        if module is None:
            module= self.loadModuleFromName(name)
        parts = parts[1:]
        obj = module
        for part in parts:
            parent, obj = obj, getattr(obj, part)
        return obj
        
    def loadTestsFromObject(self, obj, module=None):
        global modules
        doctests = self._dtf.find(obj, module=module, 
                                  globs=self.globs, 
                                  extraglobs=self.extraglobs)
        if module is None:
            if ismodule(obj):
                module= obj
            else:
                try:
                    module= modules[obj.__module__]
                except:
                    module= None
        if self.globs is None:
            globs = module and module.__dict__ or dict()
        
        # This is legacy code inspired in doctest behavior.
        # However this is not done anymore since it difficults loading
        # tests from multiple test scripts by using PackageTestLoader
        # class.
            # if not doctests:
            # # Why do we want to do this? Because it reveals a bug that
            # # might otherwise be hidden.
            #     raise ValueError(obj, "has no tests")
        doctests.sort()
        try:
            filename = module and module.__file__ or '?'
        except:
            filename = '?'
        if filename[-4:] in (".pyc", ".pyo"):
            filename = filename[:-1]
        ts= self.suiteClass()
        for dt in doctests:
            if len(dt.examples) != 0:
                if not dt.filename:
                    dt.filename = filename
                ts.addTest(self.doctestSuiteClass(dt, **self.opts))
        return ts
    
    def loadTestsFromName(self, name, module=None):
        r"""Return a suite of all tests cases given a string specifier.
        
        The name may resolve to any kind of object.
        
        The method optionally resolves the names relative to a given 
        module.
        """
        return self.loadTestsFromObject(
                                 self.findObjectByName(name, module),
                                 module)

#------------------------------------------------------
#	Default settings
#------------------------------------------------------
defaultTestRunner = unittest.TextTestRunner()

#------------------------------------------------------
#    Custom Test Suites
#------------------------------------------------------

class DocTestSuiteFixture(DocTestSuite):
  r"""Test suite that allows to set up a fixture once before all 
  its interactive examples are run and clean up after they have been 
  run (i.e. Suite Fixture Setup test pattern).
  """
  def run(self, result):
    r"""Setup the fixture, run the interactive examples (i.e. test 
    cases), and finally clean up.
    """
    try:
      proc = self.setUp
    except AttributeError :
      pass                      # No need to prepare the test suite
    else :
      try:
        proc()
      except KeyboardInterrupt:
        raise
      except:
        # Signal error for all the test cases in this suite
        for dtc in self :
          result.addError(dtc, dtc._exc_info())
        return
    
    result = DocTestSuite.run(self, result)
    
    try:
      proc = self.tearDown
    except AttributeError :
      pass                  # No need to clean up
    else :
      try :
        proc()
      except KeyboardInterrupt:
        raise
      except:
        pass                # Silence ? I have no idea about what to do.
    return result

#------------------------------------------------------
#    Test Discovery
#------------------------------------------------------

class MultiTestLoader(unittest.TestLoader):
    r"""A loader which retrieves at once unittest-like test cases from
    different sources and/or formats.
    """
    
    def __init__(self, loaders= None):
        self.loaders= loaders or []
    def loadTestsFromTestCase(self, testCaseClass):
        r"""Return a suite of all tests cases contained in 
        testCaseClass
        """
        return self.suiteClass(
                loader.loadTestsFromTestCase(testCaseClass) \
                                        for loader in self.loaders)
    def loadTestsFromModule(self, module):
        r"""Return a suite of all tests cases contained in the given
        module
        """
        return self.suiteClass(loader.loadTestsFromModule(module) \
                for loader in self.loaders)
    def loadTestsFromName(self, name, module=None):
        r"""Return a suite of all tests cases given a string 
        specifier.
        """
        return self.suiteClass(loader.loadTestsFromName(name, module) \
                                        for loader in self.loaders)
    def loadTestsFromNames(self, names, module=None):
        r"""Return a suite of all tests cases found using the given 
        sequence of string specifiers. See 'loadTestsFromName()'.
        """
        return self.suiteClass(loader.loadTestsFromNames(names, module) \
                for loader in self.loaders)

defaultTestLoader = MultiTestLoader([unittest.defaultTestLoader, 
                                DocTestLoader()])

class PackageTestLoader(unittest.TestLoader):
    r"""A unittest-like loader (Decorator/Wrapper class) that recursively
    retrieves all the tests included in all the modules found within a
    specified package and the hierarchy it determines. Some filters
    (i.e. regex) may be specified to limit the modules contributing to
    the resulting test suite.
    
    The default behavior if no parameters are specified is to load 
    all doctests and instantiate all subclasses of unittest.TestCase 
    found in all the module across the whole package structure.
    """
    
    defaultPattern = REGEX(".*")
    
    def __init__(self, pattern=defaultPattern, loader=defaultTestLoader,
                 impall=False, globs=None, ns=None, style=REGEX):
        r"""Initialize this test loader. Parameters have the following
        meaning :
        
        param pattern: A regular expression object (see re module)
            used to filter the modules which will be inspected so as
            to retrieve the test suite. If not specified then all
            modules will be processed looking for tests.
            
        param loader: Specify the loader used to retrieve test cases
            from each (single) module matching the aforementioned
            criteria.
        
        param impall: If the value of this flag evaluates to true then
            all the modules inside the package hierarchy will be
            imported (disregarding whether they will contribute to the
            test suite or not). Otherwise only those packages for
            which a match is made (i.e. those contributing to the test
            suite) are imported directly.
        
        param globs: The global namespace in which module imports will
            be carried out.
        
        param ns: The local namespace in which module imports will
            be carried out.
        param style: It is used only when a string has been specified 
            in pattern parameter. Its value *MUST* be a callable 
            object accepting a single string argument and returning a 
            Regular Expression Object to match the target module 
            names. Its possible values are : 
            
            * dutest.REGEX (default) : pattern is a standard regular 
                expression. In fact dutest.REGEX = re.compile.
            * dutest.UNIX : pattern is a Unix filename pattern. In 
                fact dutest.UNIX ~= fnmatch.translate.
        """
        if globs is None:
            globs = {}
        if ns is None:
            ns = {}
        super(PackageTestLoader, self).__init__()
        if isinstance(pattern, str):
            pattern = style(pattern)
        self.pattern = pattern
        self.loader = loader
        self.impall = impall
        self.locals = ns
        self.globs = globs
    
    def loadTestsFromTestCase(self, testCaseClass):
        r"""Return a suite of all tests cases contained in 
        testCaseClass as determined by the wrapped test loader.
        """
        return self.loader.loadTestsFromTestCase(testCaseClass)
        
    def loadTestsFromModule(self, module):
        r"""Return a suite of all test cases contained in the given
        package and the modules it contains recursively.
        
        If a ``pattern`` was not specified to the initializer then all
        modules (packages) in the aformentioned hierarchy are
        considered. Otherwise a test suite is retrieved for all those
        modules having a name matching this pattern. They are packed
        together into another test suite (its type being standard
        self.suiteClass) which is returned to the caller.
        
        If the attribute ``impall`` is set, then all modules in the
        former hierarchy are imported disregarding whether they will
        be inspected when looking for tests or not.
        """
        fnm = os.path.basename(module.__file__)
        ispyfile = any(fnm.endswith(suffix) for suffix in ['.py', '.pyc'])
        if  ispyfile and fnm.rsplit('.', 1)[0] != '__init__':
            return self.loader.loadTestsFromModule(module)
        else:
            loader = self.loader
            if ispyfile:
                root_dir = os.path.dirname(fnm)
            else:
                root_dir = fnm
            pkg_name = module.__name__
            idx = len(pkg_name)
            pend_names = [module.__name__]
            suite = self.suiteClass()
            if self.pattern.match(module.__name__) is not None:
                suite.addTest(loader.loadTestsFromModule(module))
            for modnm in pend_names:
                curdir = root_dir + modnm[idx:].replace('.', os.sep)
                for fname in os.listdir(curdir):
                    ch_path = os.path.join(curdir, fname)
                    if os.path.isdir(ch_path) \
                            and os.path.exists(os.path.join(ch_path, 
                                               '__init__.py')):
                        child_name = '.'.join([modnm, fname])
                        pend_names.append(child_name)
                    elif fname.endswith('.py') and \
                            fname != '__init__.py':
                        child_name = '.'.join([modnm, fname[:-3]])
                    else:
                        continue
                    if self.pattern.match(child_name) is not None:
                        __import__(child_name, self.globs,
                                   self.locals, [], -1)
                        suite.addTest(loader.loadTestsFromModule(
                                modules[child_name]))
                    elif self.impall:
                        __import__(child_name, self.globs,
                                   self.locals, [], -1)
            return suite

#------------------------------------------------------
#    Assertions
#------------------------------------------------------

class TextAssertionError(AssertionError):
    r"""Raised when unexpected text is found."""

class TextAssert(doctest.OutputChecker):
    r"""Customized doctest OutputChecker useful to perform PyUnit
    assertions on expected text.
    """
    failureException = TextAssertionError
    
    class FakeExample():
        def __init__(self, want):
            self.want = want
    
    def assertTextEqual(self, want, got, options):
        r"""Used to check whether the actual text matches the 
        expected value. 
        """
        if not self.check_output(want, got, options):
            fake_ex = self.FakeExample(want)
            msg = self.output_difference(fake_ex, got, options)
            raise self.failureException(msg)

#------------------------------------------------------
#    Patch to "fix" verbosity "bug" in unittest.TestProgram
#------------------------------------------------------
class VerboseTestProgram(unittest.TestProgram):
    r"""A command-line program that runs a set of tests. 
    This is primarily for making test modules conveniently executable.
    
    This class extends unittest.TestProgram for the following 
    purposes:
    
      * Fix a minor bug in unittest.TestProgram which prevents running
        from the command line a test suite using different verbosity
        levels.
        
      * By default, load test cases from unittest.TestCase descendants
        (i.e. by using unittest.TestLoader) as well as from
        interactive examples included in doctests.
    """
    def __init__(self, module='__main__', defaultTest=None,
                 argv=None, testRunner=None, 
                 testLoader=defaultTestLoader):
        return super(VerboseTestProgram, self).__init__(self, module, 
                defaultTest, argv, testRunner, testLoader)
    
	def runTests(self):
		if self.testRunner is not None:
			self.testRunner.verbosity = self.verbosity
		super(VerboseTestProgram, self).runTests()

main = VerboseTestProgram

#------------------------------------------------------
#    Tests !!!!
#------------------------------------------------------
def test_suite():
    import sys
    from types import ModuleType
    from unittest import _WritelnDecorator as WLnD
    
    TEST_MODULE_PREFIX = 'dutest._genmdl.'
    
    def create_module(modsuite, modname='', moddoc='', indent=4):
        r"""Return an instance of Module provided its code.
        
        @param modsuite a suite of Python statements executed to 
                        populate the module with items. The prefix 
                        'dutest._genmdl.' is always added.
        @param modname  module name.
        @param moddoc   documentation written for this module. 
                        Module-level docstrings in `modsuite` may be 
                        ignored.
        """
        modname = TEST_MODULE_PREFIX + modname
        modsuite = '\n'.join(l[indent:] for l in modsuite.splitlines())
        m = ModuleType(modname, moddoc)
        ns = m.__dict__
        ns['dutest'] = sys.modules[__name__]
        exec modsuite in ns
        sys.modules[modname] = m
        return m
    
    def show_result_details(result):
        r"""Display runner-agnostic test report.
        """
        println = False
        for outcome in ['failures', 'errors']:
            test_results = getattr(result, outcome, [])
            if test_results:
                if println:
                    print
                else:
                    println = True
                print "*" * 10
                print "*", outcome.capitalize()
                print "*" * 10,
                for test, msg  in test_results:
                    print
                    print '-' * 70
                    print test.shortDescription() or str(test)
                    print '-' * 70
                    print msg.strip(),
            
    class NullOutput:
        close = flush = lambda self: None
        tell = lambda self: 0
        read = readline = truncate = lambda self, size=None: ''
        readlines = lambda self, sizehint=None: []
        seek = lambda self, pos, whence=None: None
        write = lambda self, str: None
        writelines = lambda self, seq: None
        def next(self):
            raise StopIteration()
    
    helpers = {
            'runner': unittest.TextTestRunner(stream=WLnD(NullOutput())),
            'create_module': create_module,
            'show_result_details': show_result_details,
        }
    class DuTestLoader(DocTestLoader):
        class doctestSuiteClass(DocTestSuite):
            class docRunnerClass(_Doc2UnitTestRunner):
                @property 
                def tr_out(self):
                    # Redirect result output to capture in doctest
                    #return self._fakeout
                    # Ignore result output
                    return NullOutput()
                def run(self, test, compileflags=None, out=None, 
                                                        clear_globs=True):
                    runner = test.globs['runner']
                    def _makeResult():
                        result = runner.__class__._makeResult(runner)
                        result.stream = WLnD(self.tr_out)
                        return result
                    
                    runner._makeResult = _makeResult
                    from warnings import simplefilter, resetwarnings
                    simplefilter('ignore', RuntimeWarning)
                    try:
                        return _Doc2UnitTestRunner.run(self, test, 
                                                            compileflags,
                                                            out, clear_globs)
                    finally:
                        resetwarnings()
        
    loader = DuTestLoader(extraglobs=helpers, 
                            optionflags=doctest.REPORT_UDIFF)
    return loader.loadTestsFromModule(sys.modules[__name__])


__test__ = {
    '(Meta) Test setup': r"""
        >>> m = create_module('''
        ...     def choice(seq):
        ...         \"\"\"
        ...         >>> seq = range(10)
        ...         >>> elem = choice(seq)
        ...         >>> elem in seq
        ...         True
        ...         \"\"\"
        ...         return seq[0]
        ...     ''', 'dutest_basic')
        ...
        
        >>> m.choice.func_globals is m.__dict__
        True
        >>> m.choice.__doc__ <> ''
        True
        >>> m.choice.__module__
        'dutest._genmdl.dutest_basic'
        >>> m.__name__
        'dutest._genmdl.dutest_basic'
        >>> import inspect
        >>> inspect.getmodule(m.choice) is not None
        True
        """,
    'Basic usage': r"""
        >>> m = create_module('''
        ...     def shuffle(seq):
        ...         \"\"\" 
        ...         >>> seq = range(10)
        ...         >>> shuffle(seq)
        ...         >>> seq.sort()
        ...         >>> seq   #doctest: +NORMALIZE_WHITESPACE
        ...         [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        ...         \"\"\"
        ...         seq.pop()
        ...     
        ...     def sample(seq, count):
        ...         \"\"\" 
        ...         >>> seq = range(10)
        ...         >>> sample(seq, 20) # doctest: +ELLIPSIS
        ...         Traceback (most recent call last):
        ...         ...
        ...         ValueError: sample larger than population
        ...         >>> [x in seq for x in sample(seq, 5)]
        ...         ...       #doctest: +NORMALIZE_WHITESPACE
        ...         [True, True, True, True, True]
        ...         \"\"\"
        ...         if count > len(seq):
        ...             raise ValueError("sample larger than population")
        ...         return seq[:count - 1] + [None]
        ...     def choice(seq):
        ...         \"\"\"
        ...         >>> seq = range(10)
        ...         >>> elem = choice(seq)
        ...         >>> elem in seq
        ...         True
        ...         \"\"\"
        ...         return seq[0]
        ...     ''', 'dutest_basic')
        ...
        
        >>> suite = DocTestLoader().loadTestsFromModule(m)
        >>> len(suite._tests)
        3
        >>> result = runner.run(suite)
        >>> result.testsRun
        10
        >>> len(result.errors)
        0
        >>> len(result.failures)
        2
        >>> show_result_details(result)
        **********
        * Failures
        **********
        ----------------------------------------------------------------------
        dutest._genmdl.dutest_basic.sample (line 19)
        ----------------------------------------------------------------------
        AssertionError: Failed example:
            [x in seq for x in sample(seq, 5)]
                  #doctest: +NORMALIZE_WHITESPACE
        Expected:
            [True, True, True, True, True]
        Got:
            [True, True, True, True, False]
        ----------------------------------------------------------------------
        dutest._genmdl.dutest_basic.shuffle (line 7)
        ----------------------------------------------------------------------
        AssertionError: Failed example:
            seq   #doctest: +NORMALIZE_WHITESPACE
        Expected:
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        Got:
            [0, 1, 2, 3, 4, 5, 6, 7, 8]
        """,
    'Using optional doctest features': r"""
        >>> m = create_module('''
        ...     import doctest, dutest
        ...     
        ...     def ok():
        ...         r\"\"\"
        ...                >>> ok()
        ...                'OK'
        ...         \"\"\"
        ...         return 'OK'
        ...     
        ...     def fail(count):
        ...         r\"\"\"
        ...                >>> fail(extra2)
        ...                'FAIL 2'
        ...         \"\"\"
        ...         return 'FAIL ' + str(count)
        ...     
        ...     class DocTestFinderSubClass(doctest.DocTestFinder):
        ...         def find(self, obj, name=None, module=None, 
        ...                           globs=None, extraglobs=None):
        ...             bad_ex = doctest.Example(
        ...                      source=r"print 'Yo me\\nbaño\\nen el río',",
        ...                      want="Yo me\\nrío en \\n  el baño\\n",
        ...                      lineno=666, indent=0)
        ...             tests = doctest.DocTestFinder.find(self, obj,
        ...                          name, module, globs, extraglobs)
        ...             
        ...             from copy import copy
        ...             from itertools import izip, imap, repeat
        ...             for dt, ex in izip(tests, imap(copy, repeat(bad_ex))):
        ...                 dt.examples.append(ex)
        ...             return tests
        ...     
        ...     class MyOwnCheckerClass(doctest.OutputChecker):
        ...         def output_difference(self, example, got, optionflags):
        ...             super = doctest.OutputChecker.output_difference
        ...             return super(self, example, got, optionflags) + \\
        ...                     'Copyright Olemis Lang (I own you baby)\\n'
        ...     
        ...     loader =  dutest.DocTestLoader(
        ...        DocTestFinderSubClass(),
        ...        extraglobs={'extra1' : 1, 'extra2' : 2},
        ...        optionflags = doctest.REPORT_UDIFF,
        ...        checker = MyOwnCheckerClass(),
        ...        runopts = dict(
        ...              clear_globs = True)
        ...        )
        ...     
        ...     def test_suite():
        ...         import sys
        ...         return loader.loadTestsFromModule(sys.modules[__name__])
        ...     
        ...     ''', 'dutest_options')
        ... 
        
        >>> suite = m.test_suite()
        >>> len(suite._tests)
        2
        >>> result = runner.run(suite)
        >>> result.testsRun
        4
        >>> len(result.errors)
        0
        >>> len(result.failures)
        2
        >>> show_result_details(result)
        **********
        * Failures
        **********
        ----------------------------------------------------------------------
        dutest._genmdl.dutest_options.fail (line 678)
        ----------------------------------------------------------------------
        AssertionError: Failed example:
            print 'Yo me\nbaño\nen el río',
        Differences (unified diff with -expected +actual):
            @@ -1,3 +1,3 @@
             Yo me
            -río en
            -  el baño
            +baño
            +en el río
        Copyright Olemis Lang (I own you baby)
        ----------------------------------------------------------------------
        dutest._genmdl.dutest_options.ok (line 671)
        ----------------------------------------------------------------------
        AssertionError: Failed example:
            print 'Yo me\nbaño\nen el río',
        Differences (unified diff with -expected +actual):
            @@ -1,3 +1,3 @@
             Yo me
            -río en
            -  el baño
            +baño
            +en el río
        Copyright Olemis Lang (I own you baby)
        """,
    'Combining test cases and doctests': r"""
        >>> m = create_module('''
        ...     def shuffle(seq):
        ...         \"\"\" 
        ...         >>> seq = range(10)
        ...         >>> shuffle(seq)
        ...         >>> seq.sort()
        ...         >>> seq   #doctest: +NORMALIZE_WHITESPACE
        ...         [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        ...         \"\"\"
        ...         seq.pop()
        ...     
        ...     def sample(seq, count):
        ...         \"\"\" 
        ...         >>> seq = range(10)
        ...         >>> sample(seq, 20) # doctest: +ELLIPSIS
        ...         Traceback (most recent call last):
        ...         ...
        ...         ValueError: sample larger than population
        ...         >>> [x in seq for x in sample(seq, 5)]
        ...         ...       #doctest: +NORMALIZE_WHITESPACE
        ...         [True, True, True, True, True]
        ...         \"\"\"
        ...         if count > len(seq):
        ...             raise ValueError("sample larger than population")
        ...         return seq[:count - 1] + [None]
        ...     def choice(seq):
        ...         \"\"\"
        ...         >>> seq = range(10)
        ...         >>> elem = choice(seq)
        ...         >>> elem in seq
        ...         True
        ...         \"\"\"
        ...         return seq[0]
	...     
        ...     import unittest
        ...     class TestSequenceFunctions(
        ...             unittest.TestCase):
        ...         
        ...       def setUp(self):
        ...          self.seq = range(10)
        ...     
        ...       def tearDown(self):
        ...          self.seq = None
        ...     
        ...       def testshuffle(self):
        ...          shuffle(self.seq)
        ...          self.seq.sort()
        ...          self.assertEqual(
        ...                  self.seq, range(10))
        ...     
        ...       def testsample(self):
        ...          self.assertRaises(ValueError, sample, self.seq, 20)
        ...          self.assertEqual([True] * 5, 
        ...                      [x in self.seq for x in sample(self.seq, 5)])
        ...     
        ...       def testchoice(self):
        ...          self.assertTrue(choice(self.seq) in self.seq)
        ...     ''', 'dutest_both')
        ...
        
        >>> suite = defaultTestLoader.loadTestsFromModule(m)
        >>> len(suite._tests)
        2
        >>> result = runner.run(suite)
        >>> result.testsRun
        13
        >>> len(result.errors)
        0
        >>> len(result.failures)
        4
        >>> show_result_details(result)
        **********
        * Failures
        **********
        ----------------------------------------------------------------------
        testsample (dutest._genmdl.dutest_both.TestSequenceFunctions)
        ----------------------------------------------------------------------
        Traceback (most recent call last):
          File "<string>", line 54, in testsample
        AssertionError: [True, True, True, True, True] != [True, True, True, True, False]
        ----------------------------------------------------------------------
        testshuffle (dutest._genmdl.dutest_both.TestSequenceFunctions)
        ----------------------------------------------------------------------
        Traceback (most recent call last):
          File "<string>", line 49, in testshuffle
        AssertionError: [0, 1, 2, 3, 4, 5, 6, 7, 8] != [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        ----------------------------------------------------------------------
        dutest._genmdl.dutest_both.sample (line 19)
        ----------------------------------------------------------------------
        AssertionError: Failed example:
            [x in seq for x in sample(seq, 5)]
                  #doctest: +NORMALIZE_WHITESPACE
        Expected:
            [True, True, True, True, True]
        Got:
            [True, True, True, True, False]
        ----------------------------------------------------------------------
        dutest._genmdl.dutest_both.shuffle (line 7)
        ----------------------------------------------------------------------
        AssertionError: Failed example:
            seq   #doctest: +NORMALIZE_WHITESPACE
        Expected:
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        Got:
            [0, 1, 2, 3, 4, 5, 6, 7, 8]
        """,
    'Per-example fixtures for module docstrings' : r"""
        >>> m = create_module('''
        ...     def shuffle(seq):
        ...         seq.pop()
        ...     
        ...     def sample(seq, count):
        ...         if count > len(seq):
        ...             raise ValueError("sample larger than population")
        ...         return seq[:count - 1] + [None]
        ...     
        ...     def choice(seq):
        ...         return seq[0]
        ...     
        ...     class RandomTestLoader(dutest.DocTestLoader):
        ...       class doctestSuiteClass(dutest.DocTestSuite):
        ...         class docTestCaseClass(dutest.DocTestCase):
        ...           def setUp(self):
        ...             self.globalns['seq'] = range(10)
        ...     ''', 
        ...     modname='dutest_example_fixture', 
        ...     moddoc=r'''
        ...     range(10) is assigned to seq before
        ...     executing each statement.
        ...     
        ...     >>> shuffle(seq); seq.sort(); seq
        ...     ...   #doctest: +NORMALIZE_WHITESPACE
        ...     [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        ...     
        ...     >>> sample(seq, 20) # doctest: +ELLIPSIS
        ...     Traceback (most recent call last):
        ...         ...
        ...     ValueError: sample larger than population
        ...     
        ...     >>> [x in seq for x in sample(seq, 5)]
        ...     ...   #doctest: +NORMALIZE_WHITESPACE
        ...     [True, True, True, True, True]
        ...     
        ...     >>> choice(seq) in seq
        ...     True
        ...     ''')
        ...
       
        >>> suite = m.RandomTestLoader().loadTestsFromModule(m)
        >>> len(suite._tests)
        1
        >>> result = runner.run(suite)
        >>> result.testsRun
        4
        >>> len(result.errors)
        0
        >>> len(result.failures)
        2
        >>> show_result_details(result)
        **********
        * Failures
        **********
        ----------------------------------------------------------------------
        dutest._genmdl.dutest_example_fixture (line 6)
        ----------------------------------------------------------------------
        AssertionError: Failed example:
            shuffle(seq); seq.sort(); seq
              #doctest: +NORMALIZE_WHITESPACE
        Expected:
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        Got:
            [0, 1, 2, 3, 4, 5, 6, 7, 8]
        ----------------------------------------------------------------------
        dutest._genmdl.dutest_example_fixture (line 15)
        ----------------------------------------------------------------------
        AssertionError: Failed example:
            [x in seq for x in sample(seq, 5)]
              #doctest: +NORMALIZE_WHITESPACE
        Expected:
            [True, True, True, True, True]
        Got:
            [True, True, True, True, False]
        """,
    }

