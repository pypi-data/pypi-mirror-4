# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.util.CoordSystemGlobal import CoordSystemGlobal
from gizela.util.AxesOrientation import AxesOrientation

from gizela.data.PointGeodetic import PointGeodetic
from gizela.data.PointCart import PointCart
from gizela.util.Error import Error


class CoordSystemLocal3DError(Error): pass



class CoordSystemLocal3D(CoordSystemGlobal, AxesOrientation):
    """
    local coordinate system E3
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
                 name="",
                 description=""):
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
        """

        AxesOrientation.__init__(self, axesOri=axesOri,
                                       bearingOri=bearingOri)
        CoordSystemGlobal.__init__(self, ellipsoidCode=ellipsoidCode,
                                   name=name, description=description)

        self.centralPointGeo=PointGeodetic(id="", lat=lat, lon=lon,
                                           height=height)
        self.centralPointLoc=PointCart(id="", x=x, y=y, z=z)


    def __eq__(self, other):
        if isinstance(other, CoordSystemLocal3D):
            if self.ellipsoidCode == other.ellipsoidCode \
               and self.lat == other.lat \
               and self.lon == other.lon \
               and self.height == other.height \
               and self.x == other.x \
               and self.y == other.y \
               and self.z == other.z \
               and self.axesOri == other.axesOri \
               and self.bearingOri == other.bearingOri: 
                return True
        return False


    def get_tran_to_local_xyz2xyz(self, inverse=False):
        """
        returns transformation from geocentric coordinate system XYZ
        to local E3 system xyz
        """
        tran = self.get_tran_to_local_dxyz2dxyz(inverse=inverse)
        if inverse:
            raise NotImplementedError, "Inverse transformation not implemented"
        else:
            cpc = self.centralPointGeo.get_point_cart(self.ellipsoid)
            tran.translation_xyz(tx=cpc.x, ty=cpc.y, tz=cpc.z)

        return tran
        

    def get_tran_to_local_dxyz2dxyz(self, inverse=False):
        """
        returns transformation from geocentric coordinate system 
        to local E3 system for coordinate differences
        """
        
        from math import pi
        
        mirror_x, mirror_y = False, False
        alpha, beta, gamma = 0.0, 0.0, 0.0
        
        if self.axesOri == "ne":
            alpha=0.0 
            beta=(self.centralPointGeo.lat - pi/2)
            gamma=(self.centralPointGeo.lon - pi)
            mirror_y = True
        else:
            raise NotImplementedError, "Not implemented"

        from gizela.tran.Tran3D import Tran3D
        tran = Tran3D()
        tran.rotation_xyz(alpha, beta, gamma)

        if mirror_x:
            tran.mirror_x()

        if mirror_y:
            tran.mirror_y()
        
        if inverse:
            tran.set_inverse()

        return tran


    def get_tran_to_local_llh2xyz(self, inverse=False):
        raise NotImplementedError, "Not implemented"


    def _get_tran_ne_diff(self, inverse=False):
        """
        returns transformation from geocetric system to local system
        for coordinate differences
        
        local system is set: x - north
                             y - east
                             z - ellipsoidal normal
                             origin - self.centralPointGeo 
                                    - latitude, longitude and height
                                      on self.ellipsoid
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

    def _get_tran_ne(self, inverse=False):
        tran = self._get_tran_ne_diff(inverse=inverse)
        if inverse:
            raise NotImplementedError, "Inverse transformation not implemented"
        else:
            cpc = self.centralPointGeo.get_point_cart(self.ellipsoid)
            tran.translation_xyz(tx=cpc.x, ty=cpc.y, tz=cpc.z)

        return tran


    def __str__(self):
        str = ["Name: %s" % self.name]
        str.append(AxesOrientation.__str__(self))
        str.append("Ellipsoid: %s" % self.ellipsoid)
        str.append("Central point geographic:%s" % self.centralPointGeo)
        str.append("Central point local:%s" % self.centralPointLoc)
        str.append("Description:%s" % self.description)

        return "\n".join(str)

    def set_central_point_geo(lat, lon, height):
        self.centralPointGeo=PointGeodetic(id="", lat=lat, lon=lon,
                                           height=height)

    def set_central_point_loc(x, y, z):
        self.centralPointLoc=PointCart(id="", x=x, y=y, z=z)

    def parse_config_dict(self, dict):
        """
        sets self with values from dict
        """

        # set 
        try:
            self.set_ellipsoid(dict["localSystem3D"]["ellipsoid"])
        except Exception, e:
            import sys
            print >>sys.stderr, e
            raise CoordSystemLocal3DError, "parameter ellipsoid not set"

        from gizela.util.Converter import Converter

        try:
            #import sys
            #print >>sys.stderr, dict
            self.centralPointGeo.lat = \
                Converter.deg2rad_(float(dict["localSystem3D"]["latitude"]))
        except:
            raise CoordSystemLocal3DError, "parameter latitude not set"

        try:
            self.centralPointGeo.lon = \
                Converter.deg2rad_(float(dict["localSystem3D"]["longitude"]))
        except:
            raise CoordSystemLocal3DError, "parameter longitude not set"

        try:
            self.centralPointGeo.height = float(dict["localSystem3D"]["height"])
        except:
            raise CoordSystemLocal3DError, "parameter height not set"

        try:
            self.centralPointLoc.x = float(dict["localSystem3D"]["x"])
        except:
            raise CoordSystemLocal3DError, "parameter x not set"

        try:
            self.centralPointLoc.y = float(dict["localSystem3D"]["y"])
        except:
            raise CoordSystemLocal3DError, "parameter y not set"

        try:
            self.centralPointLoc.z = float(dict["localSystem3D"]["z"])
        except:
            raise CoordSystemLocal3DError, "parameter z not set"

        try:
            self.axesOri = dict["localSystem3D"]["axesOri"]
        except:
            raise CoordSystemLocal3DError, "parameter axesOri not set"

        try:
            self.bearingOri=dict["localSystem3D"]["bearingOri"]
        except:
            raise CoordSystemLocal3DError, "parameter bearingOri not set"

        try:
            self.name = dict["localSystem3D"]["name"]
        except:
            #raise CoordSystemLocal3DError, "parameter name not set"
            pass

        try:
            self.description = dict["localSystem3D"]["description"]
        except:
            #raise CoordSystemLocal3DError, "parameter description not set"
            pass

        #import sys
        #print >>sys.stderr, self



if __name__ == "__main__":

    cs = CoordSystemLocal3D(name="system 1", ellipsoidCode="wgs84", 
                            lat=1, lon=1, height=250, axesOri="ne",
                            bearingOri="right-handed")

    print cs
    x, y, z = cs.get_tran_to_local_dxyz2dxyz()(1,1,1)
    print x, y, z
    print cs.get_tran_to_local_dxyz2dxyz(inverse=True)(x,y,z)

