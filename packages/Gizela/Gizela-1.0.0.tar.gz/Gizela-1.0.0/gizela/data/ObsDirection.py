# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: ObsDirection.py 82 2010-10-30 22:15:55Z michal $


from gizela.data.ObsBase import ObsBase
from gizela.util.Error   import Error
from gizela.data.obs_table import obs_cluster_table


class ObsDirectionError(Error): pass


class ObsDirection(ObsBase):
    """class for horizontal direction
    """

    __slots__ = []

    def __init__(self, toid, val, fromdh=None, todh=None, stdev=None,
                textTable=None):
        """horizontal direction:
            to    id of target
            val    measured value in gons
            stdev    standard deviation in 10*miligons
            todh    heidht of target in meters
        """

        if textTable == None:
            textTable = obs_cluster_table()

        from math import pi

        super(ObsDirection, self).__init__(tag="direction", toid=toid, todh=todh, val=val,
                fromdh=fromdh, stdev=stdev, textTable=textTable,
                                           valscale=200.0/pi, stdevscale=1e4)
        self._dim = 1

    def compute_corr(self, corr):
        """
        Computes direction correction
        @param corr: Instance of ObsCorrSphere correction
        @type corr: object ObsCorrSphere
        """
#        corr.correct_direction(self)
        self.corr = corr.correct_direction(self)

    def compute_obs(self, corr):
        """
        Computes direction value
        @param corr: Instance of ObsCorrSphere correction
        @type corr: object ObsCorrSphere
        """
        self.val = corr.compute_direction(self)    


if __name__ == "__main__":
    dir1 = ObsDirection(toid="AB", val=1.0)
    dir2 = ObsDirection(toid="AB", val=1.01, todh=1.54, stdev=0.023)
    dir3 = ObsDirection(toid="AB", val=3.14, fromdh=1.54)

    print dir1.make_gama_xml()
    print dir1.make_gama_xml(corrected=True)
    print dir2
    print dir2.make_gama_xml()
    print dir3
    print dir3.make_gama_xml()

