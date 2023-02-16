import pytest
import logging
import os

from getmax.setting import ProductionConfig, BaseConfig
from getmax.config import Config

logger = logging.getLogger(__name__)

def test_from_object(app):
    cfg = Config(app.root_path)
    cfg.from_object(BaseConfig)
    assert cfg["MAX_HOST"] == BaseConfig.MAX_HOST

    cfg.from_object(ProductionConfig)
    assert cfg["LOGGING_LEVEL"] == ProductionConfig.LOGGING_LEVEL
    assert cfg["SQLALCHEMY_DATABASE_URI"] == ProductionConfig.SQLALCHEMY_DATABASE_URI

def test_from_json():
    root_path = os.path.abspath(os.path.dirname(__file__))
    cfg = Config(root_path)
    cfg.from_json("config.json")
    assert cfg["MAX_HOST"] == "https://world.maxmara.com"
    assert cfg["SQLALCHEMY_DATABASE_URI"] == "mysql+pymysql://root:****@****:3306/max_db"
    assert cfg["LOGGING_LEVEL"] == 20

