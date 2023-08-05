# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.util.Error import Error
from gizela.data.CoordSystemLocal import CoordSystemLocal


class ParseCentralPointError(Error):pass


def parse_central_point(cpoint):
    """
    parses central point latitude, longitude and height
    in degrees and meters
    numbers are separated by commas

    cpoint: string: latitude,longitude,height (height is optional)
    return: CoordSystemLocal instance 
    """

    cpoint = cpoint.split(",")

    if len(cpoint) < 2:
        raise ParseCentralPointError, "latitude and longitude not set: %s"%\
                cpoint

    if len(cpoint) > 3:
        raise ParseCentralPointError, "too namy numbers set: %s" % cpoint


    from gizela.util.Converter import Converter
    lat = Converter.deg2rad_(float(cpoint[0]))
    lon = Converter.deg2rad_(float(cpoint[1]))

    if len(cpoint) is 3:
        height = float(cpoint[2])
    else:
        height = 0.0

    #csl = CoordSystemLocal(
    return lat, lon, height
