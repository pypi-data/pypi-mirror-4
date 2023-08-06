from pyramid.interfaces import ITranslationDirectories

from kotti_newsitem import includeme
from kotti_newsitem import kotti_configure


def test_kotti_configure():

    settings = {
        'kotti.available_types': '',
        'pyramid.includes': '',
    }

    kotti_configure(settings)

    assert settings['pyramid.includes'] == ' kotti_newsitem'
    assert settings['kotti.available_types'] == ' kotti_newsitem.resources.NewsItem'

    assert 'kotti_newsitem.widget.slot' not in settings
    assert settings['kotti_newsitem.widget.num_news'] == 5

    settings['kotti_newsitem.num_news'] = "3"
    kotti_configure(settings)
    assert settings['kotti_newsitem.num_news'] == 3

    settings['kotti_newsitem.widget.num_news'] = "3"
    kotti_configure(settings)
    assert settings['kotti_newsitem.widget.num_news'] == 3

    settings['kotti_newsitem.widget.slot'] = "right"
    kotti_configure(settings)

    from kotti.events import objectevent_listeners
    from kotti.views.slots import RenderRightSlot

    oel = objectevent_listeners
    assert len(oel[(RenderRightSlot, None)]) == 1


def test_includeme(config):

    includeme(config)

    utils = config.registry.__dict__['_utility_registrations']
    k = (ITranslationDirectories, u'')

    # test if the translation dir is registered
    assert k in utils
    assert utils[k][0][0].find('kotti_newsitem/locale') > 0
