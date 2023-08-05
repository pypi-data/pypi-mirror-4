.. contents::

Introduction
============
collective.forgetit removes residue of Products that have been removed.
It will not delete your content objects. Use the ZMI for that.
It will not remove persistent utilities. Use wildcard.fixpersistentutilities for that.
collective.forgetit aims to remove traces in the other locations, one
of them being the catalog from zc.relation, where a removed interface
can create havoc.

While collective.forgetit does not remove your content objects, it removes other information that might have been of value. Be sure that you really don't want to reinstall the package/Product again to reuse your old content!

Currently, collective.forgetit only handles residue in zc.relation catalogs.

