import os
import logging

logger = logging.getLogger(__name__)


class BaseConfig(object):
    MAX_HOST = "https://world.maxmara.com"
    LOGGING_LEVEL = logging.DEBUG
    FOLDER_SAVE = None


class DevelopmentConfig(BaseConfig):
    SQLITE_DB = 'data-dev.db'


class TestingConfig(BaseConfig):
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-memory database
    SQLITE_DB = 'data-uat.db'


class ProductionConfig(BaseConfig):
    SQLITE_DB = 'data-pro.db'    
    LOGGING_LEVEL = logging.INFO


def get_setting(env="development"):
    cfg = {'development': DevelopmentConfig,
           'testing': TestingConfig, 'production': ProductionConfig}
    if env in cfg.keys():
        return cfg[env]
    else:
        logger.error(f'wrong env, should be in {cfg.keys()}')
        return None
