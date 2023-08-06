# -*- coding: utf-8 -*-

from datetime import date

from colander import SchemaNode
from colander import Date
from kotti.resources import Content
from kotti.security import has_permission
from kotti.views.edit.content import DocumentSchema
from kotti.views.form import AddFormView
from kotti.views.form import EditFormView
from pyramid.view import view_config
from pyramid.view import view_defaults
from sqlalchemy import desc

from kotti_newsitem import _
from kotti_newsitem.fanstatic import css
from kotti_newsitem.resources import NewsItem


class NewsItemSchema(DocumentSchema):
    """Schema for add / edit forms of NewsItem"""

    publish_date = SchemaNode(
        Date(),
        title=_(u'Publish date'),
        missing=date.today(),
    )


@view_config(name=NewsItem.type_info.add_view,
             permission='add',
             renderer='kotti:templates/edit/node.pt')
class NewsItemAddForm(AddFormView):
    """ Add form for NewsItem. """

    schema_factory = NewsItemSchema
    add = NewsItem
    item_type = _(u"NewsItem")


@view_config(name='edit',
             context=NewsItem,
             permission='edit',
             renderer='kotti:templates/edit/node.pt')
class NewsItemEditForm(EditFormView):
    """ Edit form for NewsItem. """

    schema_factory = NewsItemSchema


class BaseView(object):
    """ BaseView provides a common constructor method. """

    def __init__(self, context, request):
        """ Constructor.  Sets context and request as instance attributes.

        :param context: context.
        :type context: kotti.resources.Content or subclass thereof.

        :param request: request.
        :type request: pyramid.request.Request
        """

        self.context = context
        self.request = request

        css.need()


@view_defaults(context=NewsItem, permission='view')
class NewsItemView(BaseView):
    """ View for NewsItem. """

    @view_config(name='view',
                 renderer='kotti_newsitem:templates/news_item.pt')
    def view(self):

        return {}


@view_defaults(context=Content, permission='view')
class NewsItemListViews(BaseView):
    """ List views for multiple NewsItems.

        For now NewsItems are gathered from the whole site.  Later that might be
        restricted to searching only below the current context.
    """

    def news_items(self, num=None):
        """ Query the site for NewsItems and return them ordered by
            publish_date.

        :param num: Maximum number of NewsItems to return.  The default of
                    ``None`` means return all NewsItems.
        :type num: int or None

        :result: Sequence of NewsItems.
        :rtype: list
        """

        q = NewsItem.query \
            .filter(NewsItem.publish_date <= date.today())\
            .order_by(desc(NewsItem.publish_date))

        items = []

        for item in q.all():
            if has_permission('view', item, self.request):
                items.append(item)
                if num is not None and len(items) == num:
                    return items

        return items

    @view_config(name='recent_news',
                 renderer='kotti_newsitem:templates/recent_news.pt')
    def recent_news(self):

        settings = self.request.registry.settings
        items = self.news_items(settings['kotti_newsitem.widget.num_news'])

        return {'items': items}

    @view_config(name='all_news',
                 renderer='kotti_newsitem:templates/all_news.pt')
    def all_news(self):

        items = self.news_items()

        return {'items': items}
