
import pytest

from getmax.downloader import MaxDownloader
from getmax.db import MaxDB

@pytest.fixture
def app():
    app = MaxDownloader("testing")
    yield app

@pytest.fixture
def db(app):
    db = MaxDB(app.config["SQLALCHEMY_DATABASE_URI"])
    yield db
    