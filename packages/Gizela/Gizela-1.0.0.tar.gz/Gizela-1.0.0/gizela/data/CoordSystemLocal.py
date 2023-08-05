# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.util.Ellipsoid import Ellipsoid
from gizela.data.PointGeodetic import PointGeodetic
from gizela.data.PointCart import PointCart
from gizela.data.AxesOrientation import AxesOrientation


class CoordSystemLocal(AxesOrientation):
    """
    local coordinate system
    """

    def __init__(self,
                 ellipsoidCode="wgs84",
                 lat=0,
                 lon=0,
                 height=0,
                 x=0,
                 y=0,
                 z=0,
                 axesOri="ne",
                 bearingOri="right-handed",
                 name="not set",
                 description="",
                 proj4String=""):
        """
        ellipsoidCode: code of ellipsoid from gizela.util.Ellipsoid class
        lat, lon, height: latitude, longitude and ellipsoidal height of
                          central point of E3 local coordinate system
                          angles are in radians
        x, y, z: coordinates in E3 of central point
        axesOri: orientation of x and y axis
        bearingOri: orientation of bearings right-handed/left-handed
        name: short name of local system
        description: longer description of system
        projDict: dictionary of parameters for pyproj.Proj class
                  for transformation from global to local system
        """

        super(CoordSystemLocal, self).__init__(axesOri=axesOri,
                                               bearingOri=bearingOri)
        self.ellipsoid=Ellipsoid(ellipsoidCode)
        self.centralPointGeo=PointGeodetic(id="", lat=lat, lon=lon,
                                           height=height)
        self.centralPointLoc=PointCart(id="", x=x, y=y, z=z)
        self.name = name
        self.description = description
        self.proj4String = proj4String


    def get_tran_local_e3(self, inverse=False):
        """
        returns transformation from geocentric coordinate system XYZ
        to local E3 system xyz

        This transformation is computed from central point and orientation
        of axes
        """
        if self.axesOri == "ne":
            return self.get_tran_ne(inverse=inverse)
        else:
            return None # not implemented


    #def get_proj_local_e2(self, inverse=False): 
    def get_proj_local_e2(self): 
        """
        returns projection instance from geodetic coordinate system 
        lon, lat in degrees to local E2 system xy in meters

        This transformation is set from projDict dictionary of parameters 
        for pyproj.Proj projection

        Warning: parameters radians, errcheck and inverse do not work
        """
        from pyproj import Proj
        #self.projDict["radians"] = True
        #self.projDict["errcheck"] = True
        #self.projDict["inverse"] = inverse
        return Proj(self.proj4String)


    def get_tran_llh(self, inverse=False): 
        """
        returns transfomations from geocentric XYZ to 
        latitude, longitude and height on ellipsoid specified by
        ellipsoidCode attribute
        """
        if inverse:
            return self.ellipsoid.llh2xyz_
        else:
            return  self.ellipsoid.xyz2llh_


    def get_tran_ne(self, inverse=False):
        """
        returns transformation from xyz geocetric system to local system
        
        local system is set: x - geodetic north
                             y - east
                             z - ellipsoidal normal
                             origin - self.centralPointGeo 
                                    - latitude, longitude and height
                                      on self.ellipsoid

        Warning: translations not implemented !!!!
        """

        from gizela.tran.Tran3D import Tran3D

        tran = Tran3D()
        
        from math import pi
        
        tran.rotation_xyz(alpha=0.0, 
                          beta=(self.centralPointGeo.lat - pi/2),
                          gamma=(self.centralPointGeo.lon - pi))
        tran.mirror_y()
        
        if inverse:
            tran.set_inverse()

        return tran


    def __str__(self):
        str = ["Name: %s" % self.name]
        str.append(super(CoordSystemLocal, self).__str__())
        str.append("Ellipsoid: %s" % self.ellipsoid)
        str.append("Central point geographic:%s" % self.centralPointGeo)
        str.append("Central point local:%s" % self.centralPointLoc)
        str.append("Description:%s" % self.description)
        str.append("Proj4String:%s" % self.proj4String)

        return "\n".join(str)

    def set_central_point_geo(lat, lon, height):
        self.centralPointGeo=PointGeodetic(id="", lat=lat, lon=lon,
                                           height=height)

    def set_central_point_loc(x, y, z):
        self.centralPointLoc=PointCart(id="", x=x, y=y, z=z)


    def proj_xy(self, pointCart):

        lat, lon, height = self.get_tran_llh()(pointCart.x, pointCart.y,
                                               pointCart.z)

        from gizela.util.Converter import Converter
        proj = self.get_proj_local_e2()
        import sys
        #print >>sys.stderr, proj.srs
        #print >>sys.stderr, Converter.rad2deg_(lon)
        #print >>sys.stderr, Converter.rad2deg_(lat)
        y, x = self.get_proj_local_e2()(Converter.rad2deg_(lon),
                                        Converter.rad2deg_(lat))
        #print >>sys.stderr, x, y
        pointCart.x = x
        pointCart.y = y
        pointCart.z = None


if __name__ == "__main__":

    cs = CoordSystemLocal(name="system 1", ellipsoidCode="wgs84", 
                          lat=1, lon=2, height=250, axesOri="ne",
                          bearingOri="right-handed",
                          proj4String="+proj=lcc +ellps=WGS84 +lat_1=50.09")

    print cs
    x, y, z = cs.get_tran_local_e3()(1,1,1)
    print x, y, z
    print cs.get_tran_local_e3(inverse=True)(x,y,z)

    lat, lon, height, i, ii = cs.get_tran_llh()(1,1,1)
    print lat, lon, height
    print cs.get_tran_llh(inverse=True)(lat, lon, height)

    from math import pi
    p = cs.get_proj_local_e2()
    print p.srs
    x, y = p(1, 1)
    print x, y
