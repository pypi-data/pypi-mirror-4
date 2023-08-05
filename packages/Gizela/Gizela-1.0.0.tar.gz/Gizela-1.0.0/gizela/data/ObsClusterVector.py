# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: ObsClusterVector.py 107 2010-12-06 23:18:55Z tomaskubin $


from gizela.util.Error import Error
from gizela.data.ObsHeightDiff import ObsHeightDiff
from gizela.data.ObsClusterBase import ObsClusterBase
from gizela.data.obs_table import obs_vector_stdev_table


class ObsClusterVectorError(Error): pass


class ObsClusterVector(ObsClusterBase):
    """class for cluster of height differences
    """

    __slots__ = []

    def __init__(self, covmat=None, textTable=None): 

        if textTable==None:
            textTable = obs_vector_stdev_table()

        super(ObsClusterVector, self).__init__(covmat=covmat, textTable=textTable)

    def make_gama_xml(self, corrected=False):
        str = ["<vectors>"]
        str.extend(["\t" + obs.make_gama_xml(corrected) for obs in self._obsList])
        if self.is_cov_mat():
            str.append(self.make_gama_xml_covmat())
        str.append("</vectors>")

        return "\n".join(str)

    def make_table_row(self):
        return "".join([obs.make_table_row() for obs in self._obsList])


    def tran_3d(self, coordSystem):
        for v in self._obsList:
            v.tran_3d(coordSystem)

    def tran_2d(self, coordSystem, pointList): 
        if len(self._obsList) != 1:
            raise ObsClusterVectorError, "method transform_2d() works only with one vector in cluster"
            # working with covariance matrix for more than one vector
            # is not implemented

        for v in self._obsList:
            v.tran_2d(coordSystem, pointList)
            #self._lastIndex -= 1 # retuce from 3d to 2d - one dimension


    def scale_cov_mat(self, factor):
        self.covmat.scale_(factor)


if __name__ == "__main__":

    from gizela.data.ObsVector import ObsVector
    from gizela.data.CovMat import CovMat

    v1 = ObsVector(fromid="A", toid="B", dx=100, dy=200, dz=300)
    v2 = ObsVector(fromid="B", toid="C", dx=400, dy=300, dz=200)


    cl = ObsClusterVector()
    cl.append_obs(v1)
    cl.append_obs(v2)

    print cl.make_gama_xml()
    print cl
    from gizela.data.obs_table import obs_vector_table
    cl.textTable = obs_vector_table()
    print cl
    
    cl.covmat = CovMat(6,5)
    #cl.covmat.stdev = (0.01, 0.02, 0.03, 0.04, 0.05, 0.06)
    #cl.covmat.var = (0.01, 0.02, 0.03, 0.04, 0.05)
    cl.covmat.data = [[1,2,3,4,5,6], [2,3,4,5,6], [3,4,5,6], [4,5,6], [5,6], [6]]

    print cl.make_gama_xml()
    cl.textTable = obs_vector_stdev_table()
    print cl
    
    # iterator
    print "\n".join(["from=%s to=%s" % (obs.fromid, obs.toid) for obs in cl])
    
    #covmat of vectors
    print v1.covmat.data
    print v2.covmat.data
    cm = CovMat(3,2)
    cm.data = [[0.1, 0.2, 0.3],[0.2, 0.3],[0.3]]
    v1.covmat = cm
    print cl.covmat.data
    
    # transformation
    #from gizela.tran.Tran3D import Tran3D
    #tr = Tran3D()
    #from math import pi
    #tr.rotation_xyz(pi/2, pi/2, pi/2)
    #cl.tran_3d(tr)
    #print cl
