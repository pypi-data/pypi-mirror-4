# Copyright (c) 2010-2012 Michael Howitz
# See also LICENSE.txt
# $Id: evolve14.py 1453 2012-01-05 10:36:15Z icemac $

import icemac.addressbook.generations.utils
import icemac.addressbook.interfaces
import zope.component


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(addressbook):
    "Create person defaults entity and add it to sort order."
    person_defaults = icemac.addressbook.interfaces.IEntity(
        icemac.addressbook.interfaces.IPersonDefaults)
    order_storage = zope.component.getUtility(
        icemac.addressbook.interfaces.IOrderStorage)
    order_storage.add(
        person_defaults.name, icemac.addressbook.interfaces.ENTITIES)
    person_defaults_pos = order_storage.get(
        person_defaults.name, icemac.addressbook.interfaces.ENTITIES)
    delta = person_defaults_pos - 3
    order_storage.up(
        person_defaults.name, icemac.addressbook.interfaces.ENTITIES, delta)
