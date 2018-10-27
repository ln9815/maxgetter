# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ProductItem(scrapy.Item):
    cata_name = scrapy.Field()
    cata_page_url = scrapy.Field()
    product_code = scrapy.Field()
    product_name = scrapy.Field()
    product_page_url = scrapy.Field()
    product_zoom_image_urls = scrapy.Field()
    product_zoom_images = scrapy.Field()
