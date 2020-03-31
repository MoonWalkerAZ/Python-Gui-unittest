'''
This is a thing which, when run, produces a stream
of well-formed test result outputs. Its processing is
initiated by the top-level Executor class.

Its main API is the command line, but it's just as sensible to
call into it. See __main__ for usage
'''
import argparse
import os
import unittest
import sys
import threading

try:
    from coverage import coverage
except ImportError:
    coverage = None

import pipes

vsiTesti = []

def unroll_test_suite(suite):
    """Convert a (possibly heirarchical) test suite into a flat set of tests.

    This is used to ensure that the suite only executes any
    individual test once.
    """
    flat = set()
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            flat.update(unroll_test_suite(test))
        else:
            flat.add(test)
    return flat


class UnittestExecutor:
    '''
    This is a thing which, when run, produces a stream
    of well-formed test result outputs. Its processing is
    initiated by the top-level Executor class
    '''

    def __init__(self):

        # Allows the executor to run a specified list of tests
        self.specified_list = None

    def run_only(self, specified_list):
        self.specified_list = specified_list

    def stream_suite(self, suite):
        my_objects = pipes.PipedTestRunner().run(suite)

        for i in range(0, len(my_objects)-1,2):
            zdruzitev = {**my_objects[i], **my_objects[i+1]}
            vsiTesti.append(zdruzitev)

    def stream_results(self, imeDatoteke):
        """Build a suite matching the requested test list, and stream it."""

        loader = unittest.TestLoader()
        if not self.specified_list:
            suite = loader.discover(imeDatoteke) # tukaj podamo pot
        else:
            sys.path.insert(0, imeDatoteke)
            all_tests = set()

            for module in self.specified_list:
                file_path = module.replace(imeDatoteke, os.sep) # tukaj podamo pot
                if os.path.isdir(file_path):
                    subsuite = loader.discover(file_path, top_level_dir=imeDatoteke)
                else:
                    subsuite = loader.loadTestsFromName(module)

                all_tests.update(unroll_test_suite(subsuite))

            suite = unittest.TestSuite(list(all_tests))

        self.stream_suite(suite)

#if __name__ == '__main__':
def izvedi(imeDatoteke, listOfTests=[]):
    print("Zacetek!!!")
    vsiTesti.clear()
    executor = UnittestExecutor()
    executor.run_only(listOfTests)
    executor.stream_results(imeDatoteke)
    return vsiTesti
