from zope import interface
from zope import schema

from zope import formlib
from zope.formlib import form
from zope.browserpage import namedtemplate
from zope.browserpage import ViewPageTemplateFile
from z3c.configurator import interfaces
from z3c.configurator.i18n import _
from z3c.configurator import configurator


class SelectPlugins(form.PageForm):

    """a form to choose plugins, to be applied"""

    form_fields = form.Fields(
        schema.Choice(__name__=u'pluginName',
                      title=_(u'Plugin Name'),
                      vocabulary="Configurator Plugin Names")
        )

    @form.action(label=_(u'Apply Configuration'))
    def selectPlugins(self, action, data):
        pluginName = data.get('pluginName')
        configurator.configure(self.context, names=[pluginName])
        self.status = _('Configuration applied')


class IGenerateSchema(interface.Interface):
    """Schema for the minimal generator parameters"""

    seed = schema.TextLine(
            title = _(u'Seed'),
            description =  _(u'A seed for the random generator'),
            default = u'sample',
            required=False,
            )


class ConfigureForm(form.PageForm):
    """Configurator Plugin form"""

    base_template = form.EditForm.template
    template = ViewPageTemplateFile('configure.pt')
    subforms = []

    form_fields = form.Fields(
        schema.List(__name__=u'pluginNames',
                    title=u'Plugin Names',
                    value_type=schema.Choice(
        __name__=u'pluginName',
        title=_(u'Plugin Name'),
        vocabulary="Configurator Plugin Names")
        ))

    workDone = False

    @property
    def _pluginNames(self):
        names = self.request.form.get(self.prefix + '.pluginNames')
        if names and not type(names) is type([]):
            return [names]
        return names

    def setUpWidgets(self, ignore_request=False):
        if self._pluginNames:
            plugins = configurator.requiredPlugins(self.context,
                                                   self._pluginNames)
            self.subforms = []
            for name, factory in plugins:
                plugin = factory(self.context)
                if not interfaces.ISchemaConfigurationPlugin.providedBy(
                    plugin):
                    continue
                subform = PluginSchemaForm(context=self.context,
                                           request=self.request,
                                           plugin=plugin,
                                           prefix=name)
                subform.form_fields = form.Fields(plugin.schema)
                self.subforms.append(subform)
        super(ConfigureForm, self).setUpWidgets(ignore_request=ignore_request)

    @form.action(_("Update"))
    def handleUpdate(self, action, data):
        if not self._pluginNames:
            return
        self.setUpWidgets(ignore_request=False)
        result = self.template()
        return result

    def _pluginsSelected(self, action):
        return not not self.request.form.get(self.prefix + '.pluginNames')

    @form.action(_("Apply"), condition='_pluginsSelected')
    def handleApply(self, action, data):

        configuratorData = {}
        for subform in self.subforms:
            subform.update()
            formData = {}
            errors = form.getWidgetsData(subform.widgets,
                                         subform.prefix,
                                         formData)
            configuratorData[subform.prefix] = formData

        configurator.configure(self.context,
                               configuratorData,
                               names=self._pluginNames,
                               useNameSpaces=True)
        self.status = u'Applied: %s' % u' '.join(self._pluginNames)


class PluginSchemaForm(form.AddForm):
    """An editor for a single schema based plugin"""
    interface.implements(formlib.interfaces.ISubPageForm)
    template = namedtemplate.NamedTemplate('default')
    actions = []

    def __init__(self, context, request, plugin=None,
                 schema=None, prefix=''):
        self.plugin = plugin
        self.schema = schema
        self.prefix = prefix
        super(PluginSchemaForm, self).__init__(context, request)
