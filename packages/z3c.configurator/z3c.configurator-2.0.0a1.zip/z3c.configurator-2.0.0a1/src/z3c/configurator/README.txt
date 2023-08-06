================
The Configurator
================

The configurator is designed to extend a component after its
creation. Traditionally this is done by listening to ``ObjectCreatedEvent``
events. However, this low-level method does not suffice, since configuration
often depends on other configuration steps and additional data is often needed
to complete the configuration. And this is where the configurator comes
in. It uses a separate plugin mechanism to implement the mentioned high-level
functionality.

Before we can demonstrate the configuration mechanism, we'll have to create an
interface and a component on which the configuration can act upon:

  >>> import zope.interface

  >>> class ISomething(zope.interface.Interface):
  ...     """Some interesting interface."""

  >>> @zope.interface.implementer(ISomething)
  ... class Something(object):
  ...     """Implementation of something."""

  >>> something = Something()

Now we can have the configuration act on the component:

  >>> from z3c import configurator
  >>> configurator.configure(something, {})

The second argument is the data dictionary, which can be used to pass in
additional information that might be needed during the configuration. It is up
to each plugin to interpret the data.

Of course nothing happens, since no configuration plugins are
registered. Let's now create a new configuration plugin, which sets a new
attribute on the component:

  >>> import zope.component
  >>> from z3c.configurator import interfaces

  >>> class AddFooAttribute(configurator.ConfigurationPluginBase):
  ...     zope.component.adapts(ISomething)
  ...
  ...     def __call__(self, data):
  ...         setattr(self.context, 'foo', data.get('foo'))

  >>> zope.component.provideAdapter(AddFooAttribute, name='add foo')

If we execute the configuration again, the attribute will be added:

  >>> configurator.configure(something, {'foo': u'my value'})
  >>> something.foo
  u'my value'


Dependencies
------------

Now that we have simple configuration plugins, we can also develop plugins
that depend on another one. Let's create a configuration plugin that adds some
additional data to the foo attribute. Clearly, the foo attribute has to exist
before this step can be taken. The ``dependencies`` attribute can be used to
specify all plugin dependencies by name:

  >>> class ExtendFooAttribute(configurator.ConfigurationPluginBase):
  ...     zope.component.adapts(ISomething)
  ...     dependencies = ('add foo',)
  ...
  ...     def __call__(self, data):
  ...         self.context.foo = u'Text: ' + self.context.foo

  >>> zope.component.provideAdapter(ExtendFooAttribute, name='extend foo')

If we now execute the configuration again, the extended result should be seen:

  >>> something = Something()
  >>> configurator.configure(something, {'foo': u'my value'})
  >>> something.foo
  u'Text: my value'


Data Schemas
------------

For purely informational purposes, a ``schema`` attribute is used on the
plugin to describe the fields that the plugin expects from the data
dictionary. For adding another simple attribute, this could look as follows:

  >>> import zope.schema
  >>> class IAddBar(zope.interface.Interface):
  ...     bar = zope.schema.Text(title=u'Bar')

  >>> class AddBarAttribute(configurator.SchemaConfigurationPluginBase):
  ...     zope.component.adapts(ISomething)
  ...     schema = IAddBar
  ...
  ...     def __call__(self, data):
  ...         self.verify(data)
  ...         setattr(self.context, 'bar', data.get('bar'))

  >>> zope.component.provideAdapter(AddBarAttribute, name='add bar')

The advantage of using the base class for this case is that it provides a
``verify()`` method that allows you to verify the data against the shema. We
can now run the configuration again:

  >>> something = Something()
  >>> configurator.configure(something, {'foo': u'my value', 'bar': u'value'})
  >>> something.bar
  u'value'

The value must exist and be valid:

  >>> something = Something()
  >>> configurator.configure(something, {'foo': u'my value'})
  Traceback (most recent call last):
  ...
  RequiredMissing: bar

  >>> something = Something()
  >>> configurator.configure(something, {'foo': u'my value', 'bar': 1})
  Traceback (most recent call last):
  ...
  WrongType: (1, <type 'unicode'>, 'bar')


