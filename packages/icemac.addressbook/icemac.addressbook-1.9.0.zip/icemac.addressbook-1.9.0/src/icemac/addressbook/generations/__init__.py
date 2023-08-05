# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id: __init__.py 1487 2012-04-20 18:42:23Z icemac $
"""Database initialisation and upgrading."""

import zope.generations.generations


GENERATION = 24


manager = zope.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.addressbook.generations')
