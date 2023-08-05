# -*- coding: utf-8 -*-
# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id: tests.py 1453 2012-01-05 10:36:15Z icemac $

import gocept.reference.verify
import icemac.addressbook.principals.interfaces
import icemac.addressbook.principals.principals
import icemac.addressbook.testing
import unittest
import zope.interface.verify


class TestInterfaces(unittest.TestCase):
    layer = icemac.addressbook.testing.ADDRESS_BOOK_UNITTESTS

    def test_principal(self):
        principal = icemac.addressbook.principals.principals.Principal()
        # need to call created event handler here, because person
        # attribute is a descriptor wrapping the one verifyObject
        # expects.
        icemac.addressbook.principals.principals.created(principal, None)
        gocept.reference.verify.verifyObject(
            icemac.addressbook.principals.interfaces.IPrincipal, principal)
        zope.interface.verify.verifyObject(
            icemac.addressbook.principals.interfaces.IPasswordFields,
            principal)
        zope.interface.verify.verifyObject(
            icemac.addressbook.principals.interfaces.IRoles, principal)
