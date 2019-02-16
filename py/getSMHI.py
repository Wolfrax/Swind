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
#  Temp: 1.9
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
import datetime
import shutil


def get_data(par):
    d = date.today() - datetime.timedelta(1)  # Yesterdays date as we are gathering data from yesterday (latest-day)
    Wind = {}
    Wind["Summary"] = "Wind data from SMHI Open data"
    Wind["Date"] = d.isoformat()
    Wind["List"] = []

    url = "http://opendata-download-metobs.smhi.se/api.json"  # Root for SMHI REST API
    lst = json.loads(urllib2.urlopen(url).read())

    # The "next("... construct is used several times below to keep the code short
    # It is equivalent to:
    # for (index, d) in enumerate(lst["version"]):
    #    if d["key"] == "latest":
    #        i = index

    ind1 = next(index for (index, d) in enumerate(lst["version"]) if d["key"] == "latest")
    ind2 = next(index for (index, d) in enumerate(lst["version"][ind1]["link"]) if d["type"] == "application/json")
    # Use latest version (not recommended by SMHI), read parameter list
    url = lst["version"][ind1]["link"][ind2]["href"]
    lst = json.loads(urllib2.urlopen(url).read())

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
                elif par == "1":
                    elem["Temp"] = float(lnk["value"][0]["value"])
                elif par == "3":
                    elem["Dir"] = int(lnk["value"][0]["value"])
                else:
                    print "Wrong par value: %s", par

                elem["Lon"] = stn["longitude"]
                elem["Lat"] = stn["latitude"]
                Wind["List"].append(elem)
                n += 1
    return Wind


def find_station(name, lst):
    for ind, elem in enumerate(lst):
        if elem["Station"] == name:
            return ind
    return None


def merge_lists(l1, l2, par):
    # NB We are trying to find a station name at l1 in l2, if not found we set the value to 0 below
    # E.g. if we from previously have the station "Uppsala" in l1 but not in l2  we
    # set the the rain-value for Uppsala to zero in the l1-list.

    for i in range(len(l1["List"])):
        ind = find_station(l1["List"][i]["Station"], l2["List"])
        if ind is not None:
            l1["List"][i][par] = l2["List"][ind][par]
        else:
            l1["List"][i][par] = 0

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
            if c < cutoff and f != "se.json" and f != "swe.json" and f != "wind.js":
                # Rename files to be removed by git with "OLD_"-prefix, this is managed in Swind.sh script
                os.rename(path + f, path + "OLD_" + f)


# List of parameters (not extensive) that can be downloaded
# '1',  air temp, momentary value, 1/hour
# '2',  average temp for 1 day (24 h), at 00:00
# '3',  wind direction, average value 10 min, 1/hour
# '4',  wind speed, average value 10 min, 1/hour
# '6',  relative moisture, momentary value, 1/hour
# '8',  snow depth, momentary value, 1/hour
# '9',  air pressure, at sea level, momentary value, 1/hour
# '18', rain, 1/day, at 18:00
# '28', lowest cloud layer, momentary value, 1/hour

if __name__ == "__main__":
    print "Wind speeds"
    speeds = get_data("4")
    print "Wind directions"
    dirs = get_data("3")
    lst = merge_lists(speeds, dirs, "Dir")
    print "Temperatures"
    temps = get_data("1")
    lst = merge_lists(lst, temps, "Temp")
    store(lst)
    print "Done"
