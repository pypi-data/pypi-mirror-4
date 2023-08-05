# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.util.Ellipsoid import Ellipsoid
from gizela.util.AxesOrientation import AxesOrientation

from gizela.data.PointGeodetic import PointGeodetic
from gizela.data.PointCart import PointCart


class CoordSystemGlobal(object):
    """
    coordinate system global 3D
    """

    def __init__(self,
                 ellipsoidCode="wgs84",
                 name="",
                 description=""):
        """
        ellipsoidCode: code of ellipsoid from gizela.util.Ellipsoid class
        name: short name of system
        description: longer description of system
        """

        self.ellipsoid = Ellipsoid(code=ellipsoidCode)
        self.name = name
        self.description = description

    def set_ellipsoid(self, code="wgs84"):
        self.ellipsoid = Ellipsoid(code=code)


    def get_tran_llh2xyz(self):
        """
        transformation from latitude, longitude and height to
        x, y, z coordinates

        returns transformation instance
        """

        return self.ellipsoid.llh2xyz_


    def get_tran_xyz2llh(self):
        """
        transformation from x, y, z geocentric coordinates
        to latitude, longitude and height

        returns transformation instance
        """
    
        return  self.ellipsoid.xyz2llh_


    def __str__(self):
        str = ["Name: %s" % self.name]
        str.append("Ellipsoid: %s" % self.ellipsoid)
        str.append("Description:%s" % self.description)

        return "\n".join(str)



if __name__ == "__main__":

    cs = CoordSystemGlobal(name="system 1", ellipsoidCode="wgs84", 
                     description="description of system 1")

    print cs
    x, y, z = cs.get_tran_llh2xyz()(1,1,250)
    print x, y, z
    print cs.get_tran_xyz2llh()(x,y,z)

