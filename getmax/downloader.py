import json
import logging
import os
from datetime import datetime
from asyncio.log import logger

from getmax.config import Config
from getmax.db import Category, Image, MaxDB, MaxRoot, Product, Session, select
from getmax.page_parser import PageParser
from getmax.setting import get_setting

logger = logging.getLogger(__name__)


class MaxDownloader(object):
    default_config = dict(MAX_HOST="https://world.maxmara.com",
                          SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
                          )

    def __init__(self, env="development") -> None:
        self.root_path = os.path.abspath(os.path.dirname(__file__))
        self.instance_path = os.path.join(
            os.path.dirname(self.root_path), "instance")
        logger.info(
            f'env: {env}, root path: {self.root_path}, instance path: {self.instance_path}')

        if not os.path.exists(self.instance_path):
            try:
                os.makedirs(self.instance_path)
            except:
                pass

        self.config = Config(self.root_path, self.default_config)
        self.make_config(env)
        logger.info(f'app configuration:\n{json.dumps(self.config, indent=2)}')

    def make_config(self, env):
        obj = get_setting(env)
        if obj:
            self.config.from_object(obj)

        if 'SQLITE_DB' in self.config.keys():
            fn = os.path.join(self.instance_path, self.config['SQLITE_DB'])
            self.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{fn}'
        self.config['ENV'] = env

    def init(self):
        db = MaxDB(self.config["SQLALCHEMY_DATABASE_URI"])
        db.init_db()
        db.init_data()

    def retrieve_product_image_info(self):
        '''
        根据数据库配置ROOT信息,获取所有产品及图片位置。
        并将产品及图片信息更新到数据库。
        '''
        db = MaxDB(self.config["SQLALCHEMY_DATABASE_URI"])
        parser = PageParser(self.config["MAX_HOST"])

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
            db.add_product(product)
            images = parser.parse_detail_page(product["href"])
            db.add_product_images(product, images)
            logger.info('%d / %d product: %s, %d images added.', index + 1,
                        len(untouched_products), product["href"], len(images))

    def download_pending_images(self):
        db = MaxDB(self.config["SQLALCHEMY_DATABASE_URI"])
        parser = PageParser(self.config["MAX_HOST"])
        images = db.get_pending_images()

        for index, img in enumerate(images):
            folder_save = os.path.join(
                self.config['FOLDER_SAVE'], img.name, datetime.now().strftime("%Y-%m"))
            if not os.path.exists(folder_save):
                os.makedirs(folder_save)
            fn = os.path.join(folder_save, img.filename)
            if not os.path.exists(fn):
                parser.download_image(img.href, fn)
            db.image_set_downloaded(img.product_id, img.href)
            logger.info(' %d / %d image saved: %s', index+1, len(images), fn)
