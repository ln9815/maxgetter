import os
import logging
from dynaconf import Dynaconf

logger = logging.getLogger(__name__)


def get_instance_path():
    instance_path = None
    if os.getenv('WORK_DIR'):
        if os.path.exists(os.getenv('WORK_DIR')):
            instance_path = os.getenv('WORK_DIR')
    else:
        instance_path = os.path.join(
                    os.path.dirname(os.path.abspath(os.path.dirname(__file__))), "instance")
    
    if not os.path.exists(instance_path):
        try:
            os.makedirs(instance_path)
        except:
            pass
    
    return instance_path

def get_settings_files():
    instance_path = get_instance_path()

    fn_setting = os.path.join(instance_path, 'settings.toml')
    fn_secrets = os.path.join(instance_path, 'secrets.toml')
    if not os.path.exists(fn_setting):
        logger.warning(f'setting file {fn_setting} doese not exist.')
        assert os.path.exists(fn_setting)
    if not os.path.exists(fn_secrets):
        logger.warning(f'setting file {fn_secrets} doese not exist.')
        assert os.path.exists(fn_secrets)
        
    return [fn_setting,fn_secrets]

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=get_settings_files(),
)
settings.INSTANCE_PATH = get_instance_path()

