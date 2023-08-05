# Copyright (c) 2010-2012 Michael Howitz
# See also LICENSE.txt
# $Id: evolve15.py 1453 2012-01-05 10:36:15Z icemac $

import icemac.addressbook.generations.utils
import zope.authentication.interfaces
import zope.component


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(addressbook):
    "Register 'Flashed Session Credentials' at PAU."
    pau = zope.component.getUtility(
        zope.authentication.interfaces.IAuthentication)
    pau.credentialsPlugins = (u'No Challenge if Authenticated',
                              u'Flashed Session Credentials',)
