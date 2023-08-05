# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.util.CoordSystemGlobal import CoordSystemGlobal
from gizela.util.AxesOrientation import AxesOrientation

from gizela.util.Ellipsoid import Ellipsoid
from gizela.data.PointGeodetic import PointGeodetic
from gizela.data.PointCart import PointCart
from gizela.util.Error import Error


class CoordSystemLocal2DError(Error): pass


class CoordSystemLocal2D(CoordSystemGlobal, AxesOrientation):
    """
    local coordinate system 2D
    """

    def __init__(self,
                 ellipsoidCode="wgs84",
                 axesOri="ne",
                 bearingOri="right-handed",
                 name="",
                 description="",
                 proj4String="",
                 distScale=1.0):
        """
        ellipsoidCode: code of ellipsoid from gizela.util.Ellipsoid class
        axesOri: orientation of x and y axis
        bearingOri: orientation of bearings right-handed/left-handed
        name: short name of local system
        description: longer description of system
        proj4String: string of parameters for pyproj.Proj class
                     for projection from global to local system
        distScale: scale factor for distance reduction
        """

        AxesOrientation.__init__(self, axesOri=axesOri,
                                        bearingOri=bearingOri)
        CoordSystemGlobal.__init__(self, ellipsoidCode=ellipsoidCode,
                                   name=name, description=description)

        self.name = name
        self.description = description
        self.proj4String = proj4String
        self.distScale = distScale

    def __eq__(self, other):
        if isinstance(other, CoordSystemLocal2D):
            if self.ellipsoidCode == other.ellipsoidCode \
               and self.axesOri == other.axesOri \
               and self.bearingOri == other.bearingOri \
               and self.proj4String == other.proj4String \
               and self.distScale == other.distScale:
                return True
        return False


    def get_tran_to_local_xyz2xy(self, inverse=False):
        """
        returns projection from geocentric coordinate system XYZ
        to local E2 system xy
        """
        if inverse:
            raise NotImplementedError, "Inverse projection not implemented"
        else:
            return self._get_proj_xyz2xy


    def get_tran_to_local_ll2xy(self, inverse=False):
        """
        returns projection from latitude, longitude in radians to xy
        """

        if inverse:
            raise NotImplementedError, "Inverse projection not implemented"
        else:
            return self._get_proj_ll2xy


    def _get_proj_xyz2xy(self, x, y, z):
        """
        returns projection from x, y, z geocentric to x, y
        """

        lat, lon, height = self.get_tran_xyz2llh()(x, y, z)

        return self.get_tran_to_local_ll2xy()(lat, lon)


    def _get_proj_ll2xy(self, lon, lat): 
        """
        returns projection instance from geodetic coordinate system 
        lon, lat in radians to local E2 system xy in meters

        This transformation is set from proj4String of parameters 
        for pyproj.Proj projection

        Warning: parameters radians, errcheck and inverse do not work
       """

        from pyproj import Proj
        from gizela.util.Converter import Converter

        #self.projDict["radians"] = True
        #self.projDict["errcheck"] = True
        #self.projDict["inverse"] = inverse

        #import sys
        #print >>sys.stderr, self
        (y, x) = Proj(self.proj4String)(Converter.rad2deg_(lon),
                                        Converter.rad2deg_(lat))

        return x, y


    def __str__(self):
        str = ["Name: %s" % self.name]
        str.append(AxesOrientation.__str__(self))
        str.append("Ellipsoid: %s" % self.ellipsoid)
        str.append("Description:%s" % self.description)
        str.append("Proj4String:%s" % self.proj4String)

        return "\n".join(str)

    def proj_pointCart(self, pointCart):
        """
        transformation from geocetric xyz system to local xy system
        with use of PointCart instance

        x ~ latitude
        y ~ longitude
        """


        tran = self.get_tran_to_local_xyz2xy()
        x, y = tran(pointCart.x, pointCart.y, pointCart.z)

        pointCart.x = x
        pointCart.y = y
        pointCart.z = None


    def parse_config_dict(self, dict):
        """
        sets self with values from dict
        """

        # set 
        try:
            self.set_ellipsoid(dict["localSystem2D"]["ellipsoid"])
        except:
            raise CoordSystemLocal2DError, "parameter ellipsoid not set"

        try:
            self.axesOri = dict["localSystem2D"]["axesOri"]
        except:
            #import sys
            #print >>sys.stderr, dict
            raise CoordSystemLocal2DError, "parameter axesOri not set"

        try:
            self.bearingOri=dict["localSystem2D"]["bearingOri"]
        except:
            raise CoordSystemLocal2DError, "parameter bearingOri not set"

        try:
            self.name = dict["localSystem2D"]["name"]
        except:
            #raise CoordSystemLocal2DError, "parameter name not set"
            pass

        try:
            self.description = dict["localSystem2D"]["description"]
        except:
            #raise CoordSystemLocal2DError, "parameter description not set"
            pass

        try:
            self.proj4String = dict["localSystem2D"]["proj4String"]
        except:
            raise CoordSystemLocal2DError, "parameter proj4String not set"

        try:
            self.distScale = dict["localSystem2D"]["distScale"]
        except:
            raise CoordSystemLocal2DError, "parameter distScale not set"


if __name__ == "__main__":

    cs = CoordSystemLocal2D(name="system 1", ellipsoidCode="wgs84", 
                            axesOri="ne",
                            bearingOri="right-handed",
                            proj4String="+proj=lcc +ellps=WGS84 +lat_1=50.09")

    print cs
    proj = cs.get_tran_to_local_ll2xy()
    x, y = proj(1,1)
    print x, y 

    from gizela.data.PointCart import PointCart

    x, y, z = cs.get_tran_llh2xyz()(1, 1, 250)
    p = PointCart(id="A", x=x, y=y, z=z)
    print p
    cs.proj_pointCart(p)
    print p

    print "Is", cs.is_consistent() and "consistent" or "inconsistent"
    cs.bearingOri = "left-handed"
    print "Is", cs.is_consistent() and "consistent" or "inconsistent"
