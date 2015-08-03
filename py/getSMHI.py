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

def getData(par):
    d = date.today()
    Wind = {}
    Wind["Summary"] = "Wind data from SMHI Open data"
    Wind["Date"] = d.isoformat()
    Wind["List"] = []

    url = "http://opendata-download-metobs.smhi.se/api.json"  # Root for SMHI REST API
    lst = json.loads(urllib2.urlopen(url).read())

    ind1 = next(index for (index, d) in enumerate(lst["version"]) if d["key"] == "latest")
    ind2 = next(index for (index, d) in enumerate(lst["version"][ind1]["link"]) if d["type"] == "application/json")
    url = lst["version"][ind1]["link"][ind2]["href"]  # Use latest version (not recommended by SMHI), read parameter list
    lst = json.loads(urllib2.urlopen(url).read())

    # Parameter 4 is wind speed, parameter 3 is wind direction
    WndInd = next(index for (index, d) in enumerate(lst["resource"]) if d["key"] == par)
    JSInd = next(index for (index, d) in enumerate(lst["resource"][WndInd]["link"]) if d["type"] == "application/json")
    url = lst["resource"][WndInd]["link"][JSInd]["href"]
    lst = json.loads(urllib2.urlopen(url).read())

    n = 0
    for i, stn in enumerate(lst["station"]):
        elem = {}
        JSInd = next(index for (index, d) in enumerate(stn["link"]) if d["type"] == "application/json")
        url = stn["link"][JSInd]["href"]
        lnk = json.loads(urllib2.urlopen(url).read())
        JSInd = next((index for (index, d) in enumerate(lnk["period"]) if d["key"] == "latest-day"), None)
        if JSInd is not None:
            lnk = lnk["period"][JSInd]
            lnkInd = next(index for (index, d) in enumerate(lnk["link"]) if d["type"] == "application/json")
            url = lnk["link"][lnkInd]["href"]
            lnk = json.loads(urllib2.urlopen(url).read())

            lnkInd = next(index for (index, d) in enumerate(lnk["link"]) if d["type"] == "application/json")
            url = lnk["data"][0]["link"][lnkInd]["href"]  # Note, no key for data, hence always 0
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
            else:
                val = "None"
                #print stn["name"] + " (" + str(n) + ":" + str(i) + ") : " + val
    return Wind

def mergeLists(l1, l2):
    for i in range(len(l1["List"])):
        if l1["List"][i]["Lat"] == l2["List"][i]["Lat"] and \
           l1["List"][i]["Lon"] == l2["List"][i]["Lon"]:
             l1["List"][i]["Dir"] = l2["List"][i]["Dir"]
        else:
             return []
    return l1

def store(l):
    """
    Create a file such as "2015-07-07.js" with Javascript variable 'weather' based on JSON
    Copy the file to 'wind.js'
    :param l: JSON list
    :return: NA
    """

    import os, sys, time
    from subprocess import call

    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    path = "../data/"
    old = path + "old/"
    name = path + l["Date"] + ".js"
    with open(name, 'w') as outfile:
        outfile.write("var weather = ")
        json.dump(l, outfile)
        outfile.write(";")
        outfile.close()
        shutil.copy(name, path + "wind.js")

    # Move all files older than 7 days to old-folder
    now = time.time()
    cutoff = now - (7 * 86400)

    if not os.path.exists(old):
        os.makedirs(old) # Create old-folder if it doesn't exist

    files = os.listdir(path)
    for f in files:
        if os.path.isfile(path + f):
            t = os.stat(path + f)
            c = t.st_mtime # Modification time
            if c < cutoff and f != "swe.json" and f != "wind.js":
                os.rename(path + f, path + "OLD_" + f) # Rename files tobe removed by git with "OLD_"-prefix, this is managed in Swind.sh script

if __name__ == "__main__":
   print "Wind speeds"
   speeds = getData("4")
   print "Wind directions"
   dirs = getData("3")
   store(mergeLists(speeds, dirs))
   print "Done"



