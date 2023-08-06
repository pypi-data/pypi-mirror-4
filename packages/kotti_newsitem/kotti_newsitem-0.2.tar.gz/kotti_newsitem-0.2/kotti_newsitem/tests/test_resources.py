from kotti.resources import get_root
from kotti.testing import DummyRequest

from kotti_newsitem.resources import NewsItem


def test_newsitem(db_session, config):
    config.include('kotti_newsitem')

    root = get_root()
    content = NewsItem()
    assert content.type_info.addable(root, DummyRequest()) is True
    root['content'] = content
