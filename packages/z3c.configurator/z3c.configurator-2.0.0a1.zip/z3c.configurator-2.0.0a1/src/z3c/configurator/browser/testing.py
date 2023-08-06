"""Some test classes
"""
from z3c.configurator import configurator
from zope import interface
from zope import component
from zope import schema
from zope.dublincore.interfaces import IZopeDublinCore
from zope.annotation.interfaces import IAttributeAnnotatable

class ISingleArg(interface.Interface):

    arg = schema.TextLine(title=u'Some Argument')

class SetTitle(configurator.SchemaConfigurationPluginBase):
    """makes an object implement IFoo"""
    component.adapts(IAttributeAnnotatable)
    schema = ISingleArg

    def __call__(self, data):
        dc = IZopeDublinCore(self.context)
        dc.title = data.get('arg')

class SetDescription(configurator.SchemaConfigurationPluginBase):

    component.adapts(IAttributeAnnotatable)
    schema = ISingleArg

    def __call__(self, data):
        dc = IZopeDublinCore(self.context)
        dc.description = data.get('arg')
