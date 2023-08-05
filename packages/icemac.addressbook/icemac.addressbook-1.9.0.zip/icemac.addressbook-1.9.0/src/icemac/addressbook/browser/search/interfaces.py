# -*- coding: latin-1 -*-
# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id: interfaces.py 1453 2012-01-05 10:36:15Z icemac $

import z3c.menu.ready2go
import zope.interface
import zope.viewlet.interfaces


class ISearchMenu(z3c.menu.ready2go.ISiteMenu):
    """Search menu."""


class ISearchForm(zope.viewlet.interfaces.IViewletManager):
    """Search form manager."""


class ISearchResult(zope.viewlet.interfaces.IViewletManager):
    """Search form manager."""


class ISearch(zope.interface.Interface):
    """A search."""

    def search(**kw):
        "Search for given keyword arguments and return iterable of results."
