# -*- coding: utf-8 -*-
"""

:organization: Logilab
:copyright: 2001-2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""
from os.path import dirname, join

from logilab.common.testlib import unittest_main

from cubicweb.devtools.testlib import CubicWebTC


class AcceptanceTC(CubicWebTC):

    def test_demo_conference_scenario(self):
        self.assertDocTestFile(join(dirname(__file__), 'demo_conference.txt'))

    def test_review_process(self):
        self.skipTest('error in review-process.txt')
        self.assertDocTestFile(join(dirname(__file__), 'review-process.txt'))


if __name__ == '__main__':
    unittest_main()

