Indexing of Collage objects
===========================

Settings and utilities

  >>> def makeSet(text):
  ... 	  words = [w.strip() for w in text.split() if w.strip()]
  ...	  return set(words)

Let's create our Collage object.

  >>> catalog = self.portal.portal_catalog
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

By default, subcontents are not indexed on Collage

  >>> collage.mustIndexSubobjects()
  False

Let's see its default searchable text.

  >>> collageonly_st = makeSet(collage.SearchableText())
  >>> len(collageonly_st)
  6

We add a simple document.

  >>> _ = column.invokeFactory(id='doc', type_name='Document')
  >>> doc = column[_]
  >>> doc.edit(title='doctitle')
  >>> brains = catalog.searchResults(SearchableText='doctitle')
  >>> len(brains)
  1

Document is not indexed in collage.

  >>> collageonly_st = makeSet(collage.SearchableText())
  >>> len(collageonly_st)
  6
  >>> 'doctitle' in collageonly_st
  False

We index now collage subcontents.

  >>> collage.edit(index_subobjects=True)
  >>> collage.mustIndexSubobjects()
  True

Document's SearchableText is included in collage.

  >>> collageonly_st = makeSet(collage.SearchableText())
  >>> len(collageonly_st)
  8
  >>> 'doctitle' in collageonly_st
  True

Collage should already be indexed.

  >>> catalog = self.portal.portal_catalog
  >>> brains = catalog.searchResults(SearchableText='doctitle')
  >>> len(brains)
  2
  >>> targets = [b.getURL() for b in brains]
  >>> 'http://nohost/plone/Members/test_user_1_/collage' in targets
  True
