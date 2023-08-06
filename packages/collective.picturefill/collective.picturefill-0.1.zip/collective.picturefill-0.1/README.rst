Introduction
============

This addon install picturefill_ in Plone and provide a suite of tools to
display images from different kind of components such as brain, dexterity object
or archetypes object.

How to install
==============

This addon can be installed has any other addons. please follow official
documentation_

How to use
==========

in template::

    tal:content="structure myimage_object/@@polyfill"

in python::

    from collective.picturefill.interfaces import IPictureFill
    IPictureFill(brain)()

Credits
=======

Companies
---------

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact Makina Corpus <mailto:python@makina-corpus.org>`_

People
------

- JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>

.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to
.. _picturefill: https://github.com/scottjehl/picturefill
