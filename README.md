AstroTargets
============

This repo contains a python script to create EQTOUR and Google Calendar files for monthly lists of astro targets. 

To use the script: 

Using conda or virtualenv, create a python virtualenv named `astrotargets`, activate it and install the `pyongc`, `astroquery` and `astropy` python libraries listed in `requirements.txt`

Create a text file containing a list of object names. The names can be Messier, IC, NGC Caldwell, HCG, PCG, Abell or common names such as Algol, Rho Ophiuchi etc. For example you might create a file `galaxies.txt` containing a list of interesting galaxies:
``` bash
M81
M101
M31
NGC2749
Abell 30
Stephan's quintet
HCG 10
```

In a cmd, powershell or terminal window, activate the python virtualenv and run the script:

```bash
python ./getTargetDets.py galaxies.txt 20240101 20240130
```

The dates are optional, but if you specify these, then an `ical` compatible file will  be created as well as an EQTOUR file.

If you specify an object that can't be identified by the programme, it will emit a warning and skip over that row. You can identify the problem row by reading the error message. Often its just a spelling mistake or missing apostrophe. 

## output Files
Two files can be created, one ending in `_tour.lst` and one ending in `.ics`. For example:

* `galaxies_tour.lst` is an EQTOUR compatible listing file you can copy to your EQTOUR folder and use to drive your EQMOD compatible mount.

* `galaxies_cal.ics` optionally created only if start/end dates are specified. This  is an icalendar file suitable for import into Google Calendar or other calendar apps. 

This repository contains a number of examples. 