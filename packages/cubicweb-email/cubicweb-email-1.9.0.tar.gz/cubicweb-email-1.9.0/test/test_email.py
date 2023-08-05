"""automatic tests for email views"""

from cubicweb.devtools.testlib import AutomaticWebTest


class AutomaticWebTest(AutomaticWebTest):

    def to_test_etypes(self):
        return set(('Email', 'EmailPart', 'EmailThread'))

    def list_startup_views(self):
        return ()


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
