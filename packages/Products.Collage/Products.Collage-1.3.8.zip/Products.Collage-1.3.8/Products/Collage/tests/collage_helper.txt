Collage helper
==============

Let's create our Collage object.

  >>> catalog = self.portal.portal_catalog
  >>> _ = folder.invokeFactory(id='collage', type_name='Collage')
  >>> collage = folder[_]
  >>> _ = collage.invokeFactory(id='row', type_name='CollageRow')
  >>> row = collage[_]
  >>> _ = row.invokeFactory(id='column', type_name='CollageColumn')
  >>> column = row[_]

We add a simple document.

  >>> _ = column.invokeFactory(id='doc', type_name='Document')
  >>> doc = column[_]
  >>> helper = doc.restrictedTraverse('@@collage_helper')


We are in a collage.

  >>> helper.isCollageContent()
  True

Finding Collage parent.

  >>> helper.getCollageObject()
  <Collage at /plone/Members/test_user_1_/collage>

And its URL.

  >>> helper.getCollageObjectURL()
  'http://nohost/plone/Members/test_user_1_/collage'

The home page is not in a Collage.

  >>> homepage = self.portal['front-page']
  >>> helper = homepage.restrictedTraverse('@@collage_helper')
  >>> helper.isCollageContent()
  False

So, no Collage object.

  >>> helper.getCollageObject() is None
  True

An attempt to get at the collage object URL fails:

  >>> helper.getCollageObjectURL() is None
  Traceback (most recent call last):
   ...
  ValueError: Collage object not found.
