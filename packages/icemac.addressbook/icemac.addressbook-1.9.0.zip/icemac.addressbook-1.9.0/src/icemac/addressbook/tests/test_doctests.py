# -*- coding: latin-1 -*-
# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id: test_doctests.py 1453 2012-01-05 10:36:15Z icemac $

import icemac.addressbook.testing
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(icemac.addressbook.testing.FunctionalDocFileSuite(
        # Caution: none of these tests can run as unittest!
        'adapter.txt',
        'address.txt',
        'addressbook.txt',
        'person.txt',
        ))
    suite.addTest(icemac.addressbook.testing.TestBrowserDocFileSuite(
        'testing.txt',
        ))
    return suite
