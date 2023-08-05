# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: ObsSDistance.py 107 2010-12-06 23:18:55Z tomaskubin $


from gizela.data.ObsBase import ObsBase
from gizela.data.obs_table import obs_cluster_table


class ObsSDistance(ObsBase):
    """class for slope distance
    """

    __slots__ = []

    def __init__(self, toid, val, fromid=None, fromdh=None, todh=None,
                 stdev=None, textTable=None):
        """slope distance:
            toid    id of target
            val    measured value in meters
            stdev    standard deviation in milimeters
            todh    heidht of target in meters
        """
        
        if textTable == None:
            textTable = obs_cluster_table()

        super(ObsSDistance, self).__init__(tag="s-distance", toid=toid, todh=todh, 
                                           val=val, fromid=fromid, fromdh=fromdh,
                                           stdev=stdev, textTable=textTable,
                                           stdevscale=1e3)
        self._dim = 1

    def compute_corr(self, corr):
        """
        No correction I{pass}
        @param corr: Instance of ObsCorrSphere correction
        @type corr: object ObsCorrSphere
        """        
        pass # no correction
    
    def compute_obs(self, corr):
        """
        Computes slope distance value
        @param corr: Instance of ObsCorrSphere correction
        @type corr: object ObsCorrSphere
        """
        self.val = corr.compute_s_distance(self)      

    def get_distance(self, zangle):
        """
        returns horizontal distance

        warning: stdev of horizontal distance is the same as
                 slope distance
        """
        from math import sin, cos

        phi = self.val * sin(zangle.val) / 6378e3
        val = self.val * sin(zangle.val - phi) / cos(phi/2)
        #val = self.val * sin(zangle.val)

        from gizela.data.ObsDistance import ObsDistance

        return ObsDistance(fromid=self.fromid, toid=self.toid,
                           val=val, fromdh=self.fromdh, todh=self.todh,
                           stdev=self.stdev, textTable=self.textTable)


if __name__ == "__main__":
    sdist1 = ObsSDistance(toid="AB", val=100.01)
    sdist2 = ObsSDistance(toid="AB", val=100.01, todh=1.54, stdev=0.023)
    sdist3 = ObsSDistance(toid="AB", val=100.01, fromid="CD", fromdh=1.54)

    print sdist1
    print sdist1.make_gama_xml()
    print sdist2
    print sdist2.make_gama_xml()
    print sdist3
    print sdist3.make_gama_xml()

    from gizela.data.ObsZAngle import ObsZAngle
    from math import pi

    z = ObsZAngle(toid="", val=90*pi/200)
    print sdist1.get_distance(z)
    print sdist2.get_distance(z)
    print sdist3.get_distance(z)
