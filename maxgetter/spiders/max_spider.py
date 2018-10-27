import re
import json
import scrapy
from bs4 import BeautifulSoup
from urllib.parse import (urlencode, urlsplit)
from scrapy.crawler import CrawlerProcess
from maxgetter.items import ProductItem
from maxgetter.pipelines import is_product_exist
import threading

lock = threading.Lock()
products_crawled = 0
products_limited = 2


class MaxSpider(scrapy.Spider):
    name = 'max'
    start_urls = ['https://cn.maxmara.com/']
    

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
                        numberOfClothes=16,
                        numberOfClothesPE=16,
                        scrollTop='')
                    cata['cata_page_url'] = '{}/resultsViaAjax?{}'.format(cata['cata_page_url'], urlencode(post_data))
                    call_back = self.parse_cata_ajax_page
                
                meta = {'item': cata}
                yield response.follow(cata['cata_page_url'], call_back, meta=meta)

    def parse_cata_ajax_page(self, response):
        '''
        在产品类别页面，通过ajax获取产品详细信息
        '''

        p = {
            'cata_name': response.meta['item']['cata_name'],
            'cata_page_url': response.meta['item']['cata_page_url'],
            'product_code': '',
            'product_name': '',
            'product_page_url': ''}
        
        data_json = json.loads(response.text)
        for product in data_json['searchPageData']['results'][0]['productList']:
            # product_keys = ("code","name","url")
            p['product_code'] = product['code']
            p['product_name'] = product['name']
            p['product_page_url'] = '{}/ajax?'.format(product['url'])
            meta = {'item': p}
            url = p['product_page_url']
            # url = response.urljoin(p['product_page_url'])
            if not is_product_exist(url):
                yield response.follow(url, self.parse_product, meta=meta)
        

        total_page = int(data_json['totalPage'])
        patten = re.compile(r'numberOfPage=(\d+?)&')
        next_page = int(patten.search(response.url).group(1)) + 1
        if next_page < total_page:
            url = patten.sub('numberOfPage={}&'.format(next_page), response.url)
            cata = {
                'cata_name': response.meta['item']['cata_name'],
                'cata_page_url': response.meta['item']['cata_page_url']
                }
            meta = {'item': cata}
            yield response.follow(url, self.parse_cata_ajax_page, meta=meta)

        return None

    def parse_cata_normal_page(self, response):
        '''
        在产品类别页面，解析页面的方式获取产品详细信息
        '''
        p = {
            'cata_name': response.meta['item']['cata_name'],
            'cata_page_url': response.meta['item']['cata_page_url'],
            'product_code': '',
            'product_name': '',
            'product_page_url': ''}

        #从页面判断是否Gallery方式展示页面
        is_product_gallery = re.search(r'isProductGallery = true', response.text, re.M|re.I)
        patten = None
        if is_product_gallery:
            patten = re.compile(r'<li class="span3 item_thumb">\s+?<a href="(.+?)".+?</li>', re.I|re.M|re.S)          
        else:
            patten = re.compile(r'<a href="(/p-.+?)".+?a>', re.I|re.M|re.S)
        
        products = patten.findall(response.text)
        for product in products:
            p['product_page_url'] = '{}/ajax?'.format(product)
            url = response.urljoin(p['product_page_url'])
            meta = {'item': p}
            if not is_product_exist(url):
                yield response.follow(p['product_page_url'], self.parse_product, meta=meta)
        
        return None

    def pre_parse_product(self, url, meta):
        if not is_product_exist(url):
            yield scrapy.Request(url, self.parse_product, meta=meta)
        return None

    def parse_product(self, response):
        '''
        在产品页面，获取高清大图的地址
        '''
        #initialize the item
        p = ProductItem()
        p['cata_name'] = response.meta['item']['cata_name']
        p['cata_page_url'] = response.meta['item']['cata_page_url']
        p['product_code'] = response.meta['item']['product_code']
        p['product_name'] = response.meta['item']['product_name']
        p['product_page_url'] = response.meta['item']['product_page_url']
        p['product_zoom_image_urls'] = []

        #get all zoomed images
        images = json.loads(response.text)['images']
        zoom_images = []
        for image in images:
            if image['format'] == 'zoom':
                zoom_images.append(image['url'])
        p['product_zoom_image_urls'].extend(zoom_images)

        yield p