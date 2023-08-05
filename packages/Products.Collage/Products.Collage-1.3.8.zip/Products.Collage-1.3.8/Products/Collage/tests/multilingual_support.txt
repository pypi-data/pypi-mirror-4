Multilinguality
===============

This doctest gives an overview of how content translated via LinguaPlone is handled by Collage.

Setting up
----------

First of all, check if LinguaPlone is available.

    >>> try:
    ...   from Products.LinguaPlone.interfaces import ITranslatable
    ... except ImportError:
    ...   HAS_LINGUAPLONE = False
    ... else:
    ...   HAS_LINGUAPLONE = True

Build a basic Collage:

    >>> _ = folder.invokeFactory(id='collage', type_name='Collage')
    >>> collage = folder[_]
    >>> _ = collage.invokeFactory(id='row', type_name='CollageRow')
    >>> row = collage[_]
    >>> _ = row.invokeFactory(id='column', type_name='CollageColumn')
    >>> column = row[_]
    >>> _ = column.invokeFactory(id='alias', type_name='CollageAlias')
    >>> alias = column[_]

We need the language tool for this. Make sure start_neutral is set to 0 (it's the default, 
but using belts and suspenders won't harm us...)

    >>> ltool = self.portal.portal_languages
    >>> ltool.start_neutral = 0

Add two more language beside English to the language tool.

    >>> ltool.addSupportedLanguage('da')
    >>> ltool.addSupportedLanguage('de')
    >>> ltool.getSupportedLanguages()
    ['en', 'da', 'de']

The default language is English.

    >>> ltool.getPreferredLanguage()
    'en'


Alias
-----

Now we add a document (which is translatable) to the folder.

    >>> _ = folder.invokeFactory(id='doc', type_name='Document')
    >>> doc = folder[_]
    >>> doc.Language()
    'en'
    
The document receives a title.

    >>> doc.setTitle('English title')
    >>> doc.Title()
    'English title'

We add a Danish translation of that document.

    >>> doc.addTranslation('da')
    >>> doc_da = doc.getTranslation('da')
    >>> doc_da.Language()
    'da'

And the Danish version also gets a title.

    >>> doc_da.setTitle('Danish title')
    >>> doc_da.Title()
    'Danish title'

The document (canonical English version) is set as a target of the alias.

    >>> alias.set_target(doc.UID())
    >>> alias.get_target().Title()
    'English title'

Now we switch the preferred language to Danish.
Important: we have to invalidate the language binding, or else the new language won't get set.

    >>> ltool.REQUEST['LANGUAGE_TOOL'] = None
    >>> ltool.REQUEST['set_language'] = 'da'
    >>> ltool.use_cookie_negotiation = 1
    >>> ltool.getPreferredLanguage()
    'da'

If LinguaPlone is installed we will get the Danish title, 
or the default English title if it is not.

    >>> if HAS_LINGUAPLONE:
    ...   if alias.get_target().Title() != 'Danish title': raise ValueError
    ... else:
    ...   if alias.get_target().Title() != 'English title': raise ValueError

Now we switch the preferred language to German

    >>> ltool.REQUEST['LANGUAGE_TOOL'] = None
    >>> ltool.REQUEST['set_language'] = 'de'
    >>> ltool.use_cookie_negotiation = 1
    >>> ltool.getPreferredLanguage()
    'de'

If we look at the alias now, we will get get the English title, 
since a German version of the target is not available.

    >>> alias.get_target().Title()
    'English title'


Local content
-------------

Switch the language back to English.

    >>> ltool.REQUEST['LANGUAGE_TOOL'] = None
    >>> ltool.REQUEST['set_language'] = 'en'
    >>> ltool.use_cookie_negotiation = 1
    >>> ltool.getPreferredLanguage()
    'en'

Now we add another column, so that we can play around with content inside the collage object.
Also, we need to get the renderer for this column.

    >>> _ = row.invokeFactory(id='column2', type_name='CollageColumn')
    >>> column2 = row[_]
    >>> renderer = column2.restrictedTraverse('@@renderer')

At first, the renderer's getItems return an empty list.

    >>> renderer.getItems()
    []

We add a document to the new column. Its language will automatically be set to English.
    >>> _ = column2.invokeFactory(id='localdoc', type_name='Document')
    >>> localdoc = column2[_]
    >>> localdoc.Language()
    'en'

As before, the document receives a title.

    >>> localdoc.setTitle('English title')
    >>> localdoc.Title()
    'English title'

The renderer now returns one item.

    >>> len(renderer.getItems())
    1
    >>> renderer.getItems()[0].context.Title()
    'English title'

We add a Danish translation of the document. The translation will be contained inside column2.

    >>> localdoc.addTranslation('da')
    >>> localdoc_da = localdoc.getTranslation('da')
    >>> localdoc_da.Language()
    'da'
    >>> localdoc_da.setTitle('Danish title')
    >>> localdoc_da.aq_parent.id
    'column2'

There are now 2 items inside column2, but only the English one is returned by the renderer, if
LinguaPlone is present.

    >>> len(column2.objectValues())
    2
    >>> if HAS_LINGUAPLONE:
    ...    if len(renderer.getItems()) != 1: raise ValueError
    ...    if renderer.getItems()[0].context.Title() != 'English title': raise ValueError
    ... else:
    ...    if len(renderer.getItems()) != 2: raise ValueError
    ...    if 'Danish title' not in [x.context.Title() for x in renderer.getItems()] : raise ValueError
    ...    if 'English title' not in [x.context.Title() for x in renderer.getItems()] : raise ValueError
    

We switch the language to Danish again.

    >>> ltool.REQUEST['LANGUAGE_TOOL'] = None
    >>> ltool.REQUEST['set_language'] = 'da'
    >>> ltool.use_cookie_negotiation = 1
    >>> ltool.getPreferredLanguage()
    'da'

The renderer still only returns one item, but this time the Danish one.

    >>> if HAS_LINGUAPLONE:
    ...    if len(renderer.getItems()) != 1: raise ValueError
    ...    if renderer.getItems()[0].context.Title() != 'Danish title': raise ValueError
    ... else:
    ...    if len(renderer.getItems()) != 2: raise ValueError
    ...    if 'Danish title' not in [x.context.Title() for x in renderer.getItems()] : raise ValueError
    ...    if 'English title' not in [x.context.Title() for x in renderer.getItems()] : raise ValueError


Now we switch the language to German again.

    >>> ltool.REQUEST['LANGUAGE_TOOL'] = None
    >>> ltool.REQUEST['set_language'] = 'de'
    >>> ltool.use_cookie_negotiation = 1
    >>> ltool.getPreferredLanguage()
    'de'

As there is no German version of localdoc, the canonical English version is returned.

    >>> if HAS_LINGUAPLONE:
    ...    if len(renderer.getItems()) != 1: raise ValueError
    ...    if renderer.getItems()[0].context.Title() != 'English title': raise ValueError
    ... else:
    ...    if len(renderer.getItems()) != 2: raise ValueError
    ...    if 'Danish title' not in [x.context.Title() for x in renderer.getItems()] : raise ValueError
    ...    if 'English title' not in [x.context.Title() for x in renderer.getItems()] : raise ValueError

Finally, we add yet another document to column2, but declare it to be language neutral.

    >>> _ = column2.invokeFactory(id='neutraldoc', type_name='Document')
    >>> neutraldoc = column2[_]
    >>> neutraldoc.setLanguage('')
    >>> neutraldoc.setTitle('Neutral title')
    >>> neutraldoc.Language()
    ''

The language neutral document will always be shown.

    >>> if HAS_LINGUAPLONE:
    ...    if len(renderer.getItems()) != 2: raise ValueError
    ...    if 'English title' not in [x.context.Title() for x in renderer.getItems()] : raise ValueError
    ...    if 'Neutral title' not in [x.context.Title() for x in renderer.getItems()] : raise ValueError
    ... else:
    ...    if len(renderer.getItems()) != 3: raise ValueError
    ...    if 'Danish title' not in [x.context.Title() for x in renderer.getItems()] : raise ValueError
    ...    if 'English title' not in [x.context.Title() for x in renderer.getItems()] : raise ValueError
    ...    if 'Neutral title' not in [x.context.Title() for x in renderer.getItems()] : raise ValueError

We can switch to any other language, the neutral doc will be displayed.

    >>> ltool.REQUEST['LANGUAGE_TOOL'] = None
    >>> ltool.REQUEST['set_language'] = 'da'
    >>> ltool.use_cookie_negotiation = 1
    >>> ltool.getPreferredLanguage()
    'da'

    >>> if HAS_LINGUAPLONE:
    ...    if len(renderer.getItems()) != 2: raise ValueError
    ...    if 'Danish title' not in [x.context.Title() for x in renderer.getItems()] : raise ValueError
    ...    if 'Neutral title' not in [x.context.Title() for x in renderer.getItems()] : raise ValueError
    ... else:
    ...    if len(renderer.getItems()) != 3: raise ValueError
    ...    if 'Danish title' not in [x.context.Title() for x in renderer.getItems()] : raise ValueError
    ...    if 'English title' not in [x.context.Title() for x in renderer.getItems()] : raise ValueError
    ...    if 'Neutral title' not in [x.context.Title() for x in renderer.getItems()] : raise ValueError
