
from cmath import log
import json
import pytest
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)


def test_sqlite_init_db(db_sqlite):
    fun_init_db(db_sqlite)


def test_sqlite_init_data(db_sqlite):
    fun_init_db(db_sqlite)


def test_sqlite_add_categroies(db_sqlite):
    fun_add_categroies(db_sqlite)


def test_mysql_init_db(db_mysql):
    fun_init_db(db_mysql)


def test_mysql_init_data(db_mysql):
    fun_init_db(db_mysql)


def test_mysql_add_categroies(db_mysql):
    fun_add_categroies(db_mysql)


def fun_init_db(db):
    db.init_db()

    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    # schemas = inspector.get_schema_names()
    # tables = inspector.get_table_names(schema='test_max')

    assert inspector.has_table('maxroot')
    assert inspector.has_table('category')
    assert inspector.has_table('product')
    assert inspector.has_table('image')


def fun_init_data(db):
    db.init_db()
    db.init_data()

    with db.engine.connect() as conn:
        results = conn.execute(text("SELECT * FROM max_root")).fetchall()
        assert len(results) > 0


def fun_add_categroies(db):
    db.init_db()
    db.init_data()

    category_1 = {'id': '202',
                  'name': 'dresses',
                  'season': 'SS2023',
                  'rootid': 1
                  }
    category_2 = {'id': '202',
                  'name': 'dresses_updated',
                  'season': 'SS2023',
                  'rootid': 1
                  }
    category_3 = {'id': '203',
                  'name': 'dresses_added',
                  'season': 'SS2023',
                  'rootid': 1
                  }

    # add data
    db.add_categroies([category_1])

    rows = db.engine.connect().execute(
        text("SELECT * FROM category")).fetchall()
    assert len(rows) == 1

    db.add_categroies([category_2])
    rows = db.engine.connect().execute(
        text("SELECT * FROM category")).fetchall()
    assert len(rows) == 1

    rows = db.engine.connect().execute(
        text("SELECT * FROM category WHERE name = 'dresses_updated'")).fetchall()
    assert len(rows) == 0

    db.add_categroies([category_3])
    rows = db.engine.connect().execute(
        text("SELECT * FROM category")).fetchall()
    assert len(rows) == 2
    rows = db.engine.connect().execute(
        text("SELECT * FROM category WHERE name = 'dresses_added'")).fetchall()
    assert len(rows) == 1
