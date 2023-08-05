# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: ObsZAngle.py 82 2010-10-30 22:15:55Z michal $


from gizela.data.ObsBase import ObsBase
from gizela.data.obs_table import obs_cluster_table


class ObsZAngle(ObsBase):
    """class for zenit angle
    """
    
    __slots__ = []

    def __init__(self, toid, val, fromid=None, fromdh=None, todh=None,
                 stdev=None, textTable=None):
        """zenit angle:
            toid    id of target
            val    measured value in gons
            stdev    standard deviation in 10*miligons
            todh    heidht of target in meters
        """
        
        if textTable == None:
            textTable = obs_cluster_table()

        from math import pi

        super(ObsZAngle, self).__init__(tag="z-angle", toid=toid, todh=todh,
                                        val=val, fromid=fromid, fromdh=fromdh,
                                        stdev=stdev, textTable=textTable,
                                        valscale=200/pi, stdevscale=1e4)
        self._dim = 1

    def compute_corr(self, corr):
        """
        Computes zenith angle correction
        @param corr: Instance of ObsCorrSphere correction
        @type corr: object ObsCorrSphere
        """        
#        corr.correct_zenith(self)
        self.corr = corr.correct_z_angle(self)
        
    def compute_obs(self, corr):
        """
        Computes zenith angle value
        @param corr: Instance of ObsCorrSphere correction
        @type corr: object ObsCorrSphere
        """
        self.val = corr.compute_z_angle(self)        
        
if __name__ == "__main__":
    z1 = ObsZAngle(toid="AB", val=1.5)
    z2 = ObsZAngle(toid="AB", val=3.14, todh=1.54, stdev=0.0023)
    z3 = ObsZAngle(toid="AB", val=3.14, fromid="CD", fromdh=1.54)

    print z1
    print z1.make_gama_xml()
    print z1.make_gama_xml(corrected=True)
    print z2
    print z2.make_gama_xml()
    print z3
    print z3.make_gama_xml()

