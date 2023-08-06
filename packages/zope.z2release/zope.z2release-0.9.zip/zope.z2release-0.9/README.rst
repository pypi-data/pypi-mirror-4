Introduction
============

``zope.z2releases`` is used to generated a PyPI compatible index with
references to all pinned package versions based on a ``versions.cfg``.

It can handle both a Zope 2 release as well as a Zope Toolkit release.

Usage
=====

To generate an index, use::

    z2_kgs tags/2.12.1 /srv/Zope2/index/2.12.1

    ztk_kgs tags/1.0a1 /srv/zopetoolkit/index/1.0a1
