==============
kotti_newsitem
==============

News Item content type for Kotti.

This package provides:

-   a ``NewsItem`` content type that is just a Document with a different default
    view,

-   a ``RecentNews`` widget (that can be assigned to a slot) showing (by
    default) the 5 most recent, published ``NewsItems`` and

-   a ``all_news`` view that shows all ``News Items`` in your site,
    chronologically ordered.

`Find out more about Kotti`_

Setup
=====

To activate the ``kotti_newsitem`` add-on in your Kotti site, you need to
add an entry to the ``kotti.configurators`` setting in your Paste
Deploy config.  If you don't have a ``kotti.configurators`` option,
add one.  The line in your ``[app:main]`` (or ``[app:kotti]``, depending on how
you setup Fanstatic) section could then look like this::

    kotti.configurators = kotti_newsitem.kotti_configure

Configuration
=============

If you want the ``RecentNews`` widget to show up in your site, you have to add
a line like this::

    kotti_newsitem.widget.slot = right

The for a list of available slots in a default Kotti site see the
`kotti.view.slots API docs`_

To change the default number of news items shown in the widget (5), add a line
like this::

    kotti_newsitem.widget.num_news = 10

.. _Find out more about Kotti: http://pypi.python.org/pypi/Kotti
.. _kotti.view.slots API docs: http://kotti.readthedocs.org/en/latest/_modules/kotti/views/slots.html#assign_slot
