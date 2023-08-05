# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: ObsClusterCoor.py 107 2010-12-06 23:18:55Z tomaskubin $


from gizela.util.Error import Error
from gizela.data.ObsHeightDiff import ObsHeightDiff
from gizela.data.ObsClusterBase import ObsClusterBase
from gizela.data.PointListCovMat import PointListCovMat
from gizela.data.DUPLICATE_ID import DUPLICATE_ID
from gizela.data.point_text_table import coor_table


class ObsClusterCoorError(Error): pass


class ObsClusterCoor(ObsClusterBase):
    """class for cluster of height differences
    """

    __slots__ = []

    def __init__(self, covmat=None, textTable=None, 
                 duplicity=DUPLICATE_ID.error, sort=False):
        
        if textTable == None:
            textTable = coor_table()
        
        super(ObsClusterCoor, self).__init__()


        self._obsList = PointListCovMat(covmat=covmat, textTable=textTable)

    # multiple inheritance from classes with slots is not possible
    # TypeError: Error when calling the metaclass bases
    #    multiple bases have instance lay-out conflict

    # methods from PointListCovMat class
    def _get_cov_mat(self): return self._obsList.covmat
    def _set_cov_mat(self, covmat): self._obsList.covmat = covmat
    covmat = property(_get_cov_mat, _set_cov_mat)

    def set_sort(self): self._obsList.set_sort()
    def unset_sort(self): self._obsList.unset_sort()

    def add_point(self, point): self._obsList.add_point(point)
    def get_point(self, id): return self._obsList.get_point(id)

    def append_obs(self, obs): self._obsList.add_point(obs)

    def is_cov_mat_dim_ok(self): return self._obsList.is_cov_mat_dim_ok()
    
    def make_table(self): return self._obsList.make_table()
    
    # methods from ObsClusterBase
    def compute_corr(self, corr): pass
    
    # methods from ObsClusterBase
    def compute_obs(self, corr): pass    

    # methods from PointListCovMat and ObsClusterBase
    def __len__(self): return len(self._obsList)
    def __iter__(self): return iter(self._obsList)
    def __str__(self): return self._obsList.make_table()
    def make_gama_xml(self, corrected=False):
        return self._obsList.make_gama_xml()


if __name__ == "__main__":

    from gizela.data.PointCartCovMat import PointCartCovMat

    p1 = PointCartCovMat(id="A", x=100, y=200, z=300)
    p2 = PointCartCovMat(id="B", x=100, y=200, z=300)


    cl = ObsClusterCoor()
    cl.append_obs(p1)
    cl.append_obs(p2)

    print cl
    
    #covariance matrix
    from gizela.data.CovMat import CovMat
    cl.covmat = CovMat(6,0)
    cl.covmat.var = (1e-6, 2e-6, 3e-6, 4e-6, 5e-6, 6e-6)
    print cl.make_gama_xml()
    
    # iterator
    #print "\n".join(["%s" % obs for obs in cl])
    
