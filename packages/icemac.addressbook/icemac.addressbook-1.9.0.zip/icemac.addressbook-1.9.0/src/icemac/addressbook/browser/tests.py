# -*- coding: latin-1 -*-
# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id: tests.py 1453 2012-01-05 10:36:15Z icemac $

import icemac.addressbook.browser.testing
import icemac.addressbook.testing
import zope.testing.renormalizing


def test_suite():
    suite = icemac.addressbook.testing.TestBrowserDocFileSuite(
        "browser/about/about.txt",
        "browser/addressbook/addressbook.txt",
        "browser/authentication/login.txt",
        "browser/entities/bugfix.txt",
        "browser/entities/delete_choice_value.txt",
        "browser/entities/entities.txt",
        "browser/entities/file.txt",
        "browser/entities/sortorder-fields.txt",
        "browser/entities/sortorder.txt",
        "browser/keyword/keyword.txt",
        "browser/masterdata/masterdata.txt",
        "browser/person/clone.txt",
        "browser/person/file.txt",
        "browser/person/person.txt",
        "browser/person/sortorder.txt",
        "browser/person/translation.txt",
        "browser/principals/principals.txt",
        "browser/rootfolder/rootfolder.txt",
        "browser/search/result/handler/export/translation.txt",
        "browser/search/result/handler/export/userfields.txt",
        )
    suite.addTest(
        icemac.addressbook.testing.DocFileSuite(
            "browser/search/result/handler/delete.txt",
            "browser/search/result/handler/export/export.txt",
            "browser/search/search.txt",
            layer=icemac.addressbook.browser.testing.WSGI_SEARCH_LAYER
            ))
    suite.addTest(
        icemac.addressbook.testing.TestBrowserDocFileSuite(
            # Tests which must not run with the default <DATETIME> normalizer:
            "browser/metadata.txt",
            checker=zope.testing.renormalizing.RENormalizing([])))
    return suite
