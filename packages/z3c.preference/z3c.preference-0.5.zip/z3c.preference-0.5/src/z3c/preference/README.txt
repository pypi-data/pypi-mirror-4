Overview
========

``z3c.preference`` renders forms in the browser for the preference
sets which were defined using zope.preference_.

.. _zope.preference: http://pypi.python.org/pypi/zope.preference

Using z3c.preference
====================

There are some preconditions to use `z3c.preference`:

* The views for the ``++preferences++`` namespace are registered for
  the layer ``z3c.preference.interfaces.IPreferenceLayer``. So you
  have to add this interface to the browser layer of your application.

* Only users having the permission ``z3c.preference.EditPreference``
  are allowed to access the the preference views. So you have to add this
  permission to the users resp. roles which should be able to access
  the preferences views.

Editing preferences
===================

Set up for tests
----------------

At first we have to define a preference interface:

  >>> import zope.interface
  >>> import zope.schema
  >>> class IBackEndSettings(zope.interface.Interface):
  ...     """Backend User Preferences"""
  ...
  ...     email = zope.schema.TextLine(
  ...         title=u"E-mail Address",
  ...         description=u"E-mail address used to send notifications")
  ...
  ...     skin = zope.schema.Choice(
  ...         title=u"Skin",
  ...         description=u"The skin that should be used for the back end.",
  ...         values=['Hipp', 'Lame', 'Basic'],
  ...         default='Basic')
  ...
  ...     showLogo = zope.schema.Bool(
  ...         title=u"Show Logo",
  ...         description=u"Specifies whether the logo should be displayed.",
  ...         default=True)

The interface must be registered for preferences:

  >>> from zope.configuration import xmlconfig
  >>> import zope.preference
  >>> context = xmlconfig.file('meta.zcml', zope.preference)

  >>> context = xmlconfig.string('''
  ...     <configure
  ...         xmlns="http://namespaces.zope.org/zope"
  ...         i18n_domain="test">
  ...
  ...       <preferenceGroup
  ...           id="BackEndSettings"
  ...           title="Back End Settings"
  ...           schema="z3c.preference.README.IBackEndSettings"
  ...           />
  ...
  ...     </configure>''', context)


To access the forms a browser is needed, the user must be authorized as
the preferences are stored in the principal annotations:

>>> from zope.app.wsgi.testlayer import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')


Editing preferences using browser
---------------------------------

There is a namespace to access the preferences. On the page a form is
displayed which shows the default values:

>>> browser.open('http://localhost/++preferences++/BackEndSettings')
>>> browser.getControl('E-mail Address').value
''
>>> browser.getControl('Skin').displayValue
['Basic']
>>> browser.getControl('yes').selected
True
>>> browser.getControl('no').selected
False

The values can be changed and submitting the form makes them persistent:

>>> browser.getControl('E-mail Address').value = 'me@example.com'
>>> browser.getControl('Skin').displayValue = ['Hipp']
>>> browser.getControl('no').click()
>>> browser.getControl('Apply').click()

After submitting the form gets displayed again and shows the changed values:

>>> 'Data successfully updated.' in browser.contents
True
>>> browser.getControl('E-mail Address').value
'me@example.com'
>>> browser.getControl('Skin').displayValue
['Hipp']
>>> browser.getControl('no').selected
True
