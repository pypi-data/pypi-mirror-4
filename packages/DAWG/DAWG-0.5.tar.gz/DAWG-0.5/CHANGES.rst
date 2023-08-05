
0.5 (2012-10-08)
----------------

The storage scheme of ``BytesDAWG`` and ``RecordDAWG`` is changed in
this release in order to provide the alphabetical ordering of items.

This is a backwards-incompatible release. In order to read ``BytesDAWG`` or
``RecordDAWG`` created with previous versions of DAWG use ``payload_separator``
constructor argument::

    >>> BytesDAWG(payload_separator=b'\xff').load('old.dawg')


0.4.1 (2012-10-01)
------------------

- Segfaults with empty DAWGs are fixed by updating dawgdic to latest svn.

0.4 (2012-09-26)
----------------

- ``iterkeys``, ``iteritems`` and ``iterprefixes`` methods
  (thanks Dan Blanchard).

0.3.2 (2012-09-24)
------------------

- ``prefixes`` method for finding all prefixes of a given key.

0.3.1 (2012-09-20)
------------------

- bundled dawgdic C++ library is updated to the latest version.

0.3 (2012-09-13)
----------------

- ``similar_keys``, ``similar_items`` and ``similar_item_values`` methods
  for more permissive lookups (they may be useful e.g. for umlaut handling);
- ``load`` method returns self;
- Python 3.3 support.

0.2 (2012-09-08)
----------------

Greatly improved memory usage for DAWGs loaded with ``load`` method.

There is currently a bug somewhere in a wrapper so DAWGs loaded with
``read()`` method or unpickled DAWGs uses 3x-4x memory compared to DAWGs
loaded with ``load()`` method. ``load()`` is fixed in this release but
other methods are not.

0.1 (2012-09-08)
----------------

Initial release.