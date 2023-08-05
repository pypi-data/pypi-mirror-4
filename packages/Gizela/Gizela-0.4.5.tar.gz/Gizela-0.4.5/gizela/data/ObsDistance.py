# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: ObsDistance.py 82 2010-10-30 22:15:55Z michal $


from gizela.data.ObsBase import ObsBase
from gizela.util.Error   import Error
from gizela.data.obs_table import obs_cluster_table


class ObsDistanceError(Error): pass


class ObsDistance(ObsBase):
    """class for horizontal distance
    """

    __slots__ = []

    def __init__(self, toid, val, fromid=None, fromdh=None, todh=None,
                 stdev=None, textTable=None):
        """horizontal distance:
            to    id of target
            val    measured value in meters
            stdev    standard deviation in milimeters
            to_dh    heidht of target in meters
        """
        
        if textTable == None:
            textTable = obs_cluster_table()

        super(ObsDistance, self).__init__(tag="distance", toid=toid, val=val, 
                                          fromid=fromid, fromdh=fromdh, 
                                          todh=todh, stdev=stdev,
                                          textTable=textTable,
                                          stdevscale=1e3)
        self._dim = 1

    def compute_corr(self, corr):
        """
        No correction I{pass}
        @param corr: Instance of ObsCorrSphere correction
        @type corr: object ObsCorrSphere
        """
        pass
    
    def compute_obs(self, corr):
        """
        Computes distance value
        @param corr: Instance of ObsCorrSphere correction
        @type corr: object ObsCorrSphere
        """
        self.val = corr.compute_distance(self)     

    def scale(self, scale):
        self.val *= scale

if __name__ == "__main__":
    dist1 = ObsDistance(toid="AB", val=100.01)
    dist2 = ObsDistance(toid="AB", val=100.01, todh=1.54, stdev=2.3)
    dist3 = ObsDistance(toid="AB", val=100.01, fromid="CD", fromdh=1.54)

    print dist1
    print dist1.make_gama_xml()
    print dist2
    print dist2.make_gama_xml()
    print dist3
    print dist3.make_gama_xml()
