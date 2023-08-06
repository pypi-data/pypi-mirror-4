__docformat__ = 'restructuredtext en'
import unittest
from minitage.core.tests.fetchers import (
    test_interfaces,
    test_scm,
    test_static,)

def test_suite():
    suite = unittest.TestSuite()
    for m in (test_interfaces,
              test_scm,
              test_static,
             ):
        suite.addTest(m.test_suite())
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite())
# vim:set et sts=4 ts=4 tw=80:
