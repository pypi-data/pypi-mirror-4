.. contents::


Documentation
=============


Goal and usage
--------------

Add collective.noindexing to the eggs in your buildout (and to zcml on
Plone 3.2 or earlier).  This makes two browser views available on the
Plone Site root: ``@@collective-noindexing-apply`` and
``@@collective-noindexing-unapply``.  The first applies some patches
and the second undoes the patching.  Both can be called multiple times
safely.

This patches some catalog methods so no indexing, reindexing or
unindexing is done at all.  The idea is that you use this package so
you can quickly move a big part of your Plone Site to a different
folder without having to worry about indexing.  It really makes moving
a lot faster.  You do the indexing later, probably by doing a catalog
clear and rebuild; you have a bit more control there about
subtransactions, to help avoid a ``MemoryError`` or ``[Errno 24] Too
many open files``.  A script to run the catalog clear and rebuild with
some intermediate commits can help here for large sites; see for
example
http://svn.plone.org/svn/plone/Products.PloneOrg/trunk/scripts/catalog_rebuild.py


Notes
-----

- The patches do not apply to ``ATBTreeFolders`` like the standard
  Members, events and news Large Plone Folders from Plone 3.  This is
  not deliberate, so it might change in the future, but for now I do
  not mind.  It works fine for folders in Plone 4.

- It works for Dexterity content too.


Alternatives
------------

- Go to the ``archetype_tool`` object in the ZMI, and then to the
  Catalogs tab.  Switching off ``portal_catalog`` in all the types
  there should have basically the same effect.

- Add ``Products.QueueCatalog`` and ``Products.PloneQueueCatalog`` to
  the eggs of your buildout.  In the ``portal_quickinstaller`` install
  PloneQueueCatalog.  This renames the ``portal_catalog`` to
  ``portal_catalog_real`` and creates a ZCatalog Queue with the id
  ``portal_catalog``.  The standard settings worked fine for me.  You
  now do that large move.  In the fresh ``portal_catalog`` you go to
  the Queue tab.  It should say you have lots of items in the queue,
  in my case around 12,000.  Clicking the 'Process Queue' button will
  by default process just twenty items of that queue.  You can
  increase that number.  This is an easy way of avoiding MemoryErrors
  during indexing, as the total number of objects reindexed in one go
  will be as low as you want.

  Note that I tried this but ran into problems as this website had the
  ``portal_catalog`` in a separate CatalogData.fs, which worked fine
  until I restarted the zeoclient.  With some tinkering it should
  work, but I did not want to bother with that.  We can revisit that
  when indexing becomes a problem all the time instead of just once
  for a clear and rebuild.


Authors
-------

Maurits van Rees
