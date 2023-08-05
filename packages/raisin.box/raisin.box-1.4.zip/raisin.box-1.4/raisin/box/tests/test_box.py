import sys
import unittest
from raisin.box import boxes
from raisin.box.config import PICKLED


class BoxTest(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test_thousands_formatter(self):
        description = [['Header 1', 'string'],
                       ['Header 2', 'number']]
        table_description = {'table_description': description}
        box = {PICKLED: table_description, 'javascript': ''}
        boxes._thousands_formatter(None, box)
        javascript = 'thousandsformatter.format(data, 1);\n'
        self.failUnless(box['javascript'] == javascript)


# make the test suite.
def suite():
    loader = unittest.TestLoader()
    testsuite = loader.loadTestsFromTestCase(BoxTest)
    return testsuite


# Make the test suite; run the tests.
def test_main():
    testsuite = suite()
    runner = unittest.TextTestRunner(sys.stdout, verbosity=2)
    runner.run(testsuite)

if __name__ == "__main__":
    test_main()
