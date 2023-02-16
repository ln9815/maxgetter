import logging

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, and_,
                        create_engine, literal, select)
from sqlalchemy.orm import Session, declarative_base, relationship
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)
Base = declarative_base()


class MaxRoot(Base):
    __tablename__ = "maxroot"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    href = Column(String(200), nullable=False)
    last_update = Column(DateTime, nullable=True, default=func.now())

    categories = relationship("Category", back_populates="root")

    def __repr__(self):
        return f"MaxRoot(id={self.id!r},name={self.name!r}, href={self.href!r})"


class Category(Base):
    __tablename__ = "category"
    id = Column(String(200), primary_key=True)
    name = Column(String(200), nullable=False)
    season = Column(String(200), nullable=False)
    rootid = Column(Integer, ForeignKey("maxroot.id"), nullable=False)
    last_update = Column(DateTime, nullable=True, default=func.now())

    root = relationship("MaxRoot", back_populates="categories")
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"Category(id={self.id!r}, name={self.name!r}, season={self.season!r},rootid={self.rootid!r})"


class Product(Base):
    __tablename__ = "product"
    id = Column(String(100), primary_key=True)
    title = Column(String(200), nullable=False)
    href = Column(String(200), nullable=False)
    categoryid = Column(String(200), ForeignKey("category.id"), nullable=False)
    last_update = Column(DateTime, nullable=True, default=func.now())

    category = relationship("Category", back_populates="products")
    images = relationship("Image", back_populates="product")

    def __repr__(self):
        return f"Product(id={self.id!r}, title={self.title!r}, href={self.href!r})"


class Image(Base):
    __tablename__ = "image"
    id = Column(Integer, primary_key=True, autoincrement=True)
    href = Column(String(200), nullable=False)
    filename = Column(String(200), nullable=False)
    time_requested = Column(DateTime, nullable=True, default=func.now())
    time_downloaded = Column(DateTime, nullable=True)
    time_syned = Column(DateTime, nullable=True)
    product_id = Column(String(100), ForeignKey("product.id"), nullable=False)
    last_update = Column(DateTime, nullable=True, default=func.now())

    product = relationship("Product", back_populates="images")

    def __repr__(self):
        return f"Image(href={self.href!r})"


class MaxDB(object):
    def __init__(self, db_url) -> None:
        self.engine = create_engine(db_url, echo=False, future=True)

    def add_categroies(self, categories):
        from sqlalchemy.dialects.mysql import Insert

        data = [{x: item[x]
                 for x in ('id', 'name', 'season', 'rootid')} for item in categories]

        with self.engine.connect() as connection:
            for item in data:
                insert_stmt = Insert(Category).values(**item)
                on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
                    last_update=func.current_timestamp())
                connection.execute(on_duplicate_key_stmt)
            connection.commit()

    def add_product(self, product):
        from sqlalchemy.dialects.mysql import Insert

        item = {x: product[x] for x in ('id', 'title', 'href', 'categoryid')}
        with self.engine.connect() as connection:
            insert_stmt = Insert(Product).values(**item)
            on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
                last_update=func.current_timestamp())
            connection.execute(on_duplicate_key_stmt)
            connection.commit()

    def add_product_images(self, product, images):
        from sqlalchemy.dialects.mysql import Insert

        with self.engine.connect() as connection:
            for image in images:
                image['product_id'] = product['id']
                item = {x: image[x]
                        for x in ('href', 'filename', 'product_id')}
                insert_stmt = Insert(Image).values(**item)
                on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
                    last_update=func.current_timestamp())
                connection.execute(on_duplicate_key_stmt)
            connection.commit()

    def get_untouched_products(self, products):
        assert isinstance(products, list)

        data = [{x: item[x]
                 for x in ('id', 'title', 'href', 'categoryid')} for item in products]

        with Session(self.engine) as session:
            # empty table
            # session.query(ProductTmp).delete()
            # for x in data:
            #     session.add(ProductTmp(**x))
            # session.bulk_save_objects([ProductTmp(**x) for x in data])
            # session.bulk_insert_mappings(ProductTmp,data)
            # from sqlalchemy import insert
            # session.execute(insert(ProductTmp),data)
            # session.commit()

            # create temporary table
            smt_create_table = 'CREATE TEMPORARY TABLE temp (id VARCHAR(100) NOT NULL, title VARCHAR(200) NOT NULL, href VARCHAR(200) NOT NULL, categoryid VARCHAR(200) NOT NULL)'
            session.execute(smt_create_table)
            session.commit()

            # insert data to temporary table
            from sqlalchemy import Table
            from sqlalchemy.ext.declarative import declarative_base
            smt_insert = Table('temp', declarative_base(
            ).metadata, autoload_with=self.engine).insert()
            session.execute(smt_insert, data)
            session.commit()

            # get compared result
            smt_query = 'SELECT id, title, href, categoryid FROM temp WHERE NOT EXISTS( SELECT * FROM product WHERE product.id = temp.id)'
            return session.execute(smt_query).fetchall()

    def image_set_downloaded(self, pid, href):
        with Session(self.engine) as session:
            img = session.query(Image).filter(
                and_(Image.product_id == pid, Image.href == href)).one_or_none()
            if img:
                img.time_downloaded = func.now()
            session.commit()

    def get_pending_images(self):
        stmt = select(Image.href, Image.filename, Image.product_id, Category.name, Category.season).join(
            Image.product).join(Product.category).where(Image.time_downloaded == None)
        with Session(self.engine) as session:
            imgs = session.execute(stmt).fetchall()
        return imgs

    def init_db(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def init_data(self):
        catas = [
            ('Dresses', '/clothing/womens-dresses'),
            ('Jumpsuits', '/clothing/elegant-womens-jumpsuits'),
            ('Knitwear',  '/clothing/womens-knitwear-sweaters'),
            ('Blouses', '/clothing/womens-blouses-and-shirts'),
            ('Tops and T-shirts',  '/clothing/womens-tops-and-t-shirts'),
            ('Skirts',  '/clothing/skirts'),
            ('Trousers and Jeans', '/clothing/womens-trousers-and-jeans'),
        ]

        with Session(self.engine) as session:
            catagories = []
            for name, href in catas:
                catagories.append(MaxRoot(name=name, href=href))
            session.add_all(catagories)
            session.commit()
