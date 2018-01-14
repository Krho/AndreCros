# coding: utf-8
import bs4
import urllib
import re
import logging
import json
from bs4 import BeautifulSoup

LOG = logging.getLogger("categories")

FIRST = 338
LAST = 7118

IMAGE_URL_PREFIX = "http://basededonnees.archives.toulouse.fr/images/docfig/53Fi/FRAC31555_53Fi"
IMAGE_URL_SUFFIX = ".JPG"
NOTICE_URL_PREFIX = "http://basededonnees.archives.toulouse.fr/4DCGI/Web_VoirLaNotice/34_01/53Fi"
NOTICE_URL_SUFFIX = "/ILUMP26723"
NOTICE_ID = "tableau_notice"

DATE_REGEX = "[0-9]+\.[0-9]+\.[0-9]+"

def read(i):
    sock = urllib.urlopen(NOTICE_URL_PREFIX+str(i)+NOTICE_URL_SUFFIX)
    htmlSource = sock.read()
    sock.close()
    soup = BeautifulSoup(htmlSource, 'html.parser')
    content = soup.find(id=NOTICE_ID)
    result={}
    # title
    title = content.find_all('p')[1].string
    parts = re.split(" - ", title)
    key = parts[0]
    result["title"]=parts[1]
    m = re.search(DATE_REGEX, parts[1])
    if m is not None:
        p = re.split("\.",m.group(0))
        result["day"]=p[0]
        result["month"]=p[1]
        result["year"]="19"+p[2]
    spans = content.find_all('span')
    if spans is not None:
        result["description"] = spans[0].string
        result["type"]=spans[5].string
        result["technique"]=spans[7].string
        formats = re.split(" x ", spans[9].string)
        if formats is not None and len(formats) > 1:
            result["height"]=formats[0]
            result["width"]=formats[1]
        else:
            result["format"]=spans[9].string
        result["support"] = spans[11].string
        if len(spans)>22:
            order = re.split(">", spans[22].string)
            if len(order)>2:
                result["order"] = re.split(">", spans[22].string)[-2]
            else:
                result["order"] = spans[22].string
            result["origin"] = spans[24].string
            result["observation"] = spans[34].string
        if len(spans)>36:
            result["indexation"] = [v.string for v in spans[36].find_all("a")]
    return result

def flush(tree):
    LOG.info("Writting")
    with open ("tree.json", "w") as data:
        json.dump(tree, data, indent=2)

def main():
    result={}
    for i in range(FIRST,LAST):
        LOG.info("Reading notice %d",i)
        result["53Fi"+str(i)] = read(i)
        if i % 25 is 0:
            flush(result)

if __name__ == "__main__":
    main()
