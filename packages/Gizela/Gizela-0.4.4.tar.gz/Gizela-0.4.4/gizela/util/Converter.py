# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Michal Seidl <michal.seidl@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: Converter.py 66 2010-08-03 11:55:06Z michal $

"""
Class Module Converter
"""

import math
from gizela.util.Error import Error

class ConverterError(Error):
    """
    Exception for class Converter
    """
    pass

class Converter:
    """
    Class Converter offers static methods for basic unit conversion
    """

    @staticmethod
    def deg2rad_(deg): return deg/180*math.pi
    """
    Converts decimal degrees to radians
    @param deg: Decimal degree
    @type deg: float
    @return: Radian
    @rtype: float
    """
    
    @staticmethod
    def rad2deg_(rad): return rad/math.pi*180
    """
    Converts radians to decimal degrees
    @param deg: Radian
    @type deg: float
    @return: Decimal degree
    @rtype: float
    """
        
    @staticmethod
    def gon2rad_(gon): return gon/200*math.pi
    """
    Converts gons (gradians) to radians
    @param deg: Gon
    @type deg: float
    @return: Radian
    @rtype: float
    """
        
    @staticmethod
    def rad2gon_(rad): return rad/math.pi*200
    """
    Converts radians to gons
    @param deg: Radian
    @type deg: float
    @return: Gon
    @rtype: float
    """
    
if __name__=="__main__":
    """
    Main module doc
    """
    print "This is Converter class instance"
    converter=Converter()
    print dir(converter)
