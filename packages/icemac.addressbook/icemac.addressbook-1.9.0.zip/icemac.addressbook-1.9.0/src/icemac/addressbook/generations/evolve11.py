# -*- coding: latin-1 -*-
# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id: evolve11.py 1453 2012-01-05 10:36:15Z icemac $

import icemac.addressbook.generations.utils


def evolve(context):
    """Install batch size in default preferences provider.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
