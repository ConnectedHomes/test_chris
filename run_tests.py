import unittest
import sys
#from pylint import epylint as lint

import tests.all_tests

#lint.py_run()

'''runs the test suite defined in tests.all_tests'''
testSuite = tests.all_tests.create_test_suite()
result = text_runner = unittest.TextTestRunner(verbosity=2).run(testSuite)
if result.wasSuccessful():
    sys.exit(0)
else:
    sys.exit(1)
