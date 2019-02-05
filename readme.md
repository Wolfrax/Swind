# Wind map for Sweden

[Based on open data by SMHI](http://opendata.smhi.se/) 

[My website for rendering Swind](http://www.viltstigen.se/Swind/index.html)

This wind map for Sweden is an exercise using [D3](http://d3js.org) and [REST](https://en.wikipedia.org/wiki/Representational_state_transfer).
It is modelled after from Peter Cook's [UK Wind Map](http://prcweb.co.uk/lab/ukwind/) and loosely inspired from [Wind](http://hint.fm/wind/).

In short, there is a python script (`getSMHI.py`) that traverse the SMHI REST API and download wind speeds and directions from 'SMHI latest day' data.
This data is rendered through D3 on a SVG map of Sweden. Min, max and average wind speed is calculated as well as average wind direction (in degrees).

Details as follows.

## Python
The Pythons script `getSMHI.py` is located in the directory `py` and is using the documentation available on this 
link http://opendata.smhi.se/apidocs/metobs/
The entry point is hard coded in the python script as is the parameter values for wind speed (4) and wind direction (3).
Data is downloaded in JSON, so the 2 JSON structures is combined into one common JSON structure and saved as a file with 
the date of execution of the script
, for example `2015-07-13.js`. 
The file is then copied to `wind.js`, so this file always contain the latest data. The data in this file is accessible
through the variable `weather`.

The JSON files are stored in the `data` directory, parallel to the `py` directory. Files older than 7 days are removed.

**Note** codes are hardcoded and there is no error checking in the script. Not my proudest script obviously...

### Specifics
In my case, the Python script is executed once per day on my Raspberry Pi. I have added the following line in `etc/crontab`
    
    00 7 * * * pi python /home/pi/app/Swind/py/getSMHI.py

Remember `$ sudo chmod g+x -R getSMHI.py` and `$ sudo chmod a+w /var/log/Swind.log`

I changed the ownership of the /var/www/ directory from root to Pi through `sudo chown -R pi /var/www/`.

If the system time (use `date` at the Raspberry command prompt) is configured to the wrong timezone, us the following 
command `sudo dpkg-reconfigure tzdata` to correct.

To enable git push to GitHub repository, SSH needs to be configured, refer to these GitHub pages:

1. [Generating SSH keys](https://help.github.com/articles/generating-ssh-keys/)
2. [Changing a remote URL](https://help.github.com/articles/changing-a-remote-s-url/)

## SVG map of Sweden
This was easily done by following [Let's make a map](http://bost.ocks.org/mike/map/) by Mike Bostock, the person behind D3.
The shape files and resulting JSON files (the end result is `swe.json`) is located in the `map` directory.
I modified the instructions by Mike Bostocks as follows. 

The first command will convert the [shape file](https://en.wikipedia.org/wiki/Shapefile) 
to [GeoJSON](http://geojson.org/) format, the output file being `subunits.json` and `places.json` while 
`ne_10m_admin_1_states_provinces.shp` and `ne_10m_populated_places.shp` is the input file.

    ogr2ogr -f GeoJSON -where "ADM0_A3 = 'SWE'" subunits.json ne_10m_admin_1_states_provinces.shp
    ogr2ogr -f GeoJSON -where "ISO_A2 = 'SE' AND SCALERANK <8" places.json ne_10m_populated_places.shp

Rewrite, not county's...
    $ topojson -o se.json --properties name=NAME -- subunits.json

This is of course to include Sweden 
(SWE [ISO 3166-1 alpha-3 3 letter code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) and 
SE [ISO 3166-1 alpha-2 2 letter code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)) 
from the shp-file using the `-where` condition.

Then convert from GeoJSON format to TopoJSON (see Wikipedia article on GeoJSON) format using below, 
that combines `subunits.json` and `places.json` into one output file `swe.json`

    topojson -o swe.json --id-property postal --properties name=NAME -- subunits.json places.json

Here I wanted to include the `postal` property in the resulting JSON file (`swe.json`), although it turned out I didn't 
need it in the end. Originally I wanted to have different colors for each county in Sweden but it turned out nicer
to have one color instead.

## Animation of Wind speed and direction
`ìndex.html` includes all logic to generate the wind map. 
Specifically it includes a D3 mercator project of Sweden

    var projection = d3.geo.mercator()
        .center([14.6, 62.1])  // Somewhere in the middle of Sweden, https://sv.wikipedia.org/wiki/Sveriges_geografiska_mittpunkt
        .scale(1000)
        .translate([width / 2, height / 2]);
    var path = d3.geo.path()
        .projection(projection);

The function `wind_vector` takes the current wind speed and wind direction data and scales a line proportionally. 
It includes other information, such as delay and duration for animation. 
The lines are projected for the map and stored in the array `vectors`.

Finally the D3 library is used to render the wind map, refer to the javascript (commented) in `index.html` for details.
In the process the `swe.json` file is read, the map of Sweden is rendered and then the wind vectors is animated.
The average wind speed and direction is drawn in a circle, scaled by the wind max speed.
Some text are rendered.

## Links

Some nice links

* [Mike Bostocks blog](http://bost.ocks.org/mike/)
* [Home page Jason Dvies](https://www.jasondavies.com/)
* [D3 wiki](https://github.com/mbostock/d3/wiki/Tutorials)
* [topojson wiki](https://github.com/mbostock/topojson/wiki)

## Creating a virtual environment

Using Python3, pipenv and PyCharm.

On raspberry

    $ pip install --user pipenv

Then update .bashrc with

    export PATH=$PATH:/opt/mongo/bin/:/home/pi/.local/bin

Then do (to take effect of the new PATH)

    $ source .bashrc
    

For local (Mac) installation in PyCharm, go PyCharm/Preferences... and find Project Interpreter dialog.
Press preferences icon (small wheel, upper right corner) and use add... In the following dialog use pipenv and follow
the instructions. Add requests. Now use this environment when running locally, switch to remote environment when running
on raspberry. See installation details for this environment.



