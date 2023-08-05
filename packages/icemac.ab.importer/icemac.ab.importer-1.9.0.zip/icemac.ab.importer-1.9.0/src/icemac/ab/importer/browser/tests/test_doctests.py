# -*- coding: latin-1 -*-
# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id: test_doctests.py 1454 2012-01-05 10:36:41Z icemac $

import icemac.addressbook.testing
import icemac.ab.importer.browser.testing


def test_suite():
    return icemac.addressbook.testing.DocFileSuite(
        "importer.txt",
        "masterdata.txt",
        package='icemac.ab.importer.browser',
        layer=icemac.ab.importer.browser.testing.ImporterLayer,
        )
