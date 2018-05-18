# coding: utf-8

import codecs
import collections
import re
import logging
import json
from bs4 import BeautifulSoup, SoupStrainer
import sys

from bs4 import BeautifulSoup, SoupStrainer
import requests

PY3 = sys.version_info >= (3, )

logging.basicConfig(level=logging.INFO)

FIRST = 1
LAST = 7118

IMAGE_URL = "http://basededonnees.archives.toulouse.fr/images/docfig/53Fi/FRAC31555_53Fi{}.JPG"
NOTICE_URL = "http://basededonnees.archives.toulouse.fr/4DCGI/Web_VoirLaNotice/34_01/53Fi{}/ILUMP26723"
NOTICE_ID = "tableau_notice"
NOTICE_PREFIX = "53Fi"

DATE_REGEX = "[0-9]+\.[0-9]+\.[0-9]+"

COMMONS = pywikibot.getSite(u'commons', u'commons')

input_dict = json.loads(open("tree.json").read())

def mapping(s):
    map = {
        u"Auteur(s) :": "authors",
        u"Type document :": "type",
        u"Technique :": "technique",
        u"Format :": "format",
        u"Support :": "support",
        u"Etat matériel :": "material_condition",
        u"Série :": "series",
        u"Sous-série :": "sub_series",
        u"Producteur :": "producer",
        u"Plan de classement :": "order",
        u"Origine du document :": "origin",
        u"Mode d'entrée :": "entry_mode",
        u"Année d'entrée :": "entry_year",
        u"Droits :": "rights",
        u"Original Consultable :": "original_consultable",
        u"Observations :": "observation",
        u"Termes d'indexation :": "indexation",
        u"Période historique :": "historical_period",
    }
    return map.get(s, s)


def text(s):
    text_value = s.string.strip()
    if not PY3:
        text_value = unicode(s.string).strip()
    return text_value


def twodigits(s):
    return s.zfill(2)


def read(i):
    response = requests.get(NOTICE_URL.format(i))
    htmlSource = response.text
    soup = BeautifulSoup(htmlSource, 'html.parser', parse_only=SoupStrainer(id=NOTICE_ID))
    content = soup.find(id=NOTICE_ID)
    if content is None:
        logging.warn("Unable to download notice %d", i)
        return None
    result={}
    # title
    title = content.find_all('p')[1].string
    if title is None:
        logging.warn("Unable to parse notice %d", i)
        return None
    parts = re.split(" - ", title)
    key = parts[0]
    result["title"]=parts[1]
    m = re.search(DATE_REGEX, parts[1])
    if m is not None:
        if m.group(0) == "15.16.17": #15.16.17.18/10/62
            result["day"]="15"
            result["month"]="10"
            result["year"]="1962"
        else:
            p = re.split("\.",m.group(0))
            result["day"]=twodigits(p[0])
            result["month"]=twodigits(p[1])
            result["year"]=p[2] if len(p[2]) == 4 else "19"+p[2]
    spans = content.find_all('span')
    if spans is not None:
        for i in range(0, len(spans)):
            if i == 0:
                result["description"] = text(spans[i])
            elif i < len(spans)-1 and spans[i]["class"][0] == "titre":
                if "Format :" == text(spans[i]):
                    formats = re.split("x", text(spans[i+1]).replace("cm", "").replace(" ", ""), flags=re.IGNORECASE)
                    if formats is not None and len(formats) > 1:
                        result["height"] = formats[0]
                        result["width"] = formats[1]
                    else:
                        result[mapping(text(spans[i]))] = text(spans[i+1])
                elif "Plan de classement :" == text(spans[i]):
                    order = re.split(">", text(spans[i+1]))
                    if len(order)>2:
                        result[mapping(text(spans[i]))] = re.split(">", text(spans[i+1]))[-2].strip().rstrip(">")
                    else:
                        result[mapping(text(spans[i]))] = text(spans[i+1])
                elif "Termes d'indexation :" == text(spans[i]):
                    result[mapping(text(spans[i]))] = [v.string.strip() for v in spans[i+1].find_all("a")]
                else:
                    result[mapping(text(spans[i]))] = text(spans[i+1])
    return result


def flush(tree, fileName="tree"):
    logging.info("Writing")
    with codecs.open(fileName+".json", "w", encoding="utf-8") as data:
        try:
            json.dump(tree, data, indent=2, ensure_ascii=False)
        except BaseException as e:
            logging.error(e)


def main():
    result=collections.OrderedDict()
    for i in range(FIRST,LAST+1):
        logging.info("Reading notice %d", i)
        notice = read(i)
        if notice is not None:
            result["53Fi"+str(i)] = notice
        if i % 25 is 0 or i == LAST:
            flush(result)


def reverse():
    result = collections.OrderedDict()
    for notice in input_dict:
        for key, value in input_dict[notice].items():
            if type(value) is list:
                if key in result:
                    for val in value:
                        if val not in result[key]:
                            result[val].append(key)
                    else:
                        result[key]=value
            else:
                if key in result:
                    if value not in result[key]:
                        result[key].append(value)
                else:
                    result[key]=[value]
    for key in result:
        result[key] = sorted(result[key])
    flush(result, "reverse")

<<<<<<< HEAD
def upload(i):
    url_image = IMAGE_URL_PREFIX + str(i) + IMAGE_URL_SUFFIX
    logging.info(url_image)
#    descr = str(input_dict[NOTICE_PREFIX+str(i)])
    descr = "Test"
    bot = UploadRobot(url=url_image, description=descr,
        useFilename=input_dict[NOTICE_PREFIX+str(i)]["title"],
        summary="#AndreCros : test",
        targetSite=COMMONS)
    bot.run()

descr_template = u"{{Artwork|ID={{Archives municipales de Toulouse - FET link|}}|artist={{Creator:André Cros}}|credit line=|date=|location=|description={{fr|}}|dimensions={{Size|cm||}}|gallery={{Institution:Archives municipales de Toulouse}}|medium={{Technique|photograph}}|object history=|permission={{CC-by-SA-4.0}}|references=|source={{Fonds André Cros - Archives municipales de Toulouse}}|title={{fr|}}}}"

def description(i):
    input_dict = json.loads(open("tree.json").read())
    id_number = "53Fi"+str(i)
    notice = input_dict[id_number]
    result = descr_template[:59]+id_number+descr_template[59:110]
    if "year" in notice:
        result = result + notice["year"]
    if "month" in notice:
        result = result + "-" + notice["month"]
    if "day" in notice:
        result = result + "-" + notice["day"]
    result = result + descr_template[110:138] + notice["description"]
    if "observation" in notice:
        result = result + "\n Observation: " + notice["observation"]
    result = result + descr_template[138:160]
    if "height" in notice and "width" in notice :
        result = result + notice["height"] + "|" + notice["width"]
    else:
        result = result + "|"
    result = result + descr_template[163:270] + notice["origin"] + descr_template[270:385] + notice["title"] + descr_template[385:]
    return result


if __name__ == "__main__":
    print description(1761)
