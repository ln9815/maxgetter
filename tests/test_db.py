
from cmath import log
import json
import pytest
import logging
from sqlalchemy import text



logger = logging.getLogger(__name__)



def test_init_db(db):
    db.init_db()
    from sqlalchemy import inspect

    insp = inspect(db.engine)
    assert insp.has_table("max_root")
    assert insp.has_table("category")
    assert insp.has_table("product")
    assert insp.has_table("product_image")    
    '''
    method sqlalchemy.engine.default.DefaultDialect.has_table(connection, table_name, schema=None, **kw)
    '''

def test_init_data(db):
    db.init_db()
    db.init_data()

    
    with db.engine.connect() as conn:
        rows_found = conn.execute(text("SELECT * FROM max_root")).scalar()
        assert rows_found > 0
        results = conn.execute(text("SELECT * FROM max_root")).fetchall()
        for row in  results:
            logger.debug(f'row: {row}')
        assert len(results) > 0
        
