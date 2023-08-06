# -*- coding: utf-8 -*-

"""
Created on 2013-02-07
:author: Andreas Kaiser (disko)
"""

from pyramid.i18n import TranslationStringFactory

from kotti.views.slots import assign_slot

_ = TranslationStringFactory('kotti_newsitem')


def kotti_configure(settings):

    settings['pyramid.includes'] += ' kotti_newsitem'
    settings['kotti.available_types'] += ' kotti_newsitem.resources.NewsItem'

    if 'kotti_newsitem.widget.num_news' in settings:
        settings['kotti_newsitem.widget.num_news'] = int(
            settings['kotti_newsitem.widget.num_news'])
    else:
        settings['kotti_newsitem.widget.num_news'] = 5

    if 'kotti_newsitem.widget.slot' in settings:
        assign_slot('recent_news', settings['kotti_newsitem.widget.slot'])


def includeme(config):

    config.add_translation_dirs('kotti_newsitem:locale')
    config.scan(__name__)
