#!/usr/bin/python

__author__ = 'mm'

# Mats Melander 2015-07-01
#
# Format of produced JSON
# Wind = {
#  Summary: "xxx"
#  Date: "2015-07-01"
#  List: [ {elem1}, {elem2}, ..., {elemN}] }
#
# elem = {
#  Speed: 10.0
#  Dir: 180
#  Station: "Arlanda"
#  Lat: 62.1
#  Lon: 15.6 }
#
# Accessed as Wind["List"][0]["Speed"]
#

import urllib2
import json as json
from datetime import date
import shutil


def get_data(par):
    d = date.today()
    Wind = {}
    Wind["Summary"] = "Wind data from SMHI Open data"
    Wind["Date"] = d.isoformat()
    Wind["List"] = []

    url = "http://opendata-download-metobs.smhi.se/api.json"  # Root for SMHI REST API
    lst = json.loads(urllib2.urlopen(url).read())

    ind1 = next(index for (index, d) in enumerate(lst["version"]) if d["key"] == "latest")
    ind2 = next(index for (index, d) in enumerate(lst["version"][ind1]["link"]) if d["type"] == "application/json")
    # Use latest version (not recommended by SMHI), read parameter list
    url = lst["version"][ind1]["link"][ind2]["href"]
    lst = json.loads(urllib2.urlopen(url).read())

    # Parameter 4 is wind speed, parameter 3 is wind direction
    wnd_ind = next(index for (index, d) in enumerate(lst["resource"]) if d["key"] == par)
    js_ind = next(index for (index, d) in enumerate(lst["resource"][wnd_ind]["link"]) if d["type"] == "application/json")
    url = lst["resource"][wnd_ind]["link"][js_ind]["href"]
    lst = json.loads(urllib2.urlopen(url).read())

    n = 0
    for i, stn in enumerate(lst["station"]):
        elem = {}
        js_ind = next(index for (index, d) in enumerate(stn["link"]) if d["type"] == "application/json")
        url = stn["link"][js_ind]["href"]
        lnk = json.loads(urllib2.urlopen(url).read())
        js_ind = next((index for (index, d) in enumerate(lnk["period"]) if d["key"] == "latest-day"), None)
        if js_ind is not None:
            lnk = lnk["period"][js_ind]
            lnk_ind = next(index for (index, d) in enumerate(lnk["link"]) if d["type"] == "application/json")
            url = lnk["link"][lnk_ind]["href"]
            lnk = json.loads(urllib2.urlopen(url).read())

            lnk_ind = next(index for (index, d) in enumerate(lnk["link"]) if d["type"] == "application/json")
            url = lnk["data"][0]["link"][lnk_ind]["href"]  # Note, no key for data, hence always 0
            lnk = json.loads(urllib2.urlopen(url).read())
            if lnk["value"] is not None:
                elem["Station"] = stn["name"]
                print "%d\r" % n,
                if par == "4":
                    elem["Speed"] = float(lnk["value"][0]["value"])
                else:
                    elem["Dir"] = int(lnk["value"][0]["value"])
                elem["Lon"] = stn["longitude"]
                elem["Lat"] = stn["latitude"]
                Wind["List"].append(elem)
                n += 1
    return Wind


def merge_lists(l1, l2):
    for i in range(len(l1["List"])):
        if l1["List"][i]["Lat"] == l2["List"][i]["Lat"] and l1["List"][i]["Lon"] == l2["List"][i]["Lon"]:
            l1["List"][i]["Dir"] = l2["List"][i]["Dir"]
        else:
            l1["List"][i]["Dir"] = 0
    return l1


def store(l):
    """
    Create a file such as "2015-07-07.js" with Javascript variable 'weather' based on JSON
    Copy the file to 'wind.js'
    :param l: JSON list
    :return: NA
    """

    import os
    import sys
    import time

    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    path = "../data/"
    name = path + l["Date"] + ".js"
    with open(name, 'w') as outfile:
        outfile.write("var weather = ")
        json.dump(l, outfile)
        outfile.write(";")
        outfile.close()
        shutil.copy(name, path + "wind.js")

    # Remove all files older than 7 days
    now = time.time()
    cutoff = now - (7 * 86400)

    files = os.listdir(path)
    for f in files:
        if os.path.isfile(path + f):
            t = os.stat(path + f)
            c = t.st_mtime  # Modification time
            if c < cutoff and f != "swe.json" and f != "wind.js":
                # Rename files to be removed by git with "OLD_"-prefix, this is managed in Swind.sh script
                os.rename(path + f, path + "OLD_" + f)
if __name__ == "__main__":
    print "Wind speeds"
    speeds = get_data("4")
    print "Wind directions"
    dirs = get_data("3")
    store(merge_lists(speeds, dirs))
    print "Done"
