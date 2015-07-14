# Wind map for Sweden

[Based on open data by SMHI.] (http://opendata.smhi.se/)

This wind map for Sweden is an exercise using [D3] (http://d3js.org) and [REST] (https://en.wikipedia.org/wiki/Representational_state_transfer).
It is modelled after from Peter Cook's [UK Wind Map] (http://prcweb.co.uk/lab/ukwind/) and loosely inspired from [Wind] (http://hint.fm/wind/).

In short, there is a python script `(getSMHI.py) that traverse the SMHI REST API and download wind speeds and directions from 'SMHI latest day' data.
This data is rendered through D3 on a SVG map of Sweden. Min, max and average wind speed is calculated as well as average wind direction (in degrees).

More details follows.

## Python
The Pythons script `getSMHI.py` is located in the directory `py` and is using the documentation available on this 
link http://opendata.smhi.se/apidocs/metobs/
The entry point is hard coded in the python script as is the parameter values for wind speed (4) and wind direction (3).
Data is downloaded in JSON, so the 2 JSON structures is combined into one common JSON structure and saved as a file with 
the date of execution of the script
, for example `2015-07-13.js`. 
The file is then copied to `wind.js`, so this file always contain the latest data. The data in this file is accessible
through the variable `weather`.

The JSON files are stored in the `data` directory, parallel to the `py` directory.

### Specifics
In my case, the Python script is executed once per day on my Raspberry Pi. I have added the following line in `etc/crontab`
    
    00 10 * * * root python /var/www/py/getSMHI.py

Remember `sudo chmod g+x -R getSMHI.py`

I changed the ownership of the /var/www/ directory from root to Pi 
through `sudo chown -R pi /var/www/`.
I found out that the system time (use `date` at the Raspberry command prompt) was configured to the wrong timezone, thus 
I issued the following command `sudo dpkg-reconfigure tzdata`.

## SVG map of Sweden
This was easily done by following [Let's make a map] (http://bost.ocks.org/mike/map/) by Mike Bostock, the person behind D3.
The shape files and resulting JSON files (the end result is `swe.json`) is located in the `map` directory.
I modified the instructions by Mike Bostocks as follows

    ogr2ogr -f GeoJSON -where "ISO_A2 = 'SE' AND SCALERANK <8" places.json ne_10m_populated_places.shp

This is of course to include Sweden (SE) from the shp-file.

    topojson -o swe.json --id-property postal --properties name=NAME -- subunits.json places.json

Here I wanted to include the `postal` property in the resulting JSON file (`swe.json`), although it turned out I didn't 
need it in the end. Originally I wanted to have different colors for each county in Sweden but it turned out nicer
to have one color instead.

## Animation of Wind speed and direction
`ìndex.html` includes all logic to generate the wind map. 
Specifically it includes a D3 project of Sweden

    var projection = d3.geo.albers()
        .center([14.4, 62.0])
        .rotate([0, 0])
        .parallels([50, 60])
        .scale(1000 * 2.1)
        .translate([width / 2, height / 2.7]);
    var path = d3.geo.path()
        .projection(projection);

The function `init` takes the wind speed and wind direction data and scales a line proportionally. It includes other
information, such as delay and duration for animation. The lines are projected for the map and stored in the array 
`lines`.

Finally the D3 library is used to render the wind map

    svg.selectAll(".subunit")
         .data(topojson.feature(swe, swe.objects.subunits).features)
       .enter().append("path")
         .attr("class", "subunit")
         .attr("d", path)

Below shows the major cities in Sweden as dots on the map without labels

    svg.append("path")
       .datum(topojson.feature(swe, swe.objects.places))
       .attr("d", path)
       .attr("class", "place");

Shows the county borders

    svg.append("path")
      .datum(topojson.mesh(swe, swe.objects.subunits, function(a, b) { return a !== b; }))
      .attr("d", path)
      .attr("class", "subunit-boundary");

Finally render the lines

    svg.selectAll("line")
      .data(lines)
      .enter()
      .append("line")
      .attr({
        x1: function(d) {return d.x0},
        y1: function(d) {return d.y0}
      })
      .call(lineAnimate);

## Links

Some nice links

* [Mike Bostocks blog] (http://bost.ocks.org/mike/)
* [Home page Jason Dvies] (https://www.jasondavies.com/)
* [D3 wiki] (https://github.com/mbostock/d3/wiki/Tutorials)
* [topojson wiki] (https://github.com/mbostock/topojson/wiki)

