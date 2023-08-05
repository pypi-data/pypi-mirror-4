# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: Unit.py 57 2010-07-22 18:01:42Z kubin $

from math import pi

class Unit:
    """
    scale factors for unit of observations in gama-local
    
    - gizela internal units RAD and meters
    - only gons for gama-local are handled

        observation | value | stdev/covmat
        ----------------------------------
        direction   | gon   | gon*1e-4
        z-angle     | gon   | gon*1e-4
        angle       | gon   | gon*1e-4
        distance    | m     | mm
        s-distance  | m     | mm
        dh          | m     | mm
        vec         | m     | mm
        coor        | m     | mm
        ----------------------------------
        tol-abs     | mm
        dh - dist   | km

    """
    
    angleVal   = 200.0 / pi        # gon
    angleStdev = 200.0 / pi * 1e4  # gon*1e-4 
    distStdev  = 1e3               # mm
    tolabs     = 1e3               # mm
    dhdist     = 1e-3              # km
