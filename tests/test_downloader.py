
from turtle import Turtle
import pytest
import logging
import os
import tempfile

from sqlalchemy import text
logger = logging.getLogger(__name__)


def test_retrieve_product_image_info(app, db):

    with db.engine.connect() as conn:
        conn.execute(text("INSERT into maxroot(name, href) VALUES (:name, :href)"),
                     [{"id": 1, "name": "Dresses", "href": "/clothing/womens-dresses"},])
        conn.commit()
        app.retrieve_product_image_info()
        
        rows = conn.execute(text("SELECT * FROM maxroot")).fetchall()
        assert len(rows) == 1

        rows_found = conn.execute(
            text("SELECT COUNT(*) FROM category")).scalar()
        assert rows_found > 0

        rows_found = conn.execute(
            text("SELECT COUNT(*) FROM product")).scalar()
        assert rows_found > 0

        rows_found = conn.execute(
            text("SELECT COUNT(*) FROM image")).scalar()
        assert rows_found > 0


def test_download_pending_images(app, db):
    def file_found(filename,foler):
        found = False
        for root, dir, files in os.walk(foler):
            if filename in files:
                logger.debug(
                    f'file found: root {root}, dir {dir}, file {filename}')
                found = True
                break
        return found
    
    
    with db.engine.connect() as conn:
        conn.execute(text("INSERT into maxroot(name, href) VALUES (:name, :href)"),
                     [{"id":1, "name": "Dresses", "href": "/clothing/womens-dresses"},])
        conn.execute(text("INSERT into category(id,name,season,rootid) VALUES (:id,:name,:season,:rootid)"),
                     [{"id": 202, "name": "dresses", "season": "SS2022", "rootid": 1},])
        conn.execute(text("INSERT into product(id, title,href,categoryid) VALUES (:id, :title,:href,:categoryid)"),
                     [{"id": "9221142106002", "title": "ZAMBRA", "href": "/p-9221142106002-zambra-navy", "categoryid": "202"},])
        conn.execute(text("INSERT into image(href,filename,product_id) VALUES (:href,:filename,:product_id)"),
                     [{"href": "https://b2c-media.maxmara.com/sys-master/m0/MM/2022/1/9221142106/002/s3master/9221142106002-a-zambra.jpg", "filename": "9221142106002-a-zambra.jpg", "product_id": "9221142106002"},
                     {"href": "https://b2c-media.maxmara.com/sys-master/m0/MM/2022/1/9221142106/002/s3details/9221142106002-b-zambra.jpg",
                         "filename": "9221142106002-b-zambra.jpg", "product_id": "9221142106002"},
                      ])
        conn.commit()
    temp_dir= tempfile.TemporaryDirectory().name
    logger.debug(f'temp directory: {temp_dir}')
    app.download_pending_images(temp_dir)
    for f in ('9221142106002-a-zambra.jpg', '9221142106002-b-zambra.jpg'):
        assert file_found(f,temp_dir)
