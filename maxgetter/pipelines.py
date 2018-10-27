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

logger = logging.getLogger(__name__)


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
        export_to_sqlite(row, self.conn, self.table)

        # sql = '''
        # INSERT INTO product_saved (
        #                       cata_name,
        #                       cata_page_url,
        #                       product_code,
        #                       product_name,
        #                       product_page_url,
        #                       product_zoom_image_urls,
        #                       product_zoom_images
        #                   )
        #                   VALUES (?,?,?,?,?,?,?)
        # '''
        # c = self.conn.cursor()
        # c.execute(sql, (item['cata_name'],
        #                         item['cata_page_url'],
        #                         item['product_code'],
        #                         item['product_name'],
        #                         item['product_page_url'],
        #                         str(item['product_zoom_image_urls']),
        #                         ''))
        # self.conn.commit()
        return item
    
def is_product_exist(product_page_url):
    '''
    判断这个产品是否已经存在
    '''
    db = '/Users/victor/Documents/GitHub/MaxGetter/product_saved.db'
    sql = 'SELECT * FROM product_saved WHERE product_page_url = ?'
    row = import_from_sqlite(db, query=sql, query_args=(product_page_url,))
    product_list = export_to_dicts(row)

    return len(product_list) > 0


    