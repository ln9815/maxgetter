import click
import logging
import os
import sys
from getmax.downloader import MaxDownloader
from getmax.util import logging_init
logger = logging.getLogger(__name__)


@click.command()
@click.option('--env', type=click.Choice(['DEV', 'TST', 'PRO'], case_sensitive=False), required=True, help=f'Envrionment of app.')
@click.option('--initdb', is_flag=True, help='Init database and data.')
@click.option('--download', '-d', is_flag=True, help='Downlaod the pending images in database.')
@click.option('--retrieve', '-r', is_flag=True, help='Retrieve product and image information, and update to database.')
@click.option('--logfile', is_flag=True, help='Where log file to save.')
@click.option('--loglevel', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False), default='INFO', help=f'log levels')
@click.option('--stream', '-s', is_flag=True, help='Stream output for log.')
@click.option('--sendto', is_flag=True, help='Send email when error occured.')
def run(env, initdb, download, retrieve, stream, logfile, loglevel, sendto):
    env_dict = {'dev': 'development',
                'tst': 'testing',
                'pro': 'production'}
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR
    }

    if env.lower() == 'pro':
        for var in ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_DATABASE", "FOLDER_SAVE"):
            if os.getenv(var) is None:
                click.echo(f'env variable {var} is required.')
                return

    app = MaxDownloader(env_dict[env.lower()])
    if os.getenv('LOG_FILE') is not None:
        logfile = os.getenv('LOG_FILE')
    if not logfile:
        logfile = os.path.join(app.instance_path, 'max.log')
    click.echo(f'start the application, log file saved on {logfile}.')

    if os.getenv('MAIL_SENDTO') is not None:
        sendto = os.getenv('MAIL_SENDTO')
    if sendto:
        logging_init(log_file=logfile, log_level=levels[loglevel.upper(
        )], stream=stream, app='MaxGetter', sendto=sendto)
    else:
        logging_init(log_file=logfile,
                     log_level=levels[loglevel.upper()], stream=stream)

    if initdb:
        click.echo('Start to init databas.')
        app.init()
        click.echo('Database was initialized.')
    if retrieve:
        app.retrieve_product_image_info()
        click.echo(
            'Product and image inforamtion were retrieved form websit, and updated to database.')
    if download:
        app.download_pending_images()
        click.echo('Pending images in database was downlaoded and saved.')


def do():
    try:
        run()
    except Exception as e:
        logger.error(e, exc_info=sys.exc_info())


if __name__ == '__main__':
    do()
