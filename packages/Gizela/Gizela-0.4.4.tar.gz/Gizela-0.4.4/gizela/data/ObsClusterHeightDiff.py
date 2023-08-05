# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: ObsClusterHeightDiff.py 107 2010-12-06 23:18:55Z tomaskubin $


from gizela.util.Error import Error
from gizela.data.ObsHeightDiff import ObsHeightDiff
from gizela.data.ObsClusterBase import ObsClusterBase
from gizela.data.obs_table import obs_height_diff_table


class ObsClusterHeightDiffError(Error): pass


class ObsClusterHeightDiff(ObsClusterBase):
    """class for cluster of height differences
    """

    __slots__ = []

    def __init__(self, textTable=None):

        if textTable == None:
            textTable = obs_height_diff_table()

        super(ObsClusterHeightDiff, self).__init__(textTable=textTable)

    def make_gama_xml(self, corrected=False):
        str = ["<height-differences>"]
        str.extend([obs.make_gama_xml(corrected) for obs in self._obsList])
        if self.is_cov_mat():
            str.append(self.make_gama_xml_covmat())
        str.append("</height-differences>")

        return "\n".join(str)
    
    def make_table_row(self):
        """
        returns row of table
        """
        return "".join([obs.make_table_row() for obs in self._obsList])


if __name__ == "__main__":

    from gizela.data.ObsHeightDiff import ObsHeightDiff

    dh1 = ObsHeightDiff("A", "B", 100.01, stdev=1.1)
    dh2 = ObsHeightDiff("A", "B", 100.01, dist= 5.5)


    cl = ObsClusterHeightDiff()
    cl.append_obs(dh1)
    cl.append_obs(dh2)

    print cl

    # covariance matrix
    from gizela.data.CovMat import CovMat
    cl.covmat = CovMat(2,1)
    cl.covmat.data = [[0.005*0.005, -0.001*0.001],[0.003*0.003]]

    # iterator
    print "\n".join(["from=%s to=%s" % (obs.fromid, obs.toid) for obs in cl])
    
    #print "Making correction"
    #from gizela.corr.ObsCorrSphere import ObsCorrSphere
    #from gizela.util.Ellipsoid     import Ellipsoid
    #from gizela.data.PointGeodetic import PointGeodetic
    #from gizela.data.PointCart     import PointCart
    #from gizela.data.PointList     import PointList

    #pA = PointCart("A", x=0, y=0, z=0)
    #pl = PointList(textTable=pA.textTable)
    #pl.add_point(pA)
    #pl.add_point(PointCart("B", x=1, y=1, z=1))
    #print pl

    #corr = ObsCorrSphere(ellipsoid=Ellipsoid(), 
    #        centralPointGeo=PointGeodetic(id="c", lat=0, lon=0, height=0),\
    #        centralPointLoc=PointCart(id="c", x=0, y=0, z=0), \
    #        pointList=pl)
    #cl.compute_corr(corr)
    #print cl
    #print cl.make_gama_xml(corrected=True)
