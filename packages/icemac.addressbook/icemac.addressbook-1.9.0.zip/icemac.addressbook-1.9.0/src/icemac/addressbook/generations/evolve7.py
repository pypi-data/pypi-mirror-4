# -*- coding: latin-1 -*-
# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id: evolve7.py 1453 2012-01-05 10:36:15Z icemac $

__docformat__ = "reStructuredText"


import icemac.addressbook.generations.utils


generation = 7


def evolve(context):
    """Install user defined fields utility.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
