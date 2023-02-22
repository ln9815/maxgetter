import logging
import os
from datetime import datetime

from getmax.config import settings, get_instance_path
from getmax.db import MaxDB, MaxRoot, Session, select
from getmax.page_parser import PageParser

logger = logging.getLogger(__name__)

class MaxDownloader(object):
    def __init__(self) -> None:
        pass

    @property
    def uri(self):
        uri = ''
        if str(settings.DATABASE_TPYE).lower() == 'mysql':
            uri = f'mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}'
        else:
            fn = os.path.join(get_instance_path(), settings.SQLITE_DB)
            uri = f'sqlite:///{fn}'
        return uri

    @property
    def db(self):
        return MaxDB(self.uri)

    def init(self):
        self.db.init_db()
        self.db.init_data()


    def retrieve_product_image_info(self):
        '''
        根据数据库配置ROOT信息,获取所有产品及图片位置。
        并将产品及图片信息更新到数据库。
        '''
        db = self.db
        parser = PageParser()

        session = Session(db.engine)
        stmt = select(MaxRoot)

        # get all products first.
        product_list = []
        for root in session.scalars(stmt):
            products = parser.parse_all_category_page(root.href)
            for product in products:
                product['rootid'] = root.id
            product_list.extend(products)
        logger.info(" total %d product founded on websit.", len(product_list))

        catagory_list = []
        for product in product_list:
            ids = [x["id"] for x in catagory_list]
            if product["categoryid"] not in ids:
                catagory_list.append(
                    {'id': product['categoryid'], 'name': product['name'], 'season': product['season'], 'rootid': product['rootid']})
        db.add_categroies(catagory_list)
        logger.info(" %d categories updated on database.", len(catagory_list))

        untouched_products = db.get_untouched_products(product_list)
        logger.info(" %d of %d products untouched.", len(
            untouched_products), len(product_list))

        for index, product in enumerate(untouched_products):
            if settings.ENV != 'pro' and index >= 5:
                break
            db.add_product(product)
            images = parser.parse_detail_page(product["href"])
            db.add_product_images(product, images)
            logger.info('%d / %d product: %s, %d images added.', index + 1,
                        len(untouched_products), product["href"], len(images))

    def download_pending_images(self,folder=None):
        db = self.db
        parser = PageParser()
        images = db.get_pending_images()

        if folder is None:
            folder = os.path.join(get_instance_path(), 'maxmara')

        for index, img in enumerate(images):
            if settings.ENV != 'pro' and index >= 5:
                break
            folder_save = os.path.join(folder, img.name, datetime.now().strftime("%Y-%m"))
            if not os.path.exists(folder_save):
                os.makedirs(folder_save)
            fn = os.path.join(folder_save, img.filename)
            if not os.path.exists(fn):
                parser.download_image(img.href, fn)
            db.image_set_downloaded(img.product_id, img.href)
            logger.info(' %d / %d image saved: %s', index+1, len(images), fn)
