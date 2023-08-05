# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$


class DUPLICATE_ID(object):
    """enumeration class for handlig points with same id
    """
    
    __slots__ = ["error", "hold", "overwrite"]

    error     = 0 # raise exception for duplicate point id
    hold      = 1 # hold old point 
    overwrite = 2 # owerwrite old point with the new one
    compare   = 3 # raise exception when coordinates are different

