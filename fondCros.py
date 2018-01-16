# coding: utf-8
import bs4
import codecs
import collections
import urllib
import re
import logging
import json
from bs4 import BeautifulSoup, SoupStrainer

logging.basicConfig(level=logging.INFO)

FIRST = 1
LAST = 7118

IMAGE_URL_PREFIX = "http://basededonnees.archives.toulouse.fr/images/docfig/53Fi/FRAC31555_53Fi"
IMAGE_URL_SUFFIX = ".JPG"
NOTICE_URL_PREFIX = "http://basededonnees.archives.toulouse.fr/4DCGI/Web_VoirLaNotice/34_01/53Fi"
NOTICE_URL_SUFFIX = "/ILUMP26723"
NOTICE_ID = "tableau_notice"

DATE_REGEX = "[0-9]+\.[0-9]+\.[0-9]+"

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
    return unicode(s.string).strip()

def twodigits(s):
    return ("0"+s) if len(s) == 1 else s

def read(i):
    sock = urllib.urlopen(NOTICE_URL_PREFIX+str(i)+NOTICE_URL_SUFFIX)
    htmlSource = sock.read()
    sock.close()
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
    input_dict = json.loads(open("tree.json").read())
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


if __name__ == "__main__":
    main()
    reverse()
