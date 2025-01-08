# python to create a table of objects of interest

import sys
import os
from pyongc import ongc
from astroquery.simbad import Simbad
from astropy.coordinates import get_constellation, FK5
from astropy import units as u
import numpy as np
from ics import Calendar, Event
import pytz
import datetime


def createIcsFile(vals, startdt, enddt, fname):
    calendar = Calendar()
    gmt = pytz.timezone('Europe/London')
    event = Event()
    event.name = f'{os.path.split(os.path.splitext(fname)[0])[-1]} objects'
    event.begin = gmt.localize(datetime.datetime.strptime(startdt, '%Y%m%d'))
    event.end = gmt.localize(datetime.datetime.strptime(enddt, '%Y%m%d'))
    event.created = pytz.utc.localize(datetime.datetime.now())
    desc = ''
    for nam in vals:
        obj = vals[nam]
        mag = obj['mag']
        if obj['ra'] == 'Not Found':
            continue
        if mag == 'None':
            desc = desc + f"{obj['name']} - {obj['type']} in {obj['constellation']}\n"
        else:
            desc = desc + f"{obj['name']} - mag {mag} {obj['type']} in {obj['constellation']}\n"
    event.description = desc
    calendar.events.add(event)
    with open(f'{fname}.ics', 'w', encoding='utf-8', newline='\n') as ics_file:
        ics_file.writelines(calendar)
    # add recurrence flag - not handled by the ics library
    flines = open(f'{fname}.ics', 'r').readlines()
    with open(f'{fname}.ics', 'w') as ics_file:
        for li in flines:
            ics_file.write(li)
            if 'BEGIN:' in li:
                ics_file.write('RRULE:FREQ=YEARLY\n')
    return 


def strToDec(val):
    spls = val.split()
    decval = float(spls[0]) 
    if decval < 0:
        sign = -1
    else:
        sign = 1
    if len(spls)> 1:
        decval += float(spls[1])/60*sign
    if len(spls)> 2:
        decval += float(spls[2])/3600*sign
    return decval


def getSimbadData(name):
    Simbad.add_votable_fields('flux(B)','flux(V)', 'otype')
    try:
        obj = Simbad.query_object(name)
        ra = obj['RA'].value.data[0]
        dec = obj['DEC'].value.data[0]
        mag = obj['FLUX_V'].value.data[0]
        typ = obj['OTYPE'].value.data[0]
        rah = strToDec(ra)
        decd = strToDec(dec)
        c = FK5(rah * u.hour, decd * u.deg)
        constell = get_constellation(c, short_name=True)
        if np.isnan(mag):
            mag = obj['FLUX_B'].value.data[0]
            if np.isnan(mag):
                mag = None
        return {'name':name, 'ra':f'{rah:0.4f}', 'dec':f'{decd:0.4f}', 'mag':str(mag), 'constellation':str(constell),'type':str(typ)}
    except TypeError:
        rah = 0
        decd = 0
        mag = 0
        constell = 'None'
        typ = 'None'
        return {'name':name, 'ra':'Not Found', 'dec':'0', 'mag':'0', 'constellation':'None','type':'None'}


def getFromONGC(name):
    obj=ongc.get(name)
    if not obj:
        return getSimbadData(name)
    else:
        ra = f'{obj.coords[0][0]:.0f} {obj.coords[0][1]:.0f} {round(obj.coords[0][2],1)}'
        dec = f'{obj.coords[1][0]:.0f} {obj.coords[1][1]:.0f} {round(obj.coords[1][2],1)}'
        constell = obj.constellation
        typ = obj.type
        mag = obj.magnitudes[1]
        if mag is None:
            mag = obj.magnitudes[0]
        rah = strToDec(ra)
        decd = strToDec(dec)
    return {'name':name, 'ra':f'{rah:0.4f}', 'dec':f'{decd:0.4f}', 'mag':str(mag), 'constellation':str(constell),'type':str(typ)}


def toEQtour(vals, fname):
    return 


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python getTargetDets.py objname|filename')
    else:
        infname = sys.argv[1]
        if os.path.isfile(infname):
            objlist = open(infname, 'r').readlines()
        else:
            objlist = [infname]
        vals = {}
        for obj in objlist:
            vals[obj.strip()] = getFromONGC(obj.strip())
        print(vals)
        if len(vals) > 1:
            outfname = f'{os.path.splitext(infname)[0]}_tour.lst'
            with open(outfname, 'w') as outf:
                outf.write(f'# Objects of interest - {os.path.splitext(infname)[0]}\n\n')
                outf.write('!FORMAT=R;D;M;C;O;;\n')
                for nam in vals:
                    obj = vals[nam]
                    mag = obj['mag']
                    if mag == 'None':
                        mag = 99
                    if obj['ra'] == 'Not Found':
                        continue
                    outf.write(f"{obj['ra']};{obj['dec']};{mag};{obj['constellation']};{obj['name']};{obj['type']}\n")
        if len(sys.argv) == 4 and len(vals) > 0:
            createIcsFile(vals, sys.argv[2], sys.argv[3], os.path.splitext(infname)[0])
