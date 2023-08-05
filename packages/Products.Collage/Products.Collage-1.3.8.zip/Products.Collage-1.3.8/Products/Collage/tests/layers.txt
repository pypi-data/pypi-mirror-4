Registering Collage views on theme-specific layers
--------------------------------------------------

It's possible to create a Collage-compatible theme-specific layer.
This is necessary if you want to add or override a Collage view
but only for sites with a particular theme installed.

As we begin, there should be a 'fallback' view with the title 'fallback'::

  >>> from Products.Collage.interfaces import IDynamicViewManager
  >>> vm = IDynamicViewManager(self.portal)
  >>> vm.getLayouts()
  [(u'fallback', u'fallback')]

We're going to override it.  Let's create our theme-specific marker interface::

  >>> from zope.interface import Interface
  >>> class IMyCollageLayer(Interface):
  ...     pass
  
And we need to register this marker interface as a Collage theme-specific layer
for a particular theme (Plone Default, here) -- normally this is done with the
<interface> directive in ZCML)::

  >>> from Products.Collage.interfaces import ICollageBrowserLayerType
  >>> from zope.component.interface import provideInterface
  >>> default_skin = self.portal.portal_skins.getDefaultSkin()
  >>> provideInterface(default_skin, IMyCollageLayer, iface_type=ICollageBrowserLayerType)

Also let's register a faux view on this layer::

  >>> from Products.Five import BrowserView
  >>> class MyView(BrowserView):
  ...     title = u'foobar'
  >>> from zope.component import getGlobalSiteManager
  >>> gsm = getGlobalSiteManager()
  >>> gsm.registerAdapter(MyView, required=(Interface, IMyCollageLayer), provided=Interface, name=u'fallback')

Now if we look up the layouts again we should get our replacement::

  >>> vm.getLayouts()
  [(u'fallback', u'foobar')]
  
Cleanup::

  >>> gsm.unregisterAdapter(MyView, required=(Interface, IMyCollageLayer), provided=Interface, name=u'fallback')
  True
