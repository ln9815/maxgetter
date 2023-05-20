import logging
import os
import sys
from string import Template
from datetime import datetime
import threading
import os
import click

logger = logging.getLogger(__name__)


class MailLogHandler(logging.Handler):
    '''
    日志错误邮件通知
    '''

    def __init__(self, app=None, sendto=None):
        logging.Handler.__init__(self)
        self.app = app
        self.sendto = sendto

    def emit(self, record):
        para = {'app': self.app,
                'levelname': record.levelname,
                'process': record.process,
                'processName': record.processName,
                'asctime': record.asctime,
                'pathname': record.pathname,
                'lineno': record.lineno,
                'message': record.message,
                'exc_text': record.exc_text,
                }
        fn_template = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'mail_template.html')
        with open(fn_template, "r", encoding='utf-8') as f:
            data = f.read()
        tpl = Template(data)
        body = tpl.safe_substitute(para)
        subject = '[{}] Notification from {}'.format(
            para['levelname'], para['app'])
        send_mail(self.sendto, subject, body, _subtype='html')


def send_mail(sendto, subject, content, _subtype='plain'):
    """
    发送电子邮件
    Powershell
    $env:MAIL_SENDER_SMTP="smtp.qq.com"
    $env:MAIL_SENDER_ADDR="****@qq.com"
    $env:MAIL_SENDER_PASSWORD="********"
    """
    from email.header import Header
    from email.mime.text import MIMEText
    from smtplib import SMTP_SSL

    for var in ('MAIL_SENDER_SMTP', 'MAIL_SENDER_ADDR', 'MAIL_SENDER_PASSWORD'):
        if os.getenv(var) is None:
            logger.warning(f'env variable {var} is required.')
            return
    MAIL_SENDER_SMTP = os.getenv('MAIL_SENDER_SMTP')
    MAIL_SENDER_ADDR = os.getenv('MAIL_SENDER_ADDR')
    MAIL_SENDER_PASSWORD = os.getenv('MAIL_SENDER_PASSWORD')

    try:
        smtp = SMTP_SSL(MAIL_SENDER_SMTP)
        # set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式
        smtp.set_debuglevel(0)
        smtp.ehlo(MAIL_SENDER_SMTP)
        smtp.login(MAIL_SENDER_ADDR, MAIL_SENDER_PASSWORD)

        msg = MIMEText(content, _subtype, 'utf-8')
        msg["Subject"] = Header(subject, 'utf-8')
        msg["From"] = MAIL_SENDER_ADDR
        msg["To"] = sendto
        smtp.sendmail(MAIL_SENDER_ADDR, sendto, msg.as_string())
        smtp.quit()
    except Exception as e:
        logger.warning(
            'sent mail failed, eror: %s, send to: %s, subject: %s', e, sendto, subject)


def logging_init(log_file=None, log_level=logging.DEBUG,
                 fmt=None, stream=True, app=None, sendto=None):
    if log_file is None:
        import inspect
        caller = inspect.currentframe().f_back
        fn_caller = caller.f_globals['__file__']
        log_file = '{}.log'.format(''.join(fn_caller.split('.')[:-1]))
    fmt = '%(asctime)-15s-%(filename)s-%(lineno)d-%(name)s-%(levelname)s-%(message)s' if fmt is None else fmt

    LOG_LEVLES = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR
    }

    loglevel = logging.DEBUG
    if isinstance(log_level,int):
        loglevel = log_level
    if isinstance(log_level,str):
        if log_level.upper() in LOG_LEVLES.keys():
            loglevel = LOG_LEVLES[log_level.upper()]


    formatter = logging.Formatter(fmt)
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(loglevel)
    fh.setFormatter(formatter)

    logger_root = logging.getLogger()
    logger_root.setLevel(log_level)
    logger_root.addHandler(fh)
    if sendto is not None and app is not None:
        ml = MailLogHandler(app, sendto)
        ml.setLevel(logging.ERROR)
        ml.setFormatter(formatter)
        logger_root.addHandler(ml)

    if stream:
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(formatter)
        logger_root.addHandler(ch)


def loop(interval, unit, fun, arg=None):
    assert unit in ('H', 'M', 'S')
    seconds = {'H': interval * 3600, 'M': interval * 60,  'S': interval}
    dash = '-' * 20

    print(f'{dash} start to run command {dash}')
    global timers
    if arg is None:
        fun()
        timer = threading.Timer(seconds[unit], loop, (interval, unit, fun))
    else:
        fun(*arg)
        timer = threading.Timer(
            seconds[unit], loop, (interval, unit, fun, arg))
    print(f'{dash} wait {interval} {unit} start again {dash}')
    timer.start()


def hello(name1, name2):
    print(f'hello {name1}, {name2}.')


def bar():
    print('bar')


if __name__ == '__main__':
    # loop(5, 'S', hello, ('victor','bogan'))
    loop(5, 'S', bar)
