=================================
Setting Named Registries as Bases
=================================

While setting up named registries and filling them in ZCML is interesting in
itself, those features alone will not bring much, unless you can hook up those
named registries to local sites.

This is accomplished by setting the bases. Let's take our root folder, for
example. By default, only the global base registry is registered as a site. If
you have a quick look at ``ftesting.zcml``, you will notice that only
"example2" is available as named utility and "example1" as the unnamed one.

By setting the root folder site as the current site, we can simulate the
behavior of calling from within the root folder:

  >>> import zope.component
  >>> from zope.site import hooks

  >>> site = getRootFolder()
  >>> hooks.setSite(site)
  >>> site.getSiteManager().__bases__
  (<BaseGlobalComponents base>,)

  >>> zope.component.getUtility(IExample)
  <Example 'example1'>

  >>> zope.component.getUtility(IExample, name="example2")
  <Example 'example2'>

  >>> zope.component.getUtility(IExample, name="example4")
  Traceback (most recent call last):
  ...
  ComponentLookupError:
      (<InterfaceClass z3c.baseregistry.browser.ftests.IExample>, 'example4')

Let's now add the "custom" registry to the site as a base. After logging in ..

  >>> from zope.testbrowser.testing import Browser
  >>> manager = Browser()
  >>> manager.addHeader('Authorization', 'Basic mgr:mgrpw')

  >>> manager.open('http://localhost/manage')

you enter the site management area and then click on the "Bases" tab:

  >>> manager.getLink('Manage Site').click()
  >>> manager.getLink('Bases').click()

Let' now add the "custom" registry:

  >>> addBasesSelection(manager, ['-- Global Base Registry --', 'custom'])
  >>> manager.getControl('Apply').click()

Now, "example4" should be available, but "example3" is overridden by
"example1".

  >>> site = getRootFolder()
  >>> hooks.setSite(site)
  >>> site.getSiteManager().__bases__
  (<BaseGlobalComponents base>, <BaseComponents custom>)

  >>> zope.component.getUtility(IExample)
  <Example 'example1'>

  >>> zope.component.getUtility(IExample, name="example2")
  <Example 'example2'>

  >>> zope.component.getUtility(IExample, name="example4")
  <Example 'example4'>

However, if we change the order of the bases,

  >>> addBasesSelection(manager, ['custom', '-- Global Base Registry --'])
  >>> manager.getControl('Apply').click()

then "custom" registry overrides entries from the global base registry:

  >>> site = getRootFolder()
  >>> hooks.setSite(site)
  >>> site.getSiteManager().__bases__
  (<BaseComponents custom>, <BaseGlobalComponents base>)

  >>> zope.component.getUtility(IExample)
  <Example 'example3'>

  >>> zope.component.getUtility(IExample, name="example2")
  <Example 'example2'>

  >>> zope.component.getUtility(IExample, name="example4")
  <Example 'example4'>
