# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import sqlite3
import rows
from rows.plugins.sqlite import export_to_sqlite
from rows.plugins.sqlite import import_from_sqlite
from rows import import_from_dicts
from rows import export_to_dicts
import logging
import datetime
import pymysql
import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from scrapy.pipelines.media import MediaPipeline


logger = logging.getLogger(__name__)

def insert_item_to_db(item):
    '''
    将产品记录插入到数据库
    '''
    logger.debug('start to insert item: %s', str(item))

    sql = '''
    INSERT INTO product_saved (
                            cata_name,
                            cata_page_url,
                            product_code,
                            product_name,
                            product_page_url,
                            product_zoom_image_urls,
                            product_zoom_images
                        )
                        VALUES ("{}","{}","{}","{}","{}","{}","{}")
    '''.format(item['cata_name'],
                item['cata_page_url'],
                item['product_code'],
                item['product_name'],
                item['product_page_url'],
                str(item['product_zoom_image_urls']),
                str(item['product_zoom_images'])
                )
    conn = pymysql.connect('localhost', 'root', 'a12345678', 'products')
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()

    logger.debug('success to insert item: %s', str(item))

    return item

def is_product_exist(product_page_url):
    '''
    判断这个产品在数据库中是否已存在
    '''
    logger.debug('start to check to product_page_url: %s', product_page_url)

    sql = 'SELECT * FROM product_saved WHERE product_page_url = "{}"'.format(product_page_url)
    
    conn = pymysql.connect('localhost', 'root', 'a12345678', 'products')
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    conn.close()

    logger.debug('There are %d same pages in database.', len(data))

    return len(data) > 0

class MaxgetterPipeline(object):

    def __init__(self, file):
        self.file = file

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            file=crawler.settings.get('FILE_PRODUCT_SAVED')
        )

    def open_spider(self, spider):
        self.file = open(self.file, 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


class SqlitePipeline(object):

    collection_name = 'scrapy_items'

    def __init__(self, sqlite_db, table_name):
        self.sqlite_db = sqlite_db
        self.table = table_name
        self.conn = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            sqlite_db=crawler.settings.get('SQLITE_DATABASE'),
            table_name=crawler.settings.get('SQLITE_TABLE_NAME')
        )
        

    def open_spider(self, spider):
        self.conn = sqlite3.connect(self.sqlite_db)

    def close_spider(self, spider):
        if self.conn:
            self.conn.close()

    def process_item(self, item, spider):
        row = import_from_dicts([dict(item)])
        logger.debug(row)
        export_to_sqlite(row, self.conn, self.table)
        return item

    def is_product_exist(self, product_page_url):
        '''
        判断这个产品是否已经存在
        '''
        db = self.sqlite_db
        sql = 'SELECT * FROM product_saved WHERE product_page_url = ?'
        row = import_from_sqlite(db, query=sql, query_args=(product_page_url,))
        product_list = export_to_dicts(row)

        return len(product_list) > 0

    
class MySqlPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for image_url in item[self.images_urls_field]:
            logger.debug('start to request image: %s', image_url)
            yield scrapy.Request(image_url, meta={'item': item})

    def item_completed(self, results, item, info):
        logger.debug('item completed: %s', str(item))
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item[self.images_result_field] = image_paths
        insert_item_to_db(item)
        logger.debug('item was inserted to database: %s', str(item))
        return item

    def file_path(self, request, response=None,  。info=None):
        logger.debug('start to get file path.')
        item = request.meta['item']
        logger.debug('item cata name is %s',item['cata_name'])
        file_name = request.url.split('/')[-1]
        logger.debug('file name is %s', file_name)
        import datetime
        today = datetime.datetime.now().strftime("%Y-%m-%≥      # image_guid = hashlib.sha1(to_bytes(url)).hexdigest()  # change to request.url after deprecation
        path = '%s/%s/%s' % (item['cata_name'],today, file_name)    
        logger.debug('file path: %s', path)
        return path
