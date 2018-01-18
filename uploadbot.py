import logging
import os
import sys

import mwclient
import requests

import bot_config


LOG =  logging.getLogger(name=__name__)
HANDLER = logging.StreamHandler(stream=sys.stdout)
HANDLER.setFormatter(logging.Formatter('%(asctime)s    %(module)s    %(levelname)s    %(message)s'))
HANDLER.setLevel(logging.DEBUG)
LOG.addHandler(HANDLER)
LOG.setLevel(logging.DEBUG)

IMAGE = 'http://basededonnees.archives.toulouse.fr/images/docfig/53Fi/FRAC31555_53Fi1761.JPG'


def filename_of(url):
    return url.split('/')[-1]


def download_file(url_file):
    LOG.info('Download %s', url_file)
    filename = filename_of(url_file)
    r = requests.get(url_file, stream=True)
    if r.status_code == 200:
        LOG.info('OK<200>')
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    else:
        LOG.error('KO<%s>', r.status_code)


def upload(site, url_file, description):
    download_file(url_file)
    file = filename_of(url_file)
    LOG.info('Upload %s', file)
    site.upload(open(file, 'rb'), 'File:{}'.format(file), description, ignore=True)
    os.remove(file)


def main():
    commons = mwclient.Site('commons.wikimedia.org')
    commons.login(username=bot_config.USER, password=bot_config.PASS)
    upload(commons, IMAGE, 'Test André Cros')


if __name__ == '__main__':
    main()