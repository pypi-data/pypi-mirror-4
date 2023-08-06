Changelog
=========

0.9 - 2013-03-02
----------------

- Modernized `z2_kgs` code and updated it to work with Github.

- Modernized `ztk_kgs` code and skip the `zopeapp-versions` file for ZTK 2+.

0.8 - 2010-09-09
----------------

- Do not override existing version pins defined in the ``versions.cfg`` by
  versions from the extends lines. This refs
  https://bugs.launchpad.net/zope2/+bug/623428.

0.7 - 2010-07-13
----------------

- Added support for having an ``extends`` line pointing to another version
  file and still creating a full index.

0.6 - 2010-07-13
----------------

- Support packages with underscores in their name.

0.5 - 2010-06-30
----------------

- Disable the index building for a ZTK release.

0.4 - 2010-06-26
----------------

- Added support for creating a Zope Toolkit index.

- Update ``package_urls`` to ``release_urls`` as specified in
  http://wiki.python.org/moin/PyPiXmlRpc.

0.3 - 2010-06-13
----------------

- Added support for inline comments in the versions section.

- Readme style fixes.

0.2 - 2010-04-05
----------------

* Avoid hardcoded upper_names list.

0.1.5 - 2009-12-25
------------------

* sanity check for download_url

* better parameter check

0.1.4 - 2009-08-06
------------------

* better parameter check

0.1.3 - 2009-04-25
------------------

* generate a versions.cfg file within the index directory

0.1.2 - 2009-04-25
------------------

* removed hard-coded Zope 2 version

0.1.1 - 2009-04-25
------------------

* bahhh...fixed broken package

0.1.0 - 2009-04-24
------------------

* Initial release
