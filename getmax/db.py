import logging

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, and_,
                        create_engine, literal, select)
from sqlalchemy.orm import Session, declarative_base, relationship
from sqlalchemy.sql import func
from sqlalchemy import text, insert

logger = logging.getLogger(__name__)
Base = declarative_base()


class MaxRoot(Base):
    __tablename__ = "maxroot"
    id = Column(Integer, primary_key=True)
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
    href = Column(String(200), primary_key=True, nullable=False)
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
        self.engine = create_engine(db_url, echo=False)

    def add_categroies(self, categories):
        data = [{x: item[x]
                 for x in ('id', 'name', 'season', 'rootid')} for item in categories]

        with self.engine.connect() as connection:
            for item in data:
                if self.engine.name == 'mysql':
                    insert_stmt = insert(Category).values(
                        **item).prefix_with('IGNORE')
                elif self.engine.name == 'sqlite':
                    insert_stmt = insert(Category).values(
                        **item).prefix_with('OR IGNORE')
                connection.execute(insert_stmt)
            connection.commit()

    def add_product(self, product):
        item = {x: product[x] for x in ('id', 'title', 'href', 'categoryid')}
        with self.engine.connect() as connection:
            if self.engine.name == 'mysql':
                insert_stmt = insert(Product).values(
                    **item).prefix_with('IGNORE')
                connection.execute(insert_stmt)
            elif self.engine.name == 'sqlite':
                insert_stmt = insert(Product).values(
                    **item).prefix_with('OR IGNORE')
                connection.execute(insert_stmt)
            connection.commit()

    def add_product_images(self, product, images):

        with self.engine.connect() as connection:
            for image in images:
                image['product_id'] = product['id']
                item = {x: image[x]
                        for x in ('href', 'filename', 'product_id')}
                if self.engine.name == 'mysql':
                    insert_stmt = insert(Image).values(
                        **item).prefix_with('IGNORE')
                    connection.execute(insert_stmt)
                elif self.engine.name == 'sqlite':
                    insert_stmt = insert(Image).values(
                        **item).prefix_with('OR IGNORE')
                    connection.execute(insert_stmt)
            connection.commit()

    def get_untouched_products(self, products):
        assert isinstance(products, list)

        with Session(self.engine) as session:
            smt_query = text('SELECT id FROM product')
            rows = session.execute(smt_query).fetchall()
            new_ids = set([item['id']
                          for item in products]).difference(set(rows))

            return [item for item in products if item['id'] in new_ids]

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
        logger.debug(f'total {len(imgs)} images is pending.')
        return imgs

    def init_db(self):
        Base.metadata.create_all(self.engine)
        self.remove_data()

    def init_data(self):
        catas = [
            (1, 'Dresses', '/clothing/womens-dresses'),
            (2, 'Jumpsuits', '/clothing/elegant-womens-jumpsuits'),
            (3, 'Knitwear',  '/clothing/womens-knitwear-sweaters'),
            (4, 'Blouses', '/clothing/womens-blouses-and-shirts'),
            (5, 'Tops and T-shirts',  '/clothing/womens-tops-and-t-shirts'),
            (6, 'Skirts',  '/clothing/skirts'),
            (7, 'Trousers and Jeans', '/clothing/womens-trousers-and-jeans'),
        ]

        items = [dict(zip(('id', 'name', 'href'), row)) for row in catas]

        with Session(self.engine) as session:
            for item in items:
                if self.engine.name == 'mysql':
                    insert_stmt = insert(MaxRoot).values(
                        **item).prefix_with('IGNORE')
                    session.execute(insert_stmt)
                elif self.engine.name == 'sqlite':
                    insert_stmt = insert(MaxRoot).values(
                        **item).prefix_with('OR IGNORE')
                    session.execute(insert_stmt)
            session.commit()

    def remove_data(self):
        def delete_data(table):
            try:
                session = Session(self.engine)
                session.execute(text(f'DELETE FROM {table};'))
                session.commit()
            except Exception as e:
                pass
            finally:
                session.close()

        for table in ('image', 'product', 'category', 'maxroot'):
            delete_data(table)
