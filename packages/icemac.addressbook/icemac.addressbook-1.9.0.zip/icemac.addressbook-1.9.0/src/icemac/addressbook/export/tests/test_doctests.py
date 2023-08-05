# -*- coding: latin-1 -*-
# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id: test_doctests.py 1453 2012-01-05 10:36:15Z icemac $
import icemac.addressbook.testing


def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        'export.txt',
        'sortorder.txt',
        'userfields.txt',
        package='icemac.addressbook.export',
        )
