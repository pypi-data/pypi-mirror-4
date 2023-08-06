"""oslobysykkel

Provides a Python interface to ClearChannel's API at
http://smartbikeportal.clearchannel.no/public/mobapp/maq.asmx/

Required: Python 3.2 or later (maybe)
"""

import collections
import urllib.request, urllib.error, urllib.parse
from xml.dom.minidom import parseString
import html.parser

last_rack = 111

Rack = collections.namedtuple("Rack", "description latitude longitude online bikes locks")

def _get_stations(resource):
    url = "http://smartbikeportal.clearchannel.no/public/mobapp/maq.asmx/" + resource

    with urllib.request.urlopen(url) as f:
        data = f.read()

    dom = parseString(data)
    xml_string = dom.getElementsByTagName("string")[0].toxml()

    data = html.parser.HTMLParser().unescape(xml_string).replace("&", " og ")
    dom = parseString(data)
    dom_stations = dom.getElementsByTagName("station")

    return dom_stations

def get_racks():
    dom_stations = _get_stations("getRacks")

    return [int(s.firstChild.nodeValue) for s in dom_stations]

def get_rack(rack_id):
    dom_station = _get_stations("getRack?id=%d" % rack_id)[0]

    try:
        description = "-".join(dom_station.getElementsByTagName("description")[0].firstChild.nodeValue.split("-")[1:]).strip()
    except:
        description = None

    try:
        latitude = float(dom_station.getElementsByTagName("latitude")[0].firstChild.nodeValue)
    except:
        latitude = None

    try:
        longitude = float(dom_station.getElementsByTagName("longitute")[0].firstChild.nodeValue)
    except:
        longitude = None

    try:
        online = bool(dom_station.getElementsByTagName("online")[0].firstChild.nodeValue)
    except:
        online = None

    try:
        locks = int(dom_station.getElementsByTagName("empty_locks")[0].firstChild.nodeValue)
    except:
        locks = None

    try:
        bikes = int(dom_station.getElementsByTagName("ready_bikes")[0].firstChild.nodeValue)
    except:
        bikes = None

    return Rack(description, latitude, longitude, online, bikes, locks)

if __name__ == "__main__":
    for rack in get_racks():
        r = get_rack(rack)

        print("%3d\t%s" % (rack, get_rack(rack)))
