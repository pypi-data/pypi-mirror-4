# -*- coding: latin-1 -*-
# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id: interfaces.py 1453 2012-01-05 10:36:15Z icemac $

import z3c.menu.ready2go


class IMainMenu(z3c.menu.ready2go.ISiteMenu):
    """Main menu."""


class IAddMenu(z3c.menu.ready2go.IAddMenu):
    """Add menu."""
