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
"""Configurator Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema

from z3c.configurator import interfaces

def getAdapterFactories(component, specific=True):
    """Get adapter registrations where @iface is provided and prefer
    the specific registrations."""
    iface =  interfaces.IConfigurationPlugin
    gsm = zope.component.getGlobalSiteManager()
    res = {}
    for reg in gsm.registeredAdapters():
        # Only get adapters for which this interface is provided
        if reg.provided is None or not reg.provided.isOrExtends(iface):
            continue
        if reg.required[0].providedBy(component):
            res[reg.name] = reg.factory
        if specific or reg.name in res:
            continue
        res[reg.name] = reg.factory
    return res

def requiredPlugins(component, names=[]):

    """returns a list of tuples of (name, pluginfactory) in the right
    order to be executed"""

    if not names:
        # get all names we have available
        names = getAdapterFactories(component,
                                    specific=True).keys()

    # we need this in order to get dependencies from plugins which are
    # not available in the unconfigured component because the provided
    # interfaces may change during execution
    plugins = getAdapterFactories(component,
                                  specific=False)

    def _add(name, res):
        if name in seen:
            return
        seen.add(name)
        deps = getattr(plugins[name], 'dependencies', ())
        for dep in deps:
            if not dep in res:
                _add(dep, res)
        if name not in res:
            res.append(name)
    seen = set()
    res = []
    for name in names:
        _add(name, res)
    return [(name, plugins[name]) for name in res]

def configure(component, data, names=[], useNameSpaces=False):

    plugins = requiredPlugins(component, names)

    for name, factory in plugins:
        if useNameSpaces is True:
            d = data.get(name, {})
        else:
            d = data
        plugin = factory(component)
        plugin(d)

@zope.interface.implementer(interfaces.IConfigurationPlugin)
class ConfigurationPluginBase(object):

    def __init__(self, context):
        self.context = context

    def __call__(self, data):
        raise NotImplementedError

@zope.interface.implementer(interfaces.ISchemaConfigurationPlugin)
class SchemaConfigurationPluginBase(object):
    schema = zope.interface.Interface

    def __init__(self, context):
        self.context = context

    def verify(self, data):
        for name, field in zope.schema.getFields(self.schema).items():
            field.validate(data.get(name))

    def __call__(self, data):
        raise NotImplementedError
