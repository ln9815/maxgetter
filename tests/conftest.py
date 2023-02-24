import pytest

from getmax.config import settings
from getmax.downloader import MaxDownloader

settings.DATABASE_TPYE = 'mysql'
settings.SQLITE_DB = 'max_test.db'
settings.ENV = 'test'

@pytest.fixture
def app():
    app = MaxDownloader()
    app.db.init_db()
    yield app


