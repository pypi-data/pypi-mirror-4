# -*- coding: latin-1 -*-
# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id: interfaces.py 1453 2012-01-05 10:36:15Z icemac $

import zope.interface


class IExporter(zope.interface.Interface):
    """Exporting facility."""

    file_extension = zope.interface.Attribute(
        u'Extension (without the leading dot!) to be set on export file name.')
    mime_type = zope.interface.Attribute(u'Mime-type of the export file.')

    def export():
        """Export to a file.

        Returns a file or file-like-object.

        """
