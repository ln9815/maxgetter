#!/usr/bin/python
# -*- coding: UTF-8 -*-

import datetime
import os
import click
import time
import schedule


@click.command()
@click.option('--cmd', '-c', type=str, required=True, help='command to run.')
@click.option('--times', '-t', type=str, required=True, help='times to run command. valid format is HH:MM(:SS) and combined with %')
def run(cmd, times):
    def fn(cmd):
        print('{}: start to run command: {}.'.format(
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), cmd))
        os.system(cmd)
        print('{}: end of command: {}.'.format(
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), cmd))
    for t in times.split('%'):
        schedule.every().day.at(t).do(fn, cmd)
        print(f'command: {cmd} on: {t} added to list.')
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    run()
