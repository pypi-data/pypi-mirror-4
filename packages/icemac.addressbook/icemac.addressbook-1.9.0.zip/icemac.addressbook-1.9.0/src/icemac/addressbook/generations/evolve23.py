# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id: evolve23.py 1463 2012-01-06 13:18:53Z icemac $

import icemac.addressbook.generations.utils


def evolve(context):
    """Install update default preferences to new prefs structure.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
