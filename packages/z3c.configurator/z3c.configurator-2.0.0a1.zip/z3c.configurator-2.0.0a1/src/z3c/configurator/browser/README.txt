=========================
Calling Configurators TTW
=========================

A configuration view is registered to apply named configuration on any
object.  We defined two example configurators which we now gonna apply
to the site object.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization','Basic mgr:mgrpw')
  >>> browser.handleErrors = False

  >>> browser.open('http://localhost/manage')
  >>> browser.url
  'http://localhost/@@contents.html'

The view is registered in the zmi_views menu

  >>> browser.getLink(u'Configurators').click()
  >>> viewURL = browser.url
  >>> viewURL
  'http://localhost/@@configurators.html'

  >>> sel = browser.getControl(name="form.pluginNames.to")

First we can choose from the registered named plugins.

  >>> plugs = browser.getControl(name="form.pluginNames.from").options
  >>> sorted(plugs)
  ['z3c.configurator.testing.setdescription',
   'z3c.configurator.testing.settitle']
  >>> browser.open(viewURL + '?form.pluginNames=z3c.configurator.testing.settitle')

We have choosen a plugin, so now we have a form for the arguments needed.

  >>> browser.getControl('Some Argument').value
  ''
  >>> browser.getControl('Some Argument').value = "New Title"
  >>> browser.getControl('Apply').click()


XXX form.pluginNames have to be set, but we can't because the widget
uses javascript.


