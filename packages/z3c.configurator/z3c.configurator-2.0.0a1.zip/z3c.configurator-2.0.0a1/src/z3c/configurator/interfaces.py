##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Configurator Interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema


class CyclicDependencyError(ValueError):
    """Cyclic dependency of configuration plugins"""


class DataMissingError(ValueError):
    """Error raised when required data is missing during configuration
    execution."""


class IConfigurationPlugin(zope.interface.Interface):
    """An object executing one configuration step."""

    dependencies = zope.interface.Attribute(
        """A sequence of dependencies to other configuration plugins.""")

    def __call__(self, data):
        """Execute the configuration.

        The data is a dictionary containing values that might be of interest
        to the configuration plugin. When some required data field is missing,
        then raise a ``DataMissingError`` error.
        """


class ISchemaConfigurationPlugin(IConfigurationPlugin):
    """A configuration plugin that provides a data schema."""

    schema = zope.schema.Object(
        title=u"Configuration Schema",
        description=u"The schema describing the data fields needed.",
        schema=zope.interface.interfaces.IInterface)
