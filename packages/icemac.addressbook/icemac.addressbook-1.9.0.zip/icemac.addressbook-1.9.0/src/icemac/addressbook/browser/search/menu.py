# -*- coding: latin-1 -*-
# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id: menu.py 1453 2012-01-05 10:36:15Z icemac $

import zope.viewlet.manager
import z3c.menu.ready2go
import z3c.menu.ready2go.manager


SearchMenu = zope.viewlet.manager.ViewletManager(
    'left', z3c.menu.ready2go.IContextMenu,
    bases=(z3c.menu.ready2go.manager.MenuManager,))
