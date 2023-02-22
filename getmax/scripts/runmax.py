import click
import logging
import os
import sys
from getmax.downloader import MaxDownloader
from getmax.util import logging_init
logger = logging.getLogger(__name__)


@click.command()
@click.option('--workdir', '-w', required=True, type=str, help='work directory for this app.')
@click.option('--stream', '-s', is_flag=True, help='Stream output for log.')
@click.option('--initdb', is_flag=True, help='Init database and data.')
@click.option('--download', '-d', is_flag=True, help='Downlaod the pending images in database.')
@click.option('--retrieve', '-r', is_flag=True, help='Retrieve product and image information, and update to database.')
def run(workdir, stream, initdb, download, retrieve):
    
    if workdir:
        if os.path.exists(workdir):
            os.environ['WORK_DIR'] = workdir
        else:
            print(f'{workdir} does not exists.')
            return
    else:
        if os.environ.get('WORK_DIR') is None:
            print(f'env var WORK_DIR does not exist.')
            return

    from getmax.config import settings

    logfile = os.path.join(settings.INSTANCE_PATH, settings.LOG_FILE)
    click.echo(f'log file saved on {logfile}.')

    if str(settings.MAIL_SENDTO).strip() != '':
        logging_init(log_file=settings.LOG_FILE, log_level=settings.LOG_LEVEL,
                     stream=stream, app='MaxGetter', sendto=settings.MAIL_SENDTO)
    else:
        logging_init(log_file=settings.LOG_FILE,
                     log_level=settings.LOG_LEVEL, stream=stream)

    app = MaxDownloader()

    if initdb:
        click.echo('Start to init databas.')
        app.init()
        click.echo('Database was initialized.')
    if retrieve:
        click.echo('Start to init retrieve product and image information.')
        app.retrieve_product_image_info()
        click.echo(
            'Product and image inforamtion were retrieved and saved to database.')
    if download:
        click.echo('Start to download pending images.')
        app.download_pending_images()
        click.echo('Pending images in database was downlaoded and saved.')


def do():
    try:
        run()
    except Exception as e:
        logger.error(e, exc_info=sys.exc_info())


if __name__ == '__main__':
    do()
