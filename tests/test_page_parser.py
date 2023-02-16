import pytest
import logging

from getmax.page_parser import PageParser

logger = logging.getLogger(__name__)

@pytest.fixture
def parser(app):
    p = PageParser(app.config["MAX_HOST"])
    return p 

def test_parse_single_category_page(parser):
    urls = ('/clothing/skirts','/clothing/womens-dresses?focus=true&page=2&partial=true&q=%3AtopRated&resetQuery=true&save=false&sort=topRated')
    for url in urls:
        products, total_pages =parser.parse_single_category_page(url)
        assert len(products) > 0
        assert total_pages > 0

def test_parse_all_category_page(parser):
    url = '/clothing/skirts'
    products = parser.parse_all_category_page(url)
    assert len(products) > 0

def test_parse_detail_page(parser):
    url = '/p-2226112306003-papilla-black'
    images = parser.parse_detail_page(url)
    assert len(images) > 0

