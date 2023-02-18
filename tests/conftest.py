
import pytest

from getmax.downloader import MaxDownloader
from getmax.db import MaxDB

@pytest.fixture
def app():
    app = MaxDownloader("testing")
    yield app

@pytest.fixture
def db_sqlite(app):
    db = MaxDB(app.config["SQLALCHEMY_DATABASE_URI"])
    yield db

@pytest.fixture
def db_mysql(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:password@wekate.com:3306/test_max"
    db = MaxDB(app.config["SQLALCHEMY_DATABASE_URI"])
    yield db
