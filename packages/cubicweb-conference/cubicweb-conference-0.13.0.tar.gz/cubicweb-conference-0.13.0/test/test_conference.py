"""template automatic tests"""

from logilab.common.testlib import TestCase, unittest_main

## uncomment the import if you want to activate automatic test for your
## template

from cubicweb.devtools.testlib import AutomaticWebTest
# necessary trick to avoid cw assertion error
class AutomaticWebTest(AutomaticWebTest): pass

if __name__ == '__main__':
    unittest_main()
