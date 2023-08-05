Layout for orphan alias
=======================

An orphan alias is a CollageAlias object which target object has been deleted.
We should assume that the layout for such alias is reset to the default one
'standard'.

This test checks the fix of issue #63
http://plone.org/products/collage/issues/63


Some inits
----------

  >>> from zope.component import getMultiAdapter
  >>> request = self.app.REQUEST
  >>> request.environ['REQUEST_METHOD'] = 'POST'
  >>> from Products.Collage.interfaces import IDynamicViewManager

Creating our Collage
--------------------

  >>> _ = folder.invokeFactory(id='collage', type_name='Collage')
  >>> collage = folder[_]
  >>> collage.setTitle('collagetitle')
  >>> collage.setDescription('collagedescription')
  >>> _ = collage.invokeFactory(id='row', type_name='CollageRow')
  >>> row = collage[_]
  >>> row.setTitle('rowtitle')
  >>> row.setDescription('rowdescription')
  >>> _ = row.invokeFactory(id='column', type_name='CollageColumn')
  >>> column = row[_]
  >>> column.setTitle('columntitle')
  >>> column.setDescription('columndescription')

We add our target object - a Folder
-----------------------------------

  >>> _ = folder.invokeFactory(id='foofolder', type_name='Folder')
  >>> foofolder = folder[_]
  >>> foofolder_uid = foofolder.UID()

We add this folder as alias in our collage
------------------------------------------

  >>> _ = getMultiAdapter((column, request), name=u'insert-alias')
  >>> request.set('uid', foofolder_uid)
  >>> idontcare = _.insertAlias()
  >>> column.objectIds()
  ['alias-1']
  >>> alias = column['alias-1']
  >>> alias.get_target()
  <ATFolder at ...>

We check we have the standard layout
------------------------------------

  >>> manager = IDynamicViewManager(alias)
  >>> manager
  <Products.Collage.viewmanager.DynamicViewManager object ...>
  >>> manager.getLayout() is None
  True

We change the cell layout
-------------------------

  >>> manager.setLayout(u'portlet')
  >>> manager.getLayout()
  u'portlet'

We remove the alias target
--------------------------

  >>> folder._delObject('foofolder')
  >>> 'foofolder' in folder.objectIds()
  False

The layout should be reset.

  >>> manager = IDynamicViewManager(alias)
  >>> manager.getLayout() is None
  True
