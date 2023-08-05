# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id: evolve19.py 1459 2012-01-06 10:41:33Z icemac $

import icemac.addressbook.generations.utils


def evolve(context):
    """Install local principal annotation utility.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
