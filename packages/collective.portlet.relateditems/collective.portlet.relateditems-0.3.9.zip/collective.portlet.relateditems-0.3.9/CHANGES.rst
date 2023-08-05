Change History
==============

0.3.9 (2012-11-22)
------------------

- Fix package distribution.
  [hvelarde]


0.3.8 (2012-10-31)
------------------

- Portlet uses property 'typesUseViewActionInListings' to determine whether
  /view should be appended to the URL of the item.
  [huubbouma]


0.3.7 (2012-10-14)
------------------

- Fixed long description of package.
  [maurits]


0.3.6 (2012-10-14)
------------------

- Moved to
  https://github.com/collective/collective.portlet.relateditems
  [maurits]


0.3.5 (2011-12-01)
------------------

- Make sure the portlet title in @@manage-portlets is translated in
  both Plone 3 (i18n) and Plone 4 (locales).
  [maurits]

- Use the required plone domain in portlets.xml.
  [maurits]

- Added Dutch translations.
  [maurits]

- Added MANIFEST.in so .mo files are included in the distribution
  when available (see zest.pocompile plus zest.releaser).
  [maurits]

- Fixed error where 'only_subject' was always True after portlet creation.
  [maurits]

- Restored compatibility with earlier Plone versions by loading the
  CMFCore permissions.zcml only on Plone 4.1 or higher.
  [maurits]

- Added z3c.autoinclude entry point for plone, so you do not need to
  add this to the zcml option of your buildout anymore.
  [maurits]

- Fixed portlet_title on creating
  [kroman0]


0.3.4 - 2011-05-17 
------------------
- adapting to changes in Plone 4.1 (thanks to Daniel Marks/Netsight Internet Solutions)

0.3.3 - 2011-05-12 
------------------
- Merging some i18n features [DavidJonas]
- Translations Danish and Czech thanks to Roman Kozlovskiy and Radim Novotny 
 
0.3.2 - 2011-02-15
-------------------
- Bugfix for error: "ParseError: Token 'ATOM' required, 'Not' found" [DavidJonas]

0.3.1 - 2010-03-05 
-------------------

- Fix ImportException -> ImportError [kiorky]
- Fix leadimage checks when you don't have leadimage [kiorky]
- Let the use filter only on subject if he wants [kiorky]
- Let the user configure if he want to use the last items
  where there are no related items found as a fallback [kiorky]
- Let the user choose the portlet title [kiorky]
- Let the user choose to display the content description  [kiorky]

0.3.0 2009-12-30
----------------

- Related items use image tile instead of thumb.

0.2.9 2009-05-27
----------------

- Minor changes regarding the dates of events.

0.2.6 2009-05-07
----------------

- Bug fix.
- Added classes to improve CSS.

0.2.5 2009-05-01
----------------

- Bug fix: hard dependency to contentleadimage removed.

0.2.4 2009-04-30
----------------

- Bug fix: files types like Image and File did not appeared in sea.
- Bug fix: portlet rendered bug in admin pages.
- Bug fix: title of non folder items (with references) was not included in the search.

0.2.3 2009-04-03
----------------

- Bug fix: related items did not appear in some collections.

0.2.2 2009-03-31
----------------

- Manual selected related items are used as a search query (references and backreferences);

0.2.1 2009-03-26
----------------

- Bug fix: related items did not appear in some collections.

0.2 2009-03-25
--------------

- Related items for folderish items (folder, collection, etc)

0.1 2009-03-23
--------------

- Initial package structure.
  [zopeskel]

