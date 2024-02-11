import glob
import unittest

'''fetches all tests from files in this folder starting with "test_"'''
def create_test_suite():
    test_file_strings = glob.glob('tests/test_python*.py')
    module_strings = ['tests.'+str[6:len(str)-3] for str in test_file_strings]
    print('debug module_strings', module_strings)
    suites = [unittest.defaultTestLoader.loadTestsFromName(name) \
              for name in module_strings]
    print('debug suites', suites)
    test_suite = unittest.TestSuite(suites)
    return test_suite
