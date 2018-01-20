# coding: utf-8
import logging
import os
import sys
import json

import mwclient
import requests

import bot_config

LOG =  logging.getLogger(name=__name__)
HANDLER = logging.StreamHandler(stream=sys.stdout)
HANDLER.setFormatter(logging.Formatter('%(asctime)s    %(module)s    %(levelname)s    %(message)s'))
HANDLER.setLevel(logging.DEBUG)
LOG.addHandler(HANDLER)
LOG.setLevel(logging.DEBUG)

CAT_NAME = u"\n\n[[Category:Fonds André Cros - {}]]"

IMAGE_URL = "http://basededonnees.archives.toulouse.fr/images/docfig/53Fi/FRAC31555_{}.JPG"

input_dict = json.loads(open("tree.json").read())

descr_template = u"{{Artwork\n|ID={{Archives municipales de Toulouse - FET link|}}\n|artist={{Creator:André Cros}}\n|credit line=\n|date=\n|location=\n|description={{fr|}}\n|dimensions={{Size|cm|}}\n|gallery={{Institution:Archives municipales de Toulouse}}\n|medium={{Technique|photograph}}\n|object history={{fr|}}\n|permission={{CC-by-SA-4.0}}\n|references=\n|source={{Fonds André Cros - Archives municipales de Toulouse}}\n|title={{fr|}}\n}}"


def description(id_number):
    notice = input_dict[id_number]
    result = descr_template[:60]+id_number+descr_template[60:114]
    if "year" in notice:
        result = result + notice["year"]
    if "month" in notice:
        result = result + "-" + notice["month"]
    if "day" in notice:
        result = result + "-" + notice["day"]
    result = result + descr_template[114:144] + notice["description"]
    if "observation" in notice:
        result = result + "\nObservation: " + notice["observation"]
    result = result + descr_template[144:169]
    if "height" in notice and "width" in notice :
        result = result + notice["height"].replace(",",".") + "|" + notice["width"].replace(",",".")
    else:
        result = result + "|"
    result = result + descr_template[169:284] + notice["origin"] + descr_template[284:405] + notice["title"] + descr_template[405:]
    # Categories
    if "order" in notice:
        result = result + CAT_NAME.format(notice["order"]).replace(">","-")
    else:
        result = result + "\n\n[[Category:Fonds André Cros -No notice]]"
    return result


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


def upload(site, id_number):
    url_file=IMAGE_URL.format(id_number)
    title=input_dict[id_number]["title"]+" - "+id_number
    descr=description(id_number)
    download_file(url_file)
    file = filename_of(url_file)
    LOG.info('Upload %s', title)
    site.upload(open(file, 'rb'), u'File:{}.jpg'.format(title), descr, ignore=True)
    os.remove(file)


def main():
    commons = mwclient.Site('commons.wikimedia.org')
    commons.login(username=bot_config.USER, password=bot_config.PASS)
    first = 442
    last = 442
    for i in range(first,last+1):
        id_number = "53Fi"+str(i)
        upload(commons, id_number)


if __name__ == '__main__':
    main()
