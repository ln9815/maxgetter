import click
import logging
import os
import sys

logger = logging.getLogger(__name__)


@click.command()
@click.option('--workdir', help='work directory for this app.')
@click.option('--initdb', is_flag=True, help='Init database and data.')
@click.option('--retrieve', '-r', is_flag=True, help='Retrieve product and image information, and update to database.')
@click.option('--download', '-d', is_flag=True, help='Downlaod the pending images in database.')
@click.option('--stream', '-s', is_flag=True, help='Stream output for log.')
def run(workdir, stream, initdb, download, retrieve):

    old_env = os.getenv('WORK_DIR')
    if workdir:
        if os.path.exists(workdir):
            os.environ['WORK_DIR'] = workdir
        else:
            print(f'{workdir} does not exists, and no workdir specified.')
            exit(-1)

    if os.getenv('WORK_DIR') is None:
        print(f'env var WORK_DIR does not exist.')
        exit(-1)

    from getmax.config import settings
    from getmax.downloader import MaxDownloader
    from getmax.util import logging_init

    if settings is None:
        path = os.getenv('WORK_DIR')
        print(f'setting files does not exist in {path}.')
        exit()

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

    if old_env:
        os.environ['WORK_DIR'] = old_env
    else:
        del os.environ['WORK_DIR']


def do():
    try:
        run()
    except Exception as e:
        logger.error(e, exc_info=sys.exc_info())


if __name__ == '__main__':
    do()
