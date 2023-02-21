
from cmath import log
import json
import pytest
import logging
from sqlalchemy import text

def test_init_db(db):
    db.init_db()

    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    # schemas = inspector.get_schema_names()
    # tables = inspector.get_table_names(schema='test_max')

    assert inspector.has_table('maxroot')
    assert inspector.has_table('category')
    assert inspector.has_table('product')
    assert inspector.has_table('image')


def test_add_categroies(db):
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