Data Namespaces
---------------

In order to not confuse attribute names if two plugins share a common
name it is possible to pass data as a dictionary of dictionaries. The
keys of the dictionary is the name under which the plugins are
registered.

  >>> something = Something()
  >>> data = {u'add foo': {'foo': u'foo value'},
  ...         u'add bar': {'bar': u'bar value'}}
  >>> configurator.configure(something, data, useNameSpaces=True)
  >>> something.foo, something.bar
  (u'Text: foo value', u'bar value')

Named Configuration
-------------------

Sometimes we do not want all registered configuration plugins to be
executed. This can be achieved by providing the names argument to the
configure function.

Let us create a new something:

  >>> something = Something()

If we now configure it without names we get both attributes set.

  >>> configurator.configure(something, {'foo': u'my value', 'bar': u'asdf'})
  >>> sorted(something.__dict__.items())
  [('bar', 'asdf'), ('foo', 'Text: my value')]

Now let us just configure the plugin 'add bar'.

  >>> something = Something()
  >>> configurator.configure(something, {'foo': u'my value', 'bar': u'asdf'},
  ...     names=['add bar'])
  >>> something.__dict__
  {'bar': u'asdf'}

Dependencies of plugins are always executed - they don't have to be
added to the ```names``` argument.

  >>> something = Something()
  >>> configurator.configure(something, {'foo': u'my value'},
  ...     names=['extend foo'])
  >>> something.foo
  u'Text: my value'

Named configurations are usefull when called manually through the web
(see browser/README.txt). The configurator package does not look if a
configuration is already applied if called twice. It is the
responsibility of the plugin to be aware that it doesn't do things
twice or delete things.


Wrong Implementations
---------------------

A configurator must provide a __call__ method.

  >>> class CallNotImplemented(configurator.ConfigurationPluginBase):
  ...     zope.component.adapts(ISomething)
  >>> zope.component.provideAdapter(CallNotImplemented, name='no call')

  >>> configurator.configure(something, None,  names=['no call'])
  Traceback (most recent call last):
  ...
  NotImplementedError

The same must happen for a schema base configurator.

  >>> class SchemaCallNotImplemented(configurator.SchemaConfigurationPluginBase):
  ...     zope.component.adapts(ISomething)
  >>> zope.component.provideAdapter(SchemaCallNotImplemented, name='schema no call')

  >>> configurator.configure(something, None,  names=['schema no call'])
  Traceback (most recent call last):
  ...
  NotImplementedError


No Recursion
------------

It's possible to define recursive dependencies without to run into recursion 
errors. Let's define a new plugin free object:

  >>> class IFoo(zope.interface.Interface):
  ...     """Just a foo interface."""

  >>> @zope.interface.implementer(IFoo)
  ... class Foo(object):
  ...     """Implementation of foo."""

Let's define another plugin named `first` which depends on a plugin named 
`second`.

  >>> log = []
  >>> class FirstPlugin(configurator.ConfigurationPluginBase):
  ...     zope.component.adapts(IFoo)
  ...     dependencies = ('second',)
  ...
  ...     def __call__(self, data):
  ...         log.append('FirstPlugin called')

  >>> zope.component.provideAdapter(FirstPlugin, name='first')

And define a plugin named `second` which depends on `first`:

  >>> class SecondPlugin(configurator.ConfigurationPluginBase):
  ...     zope.component.adapts(IFoo)
  ...     dependencies = ('first',)
  ...
  ...     def __call__(self, data):
  ...         log.append('SecondPlugin called')

  >>> zope.component.provideAdapter(SecondPlugin, name='second')

  >>> foo = Foo()
  >>> configurator.configure(foo, {})
  >>> for msg in sorted(log): print(msg)
  FirstPlugin called
  SecondPlugin called
