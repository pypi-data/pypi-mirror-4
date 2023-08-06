# -*- coding: utf8 -*-
"""oslobysykkel

Provides a Python interface to ClearChannel's "API" at
http://www.bysykler.no/oslo/kart-over-sykkelstativer

Required: Maybe Python 2.6, 3.2 or later
"""

import collections

import lxml.html

Rack = collections.namedtuple("Rack", "number description latitude longitude online bikes locks")

def get_rack(rack_id):
    for r in get_racks():
        if r.number == rack_id:
            return r

def get_racks():
    url = "http://www.bysykler.no/oslo/kart-over-sykkelstativer"

    doc = lxml.html.parse(url)

    racks = map(parse_rack, doc.findall(".//div[@class='mapMarker']"))

    return racks

def parse_rack(r):
    lat = float(r.attrib["data-poslat"])
    lng = float(r.attrib["data-poslng"])

    htm = r.attrib["data-content"]
    doc = lxml.html.fromstring(htm)

    ps = doc.findall("p")

    try:
        words = ps[0].findall("strong")[0].text.split("-")

        number = int(words[0])
        name = "-".join(words[1:])

        bikes = int(ps[1].text.split("kler:")[1])
        locks = int(ps[2].text.split("ser:")[1])

        return Rack(number, name, lat, lng, False, bikes, locks)
    except:
        words = ps[0].text.split("-")

        number = int(words[0])
        name = "-".join(words[1:])

        return Rack(number, name, lat, lng, False, 0, 0)

    raise ValueError("cannot parse \"%s\"" % htm)

if __name__ == "__main__":
    for r in get_racks():
        print(r)
