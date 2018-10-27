import re
import json
import scrapy
import logging
from bs4 import BeautifulSoup
from urllib.parse import (urlencode, urlsplit)
from scrapy.crawler import CrawlerProcess
from maxgetter.items import ProductItem
from maxgetter.pipelines import is_product_exist
# from maxgetter.pipelines import MySqlPipeline

import threading

logger = logging.getLogger(__name__)


class MaxSpider(scrapy.Spider):
    name = 'max'
    # start_urls = ''

    def __init__(self):
        super().__init__()
        # self.is_product_exist = MySqlPipeline.from_crawler(self.crawler).is_product_exist

    def start_requests(self):
        urls = [
            # 'https://cn.?maxmara.com/',
            # 'https://cn.maxmara.com/leather-and-fur-coats/c-103/resultsViaAjax?q=%3AtopRated%3AcollectionActive%3Atrue&sort=topRated&numberOfPage=0&numberOfClothes=16&numberOfClothesPE=16&scrollTop=',
            # 'https://cn.maxmara.com/101801-iconic-coat',
            'https://cn.maxmara.com/p-5446038906003-zucca-tobacco/ajax?'
            ]
        
        for url in urls:
            data = {
                'cata_name': 'tst',
                'cata_page_url': '',
                'product_code': '',
                'product_name': '',
                'product_page_url': ''
                }
            yield scrapy.Request(url, callback=self.parse_cata_ajax_page, meta={'item': data})

    

    def parse(self, response):
        ''' 
        在主页，获取maxmara的产品目录
        '''
        targets = [
            {'type':'Clothing', 'select':'.dropdown.cat-200 .sub-nav-item a'},
            {'type':'Outerwear', 'select':'.dropdown.cat-100 .sub-nav-item a'}]

        soup = BeautifulSoup(response.text, 'lxml')
        for target in targets:
            items = soup.select(target['select'])
            for item in items:
                cata = {
                    'cata_name': item.text.strip('\n'),
                    'cata_page_url': item['href']}
                call_back = self.parse_cata_normal_page

                #如果c开头的类别，就用ajax获取， 其它的就直接从页面获取
                is_ajax_query = re.search(r'/c-\d+?$', cata['cata_page_url'], re.M|re.I)
                if is_ajax_query:
                    post_data =dict(
                        q=':topRated:collectionActive:true',
                        sort='topRated',
                        numberOfPage=0,
                        # categoryCode=202,
                        # numberOfClothes=16,
                        # numberOfClothesPE=16,
                        numberOfClothes=320,
                        numberOfClothesPE=320,
                        scrollTop='')
                    cata['cata_page_url'] = '{}/resultsViaAjax?{}'.format(cata['cata_page_url'], urlencode(post_data))
                    call_back = self.parse_cata_ajax_page
                
                meta = {'item': cata}
                yield response.follow(cata['cata_page_url'], call_back, meta=meta)

    def parse_cata_ajax_page(self, response):
        '''
        在产品类别页面，通过ajax获取产品详细信息
        '''

        content = json.loads(response.text)
        products = content['searchPageData']['results'][0]['productList']
        logger.debug('There are %d products in page %s.', len(products), response.url)
        
        for product in products:
            url = '{}/ajax?'.format(product['url'])
            if not is_product_exist(url):
                data = {
                    'product_code': product['code'],
                    'product_name': product['name'],
                    'product_page_url': url
                    }
                meta = dict(response.meta['item'], **data)
                yield response.follow(url, self.parse_product, meta={'item': meta})
        

        total_page = int(content['totalPage'])
        logger.debug('There are total %d pages in page %s.', total_page, response.url)
        patten = re.compile(r'numberOfPage=(\d+?)&')
        next_page = int(patten.search(response.url).group(1)) + 1
        if next_page < total_page:
            url = patten.sub('numberOfPage={}&'.format(next_page), response.url)
            yield response.follow(url, self.parse_cata_ajax_page, meta={'item': response.meta['item']})

    def parse_cata_normal_page(self, response):
        '''
        在产品类别页面，解析页面的方式获取产品详细信息
        '''
        #从页面判断是否Gallery方式展示页面
        is_product_gallery = re.search(r'isProductGallery = true', response.text, re.M|re.I)
        patten = None
        if is_product_gallery:
            patten = re.compile(r'<li class="span3 item_thumb">\s+?<a href="(.+?)".+?</li>', re.I|re.M|re.S)          
        else:
            patten = re.compile(r'<a href="(/p-.+?)".+?a>', re.I|re.M|re.S)
        
        products = patten.findall(response.text)
        for product in products:
            url = '{}/ajax?'.format(product)
            if not is_product_exist(url):
                data = {
                    'product_code': '',
                    'product_name': '',
                    'product_page_url': url
                    }
                meta = dict(response.meta['item'], **data)
                yield response.follow(url, self.parse_product, meta={'item': meta})


    def parse_product(self, response):
        '''
        在产品页面，获取高清大图的地址
        '''
        #initialize the item
        p = ProductItem(response.meta['item'])
        p['product_zoom_image_urls'] = []

        #get all zoomed images
        images = json.loads(response.text)['images']
        zoom_images = []
        for image in images:
            if image['format'] == 'zoom':
                zoom_images.append(image['url'])
        p['product_zoom_image_urls'].extend(zoom_images)
        p['product_zoom_images'] = ''

        yield p