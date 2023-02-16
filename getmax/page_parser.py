import logging
import math
import os
import re

from requests import Session
from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)


class PageParser(object):
    def __init__(self, host="https://world.maxmara.com") -> None:
        self._session = Session()
        self._session.mount('http://', HTTPAdapter(max_retries=5))
        self._session.mount('https://', HTTPAdapter(max_retries=5))
        self._host = host
        logger.info(f'Maxmara host: {self._host}.')

    def request(self, **kwargs):
        assert 'method' in kwargs.keys()
        assert 'url' in kwargs.keys()

        # logger.debug(f'request kwargs initial: {kwargs}')
        headers = kwargs['headers'] if 'headers' in kwargs.keys() else {}
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74'
        timeout = kwargs['timeout'] if 'timeout' in kwargs.keys() else (5, 10)
        kwargs['headers'] = headers
        kwargs['timeout'] = timeout
        # logger.debug(f'request kwargs updated: {kwargs}')

        return self._session.request(**kwargs)

    def max_url(self, url):
        return f'{self._host}{url}' if url.find("maxmara.com") < 1 else url

    def parse_single_category_page(self, url, page=1, pages=None):
        response = self.request(method="GET", url=self.max_url(url))
        if response is None:
            return [], 0

        # get product info
        product_list = []
        regex = f'data-product-id="(.*?)".*title="(.*?)".*href="(/p.+?)".*data-season="(.*?)".*data-categoryid="(.*?)".*data-category="(.*?)"'
        patten = re.compile(regex, re.I | re.M)
        products = [dict(zip(["id", "title", "href", "season", "categoryid", "name"], item))
                    for item in patten.findall(response.text)]

        # get total page numbers
        searchObj = re.search(r'View all (.+?)\n', response.text, re.M | re.I)
        total_numbers = int(searchObj.group(
            1)) if searchObj is not None else len(products)
        total_pages = math.ceil(total_numbers/len(products))
        total_pages = total_pages if pages is None else pages

        logger.info('  %d products in page: %d/%d. url: %s',
                    len(products), page, total_pages, url)

        return products, total_pages

    def parse_all_category_page(self, url):
        products, total_pages = self.parse_single_category_page(url)

        if total_pages > 1:
            for page in range(2, total_pages+1):
                url_page = '{}?focus=true&page={}&partial=true&q=%3AtopRated&resetQuery=true&save=false&sort=topRated'.format(
                    url, page)
                new_products, _ = self.parse_single_category_page(
                    url_page, page, total_pages)
                products.extend(new_products)

        logger.info(" Total %d products founded on %s.", len(products), url)
        return products

    def parse_detail_page(self, url):
        def _filename(href):
            searchObj = re.search(r's3.*?/(.*?.jpg)$', href, re.M | re.I)
            return searchObj.group(1) if searchObj is not None else 'unkonw.jpg'

        response = self.request(method="GET", url=self.max_url(url))
        if response is None:
            return []

        patten = re.compile(r'data-lazy="(.*?)#zoom"', re.I | re.M | re.S)
        images = patten.findall(response.text)
        logger.debug("%d images in url %s", len(images), url)

        result = []
        for img in images:
            result.append({"href": img, "filename": _filename(img)})

        return result

    def download_image(self, url, file_name):
        path_save = os.path.dirname(file_name)
        if not os.path.exists(path_save):
            os.makedirs(path_save)

        response = self.request(method="GET", url=url, timeout=120)
        if response is None:
            return
        with open(file_name, 'wb') as f:
            f.write(response.content)
        logger.info(f'image: {url} was downloaded, saved on {path_save}.')
