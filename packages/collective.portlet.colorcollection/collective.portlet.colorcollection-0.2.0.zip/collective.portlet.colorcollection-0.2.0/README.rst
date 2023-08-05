Introduction
============

Change the renderer of your Plone collection portlet, trying to force a link color
using a ``style="color: ..."`` attribute.

How to use
==========

This product is for *developers*. It only add a catalog column (*color*) and change
the basic Collection Plone renderer to check for this color.

Installing this won't add any real new colors in collection portlets (and we don't want
... normally color must came from site UI theme, not contents).

How support colors
------------------

You can:

Support for a ``color`` property
    Add to your content types a new ``color`` method or property.
Support for a ``color`` @indexer
    Add an indexer that return the color you want:
    
    >>> from plone.indexer.decorator import indexer
    >>> @indexer(IMyType)
    >>>     def color(object, **kw):
    ...     return 'red'

    See `Custom indexing strategies`__ on Plone documentation section.

__ http://plone.org/documentation/manual/developer-manual/indexing-and-searching/custom-indexing-strategies

The color format must be CSS valid. So: 'red', '#FF0000', '#F00' or 'rgb(255,0,0)' are
all good values.

Credits
=======

Developed with the support of `S. Anna Hospital, Ferrara`__; S. Anna Hospital supports the
`PloneGov initiative`__.

.. image:: http://www.ospfe.it/ospfe-logo.jpg
   :alt: OspFE logo

__ http://www.ospfe.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/

