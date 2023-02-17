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
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}:{}/{}".format(
        os.getenv("DB_USER"),
        os.getenv("DB_PASSWORD"),
        os.getenv("DB_HOST"),
        os.getenv("DB_PORT"),
        os.getenv("DB_DATABASE"))
    FOLDER_SAVE = os.getenv("FOLDER_SAVE")
    LOGGING_LEVEL = logging.INFO


def get_setting(env="development"):
    cfg = {'development': DevelopmentConfig,
           'testing': TestingConfig, 'production': ProductionConfig}
    if env in cfg.keys():
        return cfg[env]
    else:
        logger.error(f'wrong env, should be in {cfg.keys()}')
        return None
