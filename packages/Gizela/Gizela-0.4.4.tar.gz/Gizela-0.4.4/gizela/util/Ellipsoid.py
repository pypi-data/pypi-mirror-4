# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Michal Seidl <michal.seidl@fsv.cvut.cz>
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: Ellipsoid.py 81 2010-10-30 20:42:11Z michal $

"""
Class Module Ellipsoid
"""

import math
from gizela.util.Error import Error

class EllipsoidError(Error):
    """
    Exception for class Ellipsoid
    """
    pass

class Ellipsoid(object):
    """
    Instance of Ellipsoid Class offers basic calculation on ellipsoid
    """
    
    ELLIPSOID = {
        'wgs84':  (6378137.0,     298.257223563, 'World Geodetic System 1984'),
        'WGS84':  (6378137.0,     298.257223563, 'World Geodetic System 1984'),
        'bessel': (6377397.15508, 299.15281282917516, 'Bessel ellipsoid 1841')
                     }
    def __init__(self, code="wgs84"):
        """
        
        @param code: Code of ellipsoid. Used to choose ellipsoid parameters. 
        @type code: string
        """

        """
        @ivar: Dictionary of supported ellipsoid
        @type: dictionary
        """ 

        if not code in self.ELLIPSOID:
            raise EllipsoidError, "Unknown ellipsoid \"%s\"" % code

        self._code = code #: code of ellipsoid 
        self._a = self.ELLIPSOID[code][0] #: major axis
        self._fInv = self.ELLIPSOID[code][1] #: inverse flattening
        self._desc = self.ELLIPSOID[code][2] #: description
        self._b = self._a - self._a / self._fInv #: minor axis
        self._firstEccen2 = ((self._a**2-self._b**2)/self._a**2) #: first eccentricity squared

    def get_W(self, lat):
        """
        Computes parametr W used in computation of curvature
        @param lat: Latitude
        @type lat: float
        @return: Parameter W
        @rtype: float
        """
        return (1-self._firstEccen2*math.sin(lat)**2)**0.5
        
    def get_M(self, lat):
        """
        Meridional curvature
        @param lat: Latitude
        @type lat: float
        @return: Meridional curvature
        @rtype: float
        """
        W = self.get_W(lat)
        return self._a*(1-self._firstEccen2)/W**3
    
    def get_N(self, lat):
        """
        Normal curvature
        @param lat: Latitude
        @type lat: float
        @return: Normal curvature
        @rtype: float
        """        
        return self._a/self.get_W(lat)
        
    def get_R(self, lat):
        """
        Gaussian curvature
        @param lat: Latitude
        @type lat: float
        @return: Gaussian curvature
        @rtype: float
        """
        return self._a*(1-self._firstEccen2)**0.5/(1-self._firstEccen2*(math.sin(lat)**2))
    
    def llh2xyz_ (self, lat, lon, height):
        """
        Converts ellipsoidal coordinates to cartesian
        @param lat: Latitude
        @type lat: float
        @param lon: Logitude
        @type lon: float
        @param height: Ellipsoidal height
        @type height: float
        @return: Geocentric cooridantes X,Y,Z
        @rtype: tuple
        """
        
        N = self.get_N(lat)
        x = (N+height)*math.cos(lat)*math.cos(lon)
        y = (N+height)*math.cos(lat)*math.sin(lon)
        z = (N*(1-self._firstEccen2)+height)*math.sin(lat)
        return (x, y, z)
    
    def xyz2llh_ (self, x, y, z):
        """
        Convert cartesian coordinates to ellipsoidal
        @param x: X
        @type x: float
        @param y: Y
        @type y: float
        @param z: X
        @type z: float
        @return: Returns Lat, Lon, Height, diffLat, IterNum)
        @rtype: tuple        
        """
        dif = 0.01e-3 #: accuracy of computed coordinates in meters
        difRad = dif/((self._a+self._b)/2) #: aproximate accuracy of computed coordinates in radians
        maxIter = 30
        
        # Loop computes latitude coordinate
        iterNum = 0 #: Inicialization of iterNum 
        difLat = 1 #: Inicialization of difLat
        latI = math.atan(z/((x**2+y**2)**0.5*(1-self._firstEccen2)))
        
        while (iterNum < maxIter and difLat > difRad):
            N = self.get_N(latI)
            latJ = math.atan((z+N*self._firstEccen2*math.sin(latI))/(x**2+y**2)**0.5)
            iterNum += 1
            difLat = math.fabs(latI-latJ)
            latI = latJ
            
#        if (difLat > difRad) :
#            raise Exception ("With 30 iteration difference is still too big")
            
        lon = math.atan2(y, x)
        N = self.get_N(latI)
        height = x/(math.cos(latI)*math.cos(lon))-N
        return (latI, lon, height)
        #return (latI, lon, height, difLat, iterNum)

    def get_code(self): return self._code
    
    def __str__(self):
        return "%s: %s" % (self._code, self._desc)

    def __eq__(self, other):
        if isinstance(other, Ellipsoid):
            return self._code == other._code
        elif type(other) is str or type(other) is unicode:
            return self._code == other
        elif other is None:
            return False
        else:
            raise EllipsoidError, "Unknown type of instance %s" % type(other)
            return False    

if __name__ == "__main__":
    """
    Main module doc
    """
    
    roGon = 200/math.pi
    roDeg = 180/math.pi
    print "This is Ellipsoid class instance"
    ellipsoid = Ellipsoid('bessel')
    print ellipsoid._code
    print ellipsoid._desc
    print ellipsoid._a
    print ellipsoid._b
    print ellipsoid._firstEccen2
    print ellipsoid._fInv
    print ellipsoid.get_M(50.1885/roDeg)
#    print ellipsoid.get_R(0.0/roGon)
#    print ellipsoid.get_R(25.0/roGon)
#    print ellipsoid.get_R(50.0/roGon)
#    print ellipsoid.get_R(75.0/roGon)
#    print ellipsoid.get_R(100.0/roGon)
#    print dir(ellipsoid)

#    llh = Object()
#    llh.lat = 50/roDeg
#    llh.lon = 14/roDeg
#    llh.height = 500
    lat = 50/roDeg
    lon = 14/roDeg
    height = 500 
    
    xyz = ellipsoid.llh2xyz_(lat, lon, height)
    print xyz
    
    llh = ellipsoid.xyz2llh_(xyz[0],xyz[1],xyz[2])
    print llh
    print [v*roDeg for v in llh[0:2]]

    el = Ellipsoid("wgs84")
    #el = Ellipsoid("wgs")
    print el == el
    print el == "wgs84"
    print el == "wgs"
