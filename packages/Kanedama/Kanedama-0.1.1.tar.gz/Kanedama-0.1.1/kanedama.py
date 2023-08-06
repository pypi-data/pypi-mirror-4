#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import smtplib

from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from ghost import Ghost

try:
    from ConfigParser import SafeConfigParser as ConfigParser
except ImportError:  # py3k
    import sys
    minor = sys.version_info[1]
    if minor >= 2:
        # SafeConfigParser is deprecated as of 3.2
        from configparser import ConfigParser
    else:
        from configparser import SafeConfigParser as ConfigParser


def _get_config():
    path = os.path.join(
        os.getenv('HOME'), '.config', 'kanedama', 'config.ini'
    )
    if not os.path.exists(path):
        raise Exception('Unable to find configuration at %s' % path)

    config = ConfigParser()
    config.read(path)
    return config


def heroku(api_key, year, month):
    ghost = None

    file_path = '/tmp/heroku_invoice_%d-%d.png' % (year, month)
    if os.path.exists(file_path):
        os.remove(file_path)

    # TODO: make dimensions configurable? Automatic (is that possible?)?
    ghost = Ghost(viewport_size=(1000, 1600))
    ghost.wait_timeout = 20

    ghost.open('https://id.heroku.com/login')
    ghost.fill("form", dict(email="", password=api_key))
    ghost.fire_on("form", "submit", expect_loading=True)
    ghost.open('https://dashboard.heroku.com/invoices/%s/%s' % (year, month))

    ghost.capture_to(file_path)

    return file_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int)
    parser.add_argument('--month', type=int)
    parser.add_argument('--email')
    parser.add_argument('--key')
    args = parser.parse_args()

    config = _get_config()

    year, month = args.year, args.month

    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month - 1  # default to last month

    if month == 0:
        year = year - 1
        month = 12

    api_key = None
    if args.key:
        api_key = args.key

    if not api_key:
        api_key = config.get('heroku', 'api_key')

    if not api_key:
        raise Exception(
            'Unable to find an API key for Heroku. Either pass one explicitly '
            'with --key or create a configuration file as per the example and '
            'put it in ~/.config/kanedama/config.ini'
        )

    file_path = heroku(api_key, year, month)

    if args.email:
        me = config.get('main', 'mail_from')

        msg = MIMEMultipart()
        msg['Subject'] = 'Heroku invoice for %d-%d' % (year, month)
        msg['From'] = me
        msg['To'] = args.email

        with open(file_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header(
                'Content-Disposition', 'attachment; filename="%s"' %
                file_path.split('/')[-1]
            )
            msg.attach(img)

        s = smtplib.SMTP(config.get('main', 'smtp_host'))
        s.sendmail(me, args.email, msg.as_string())
        s.quit()
    else:
        print(file_path)
