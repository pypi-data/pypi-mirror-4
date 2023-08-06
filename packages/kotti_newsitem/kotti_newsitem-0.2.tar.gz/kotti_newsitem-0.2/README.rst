==============
kotti_newsitem
==============

|build status production|

News Item content type for Kotti.

This package provides:

-   a ``NewsItem`` content type that is just a Document with a different
    default view,

-   a ``news_listing`` view that provides an alternative default view for
    Document, for listing most recent published ``NewsItems`` on a full-page
    style display,

-   a ``RecentNews`` widget for showing most recent published ``NewsItems``
    in a slot, and

-   an ``all_news`` view that shows ALL ``News Items`` in your site,
    chronologically ordered.

`Find out more about Kotti`_

Setup
=====

To activate the ``kotti_newsitem`` add-on in your Kotti site, you need to add
an entry to the ``kotti.configurators`` setting in your Paste Deploy config.
If you don't have a ``kotti.configurators`` option, add one.  The line in your
``[app:main]`` (or ``[app:kotti]``, depending on how you setup Fanstatic)
section could then look like this::

    kotti.configurators = kotti_newsitem.kotti_configure

Configuration
=============

A good approach for managing news items on your site is to make a private
container document for holding the actual news items. It is a good idea to
organize them somehow, as by year::

    news-items
        2013
            news-item-foo
            news-item-bar
            ...
        2014
            ...

This is primarily to help the content creator organize content, but it could
also be used as a "manual" way of presenting news items if published.  Display
of most recent news items can be done either by selecting ``News Listing`` for
the default view of a Document, or by using the recent news widget in a slot.

News Listing
------------

For a full-page listing of most recent news items, add a Document, usually at
the top-level of your site and titled "News", and set its default view to
``News Listing``.  Control the number of recent items shown with::

    kotti_newsitem.num_news = 10

At the bottom of the list of news items, regardless of the number of recent
news items listed, is a link to a page for ``All News``, where all news items
are shown.

Recent News Widget
------------------

If you want the ``RecentNews`` widget to show up in your site in a slot, either
in place of a dedicated full-page news listing or to augment it, you have to
add a line like this to enable the recent news widget::

    kotti_newsitem.widget.slot = right

The for a list of available slots in a default Kotti site see the
`kotti.view.slots API docs`_

To change the default number of recent news items shown in the widget (5), add
a line like this::

    kotti_newsitem.widget.num_news = 10

.. Note:: kotti_newsitem.num_news controls the number of items shown in a
          news listing; kotti_newsitem.widget.num_news does the same for the
          widget. For example, you might have the news listing set to show 10,
          but the widget only 2.

Development
===========

|build status master|

Contributions to ``kotti_newsitem`` are highly welcome. Just clone its Github
repository and submit your contributions as pull requests.


.. |build status production| image:: https://travis-ci.org/Kotti/kotti_newsitem.png?branch=production
.. |build status master| image:: https://travis-ci.org/Kotti/kotti_newsitem.png?branch=master
.. _Find out more about Kotti: http://pypi.python.org/pypi/Kotti
.. _kotti.view.slots API docs: http://kotti.readthedocs.org/en/latest/_modules/kotti/views/slots.html#assign_slot
