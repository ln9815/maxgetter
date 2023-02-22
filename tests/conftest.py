import pytest

from getmax.config import settings
from getmax.downloader import MaxDownloader

settings.DATABASE_TPYE = 'sqlite'
settings.SQLITE_DB = 'max_test.db'
settings.ENV = 'test'

@pytest.fixture
def app():
    app = MaxDownloader()
    app.db.init_db()
    yield app

@pytest.fixture
def db(app):
    yield app.db
