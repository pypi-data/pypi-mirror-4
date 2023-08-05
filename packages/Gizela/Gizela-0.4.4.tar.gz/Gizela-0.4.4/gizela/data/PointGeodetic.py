# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz>
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: PointGeodetic.py 76 2010-10-22 21:19:21Z tomaskubin $

"""Module PointGeodetic:    geodetic coordinates latitude, longitude, height
"""


#from gizela.text.TextTable import TextTable
from gizela.data.PointBase import PointBase
from gizela.data.point_text_table import geo_coor_table
from gizela.util.Converter import Converter


class PointGeodetic(PointBase):
    """Class for geodetic coordinates latitude, longitude, height"""

#    __slots__ = ["_lat", "_lon", "_height"]

    def __init__(self, id, lat=None, lon=None, height=None, textTable=None):
        """id, coordinates latitude, longitude, height
        and format of text table output
        """
        
        self.lat=lat; self.lon=lon; self.height=height

        if textTable == None:
            textTable = geo_coor_table()
        
        super(PointGeodetic, self).__init__(id, textTable=textTable)

#    def get_lat(self): return self._lat
#    def get_lon(self): return self._lon
#    def get_height(self): return self._height
    def get_latlon(self): return (self.lat, self.lon)
    def get_latlonheight(self): return (self.lat, self.lon, self.height)

#    def set_lat(self,lat): self._lat = lat
#    def set_lon(self,lon): self._lon = lon
#    def set_height(self, height): self._height = height
#    def set_latlon(self, lat, lon):
#        self._lat = lat
#        self._lon = lon
#    def set_latlonheight(self, lat, lon, height):
#        self._lat = lat
#        self._lon = lon
#        self._height = height

    def make_table_row(self): 
        return self.textTable.make_table_row(self.id, 
                                             Converter.rad2deg_(self.lat),
                                             Converter.rad2deg_(self.lon),
                                             self.height)

    def get_point_cart(self, ellipsoid):
        from gizela.data.PointCart import PointCart

        x, y, z = ellipsoid.llh2xyz_(self.lat, self.lon, self.height)
        return PointCart(id=self.id, x=x, y=y, z=z)
    

if __name__=="__main__":

    c1 = PointGeodetic(id="A", lat=1, lon=2)
    c2 = PointGeodetic(id="A2", lat=1, lon=2, height=3)
    c2.set_text_table_type("border")

    print c1
    print 
    print c2
