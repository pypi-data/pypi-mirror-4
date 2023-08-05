# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id: __init__.py 1454 2012-01-05 10:36:41Z icemac $
"""Database initialisation and upgrading."""

import zope.generations.generations


GENERATION = 0


manager = zope.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.ab.importer.generations')
