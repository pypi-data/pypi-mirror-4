# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: ObsVector.py 82 2010-10-30 22:15:55Z michal $


from gizela.data.ObsBase import ObsBase
from gizela.util.Error   import Error
from gizela.data.obs_table import obs_vector_stdev_table
from gizela.data.CovMat import CovMat


class ObsVectorError(Error): pass


class ObsVector(ObsBase):
    """
    class for vectors - coordinate differences
    2d or 3d vector
    """

    __slots__ = ["dx", "dy", "dz"]

    def __init__(self, fromid, toid,  
                 dx, dy, dz=None, 
                 textTable=None):
        """
        vector:
        fromid        id of stand point
        toid        id of target
        dx, dy, dz    coordinate differences
        """
        
        if textTable == None:
            textTable = obs_vector_stdev_table() 

        super(ObsVector, self).__init__(tag="vec", fromid=fromid, toid=toid,
                                        textTable=textTable)
    
        self.dx, self.dy, self.dz = dx, dy, dz
        if dz is None:
            self._dim = 2
        else:
            self._dim = 3

    def compute_corr(self, corr):
        """
        No correction I{pass}
        @param corr: Instance of ObsCorrSphere correction
        @type corr: object ObsCorrSphere
        """
        pass # no correction
    
    def compute_obs(self, corr):
        """
        Computes vector value
        @param corr: Instance of ObsCorrSphere correction
        @type corr: object ObsCorrSphere
        """
        self.val = corr.compute_vector(self) 
            
    def make_gama_xml(self, corrected=False):

        if self._dim == 2:
            return '<vec from="%s" to="%s" dx="%.4f" dy="%.4f"/>' \
                    % (self.fromid, self.toid, self.dx, self.dy)
        else:
            return '<vec from="%s" to="%s" dx="%.4f" dy="%.4f" dz="%.4f"/>' \
                    % (self.fromid, self.toid, self.dx, self.dy, self.dz)
    
    def make_table_row(self): 
        """
        returns row of table
        """
        var = self.var        

        if self._dim == 2:
            var.append(None)

        return self.textTable.make_table_row(self._tag, self.fromid, self.toid, 
                                             self.dx, self.dy, self.dz, 
                                             var[0], var[1], var[2])
        
    def _get_var(self):
        "return variance of vector"
        if self.cluster == None or self.index == None or \
           self.cluster.covmat == None:
            return [None for i in xrange(self._dim)]
        else:
            return [self.cluster.covmat.get_var(i) \
                    for i in xrange(self.index, self.index + self._dim)] 
    
    def _set_var(self, var):
        "sets variances of vector"

        if len(var) != self._dim:
            raise ObsVectorError,\
                "dimension of observation != number of variances (%i != %i)" %\
                        (self._dim, len(var))

        if self.cluster == None:
            raise ObsVectorError, "Cluster not set"
        if self.index == None:
            raise ObsVectorError, "Index of row in covariance matrix not set"
        for i in xrange(self._dim):
            self.cluster.covmat.set_var(self.index + i, var[i])

    var = property(_get_var, _set_var)
    
    def _get_cov(self):
        "returns covariances of vector"
        
        if self.cluster == None or self.cluster.covmat == None:
            raise ObsVectorError, "No covariance matrix - no cluster"
        if self.index == None:
            raise ObsVectorError, "No row index in covariance matrix"
        if self._dim == 2:
            return self.cluster.covmat.get_cov(self.index, self.index + 1)
        else: # _dim = 3
            return [self.cluster.covmat.get_cov(self.index, self.index + 1),
                    self.cluster.covmat.get_cov(self.index, self.index + 2),
                    self.cluster.covmat.get_cov(self.index + 1, self.index + 2)]
    
    def _set_cov(self, cov):
        """
        sets covariances of vector

        if covariance matrix band width is 0 or 1 enlarge bandwidth to 2
        """     
        
        if self.cluster == None or self.cluster.covmat == None:
            raise ObsVectorError, "No covariance matrix - no cluster"
        if self.index == None:
            raise ObsVectorError, "No row index in covariance matrix"
        #if self._dim == 2:
            #if len(cov) != 1:
            #    raise ObsVectorError, "One covariance expected"
        if self._dim == 3:
            if len(cov) != 3:
                raise ObsVectorError, "Three covariances expected"

        if self._dim == 2:
            self.covmat.band = 1
            self.cluster.covmat.set_cov(self.index, self.index + 1, cov)
        else:
            self.covmat.band = 2
            self.cluster.covmat.set_cov(self.index, self.index + 1, cov[0])
            self.cluster.covmat.set_cov(self.index, self.index + 2, cov[1])
            self.cluster.covmat.set_cov(self.index + 1, self.index + 2, cov[2])
    
    cov = property(_get_cov, _set_cov)



    def _get_covmat(self):
        "returns covariance matrix of vector"
        if self.cluster == None or self.cluster.covmat == None:
            #raise ObsVectorError, "No covariance matrix - no cluster"
            return None
        if self.index == None:
            #raise ObsVectorError, "No row index in covariance matrix"
            return None
        if len(self.cluster) == 1: # just one vector in cluster
            if self.cluster.covmat.dim == 3:
                return self.cluster.covmat
        cm = CovMat(dim=self._dim, band=self._dim-1)
        cm.var = self.var
        cov = self.cov
        if self._dim == 2:
            cm.set_cov(0, 1, cov)
        else:
            cm.set_cov(0, 1, cov[0])
            cm.set_cov(0, 2, cov[1])
            cm.set_cov(1, 2, cov[2])
        return cm

    def _set_covmat(self, covmat):
        "sets covariance matrix of vector"
        
        if self.cluster == None or self.cluster.covmat == None:
            raise ObsVectorError, "No covariance matrix - no cluster"
        if self.index == None:
            raise ObsVectorError, "No row index in covariance matrix"
        
        self.var = covmat.var
        if self._dim == 2:
            self.cov = covmat.get_cov(0, 1)
        else: # _dim == 3
            self.cov = (covmat.get_cov(0, 1),
                        covmat.get_cov(0, 2),
                        covmat.get_cov(1, 2))

    covmat = property(_get_covmat, _set_covmat)

    def tran_3d(self, coordSystem):
        """
        transformation of vector with covariance matrix
        
        coordSystem: CoordSystemLocal3D instance
        """

        if self._dim != 3:
            raise ObsVectorError, "Transformation only 3D vectors"

        tran = coordSystem.get_tran_to_local_dxyz2dxyz()

        # transformation of vector
        self.dx, self.dy, self.dz = tran(self.dx, self.dy, self.dz)

        # transformation of covariance matrix
        if self.covmat is not None:
            cm = self.covmat
            cm.transform_(tran)
            self.covmat = cm


    def tran_2d(self, coordSystem, pointList):
        """
        transforms 3d vector in geocentric system to local 2d system
        using projection proj. Covariance matrix is transformed to neu
        directions

        coordSystem: CoordSystemLocal2D instance 
        pointList: list of points - PointList instance
        """

        if self._dim != 3:
            import sys
            print >>sys.stderr, self
            raise ObsVectorError, "Transforms only 3D vectors"

        # find start point of vector
        try:
            point1 = pointList.get_point(self.fromid)
        except:
            import sys
            print >>sys.stderr, pointList
            print >>sys.stderr, self
            raise ObsVectorError, \
                "Transformation of vector failed. Unknown coordinates of first point %s" % self.fromid

        #import sys
        #print >>sys.stderr, point1
        if not point1.is_set_xyz():
            import sys
            print >>sys.stderr, pointList
            print >>sys.stderr, self
            raise ObsVectorError, "Point %s without xyz coordinates" %\
                    self.fromid

        # point from and to in geographic coordinates
        lat1, lon1, height1 = coordSystem.get_tran_xyz2llh()(point1.x, 
                                                             point1.y, 
                                                             point1.z)

        lat2, lon2, height2 = coordSystem.get_tran_xyz2llh()(\
                                                        point1.x + self.dx, 
                                                        point1.y + self.dy, 
                                                        point1.z + self.dz)
        
        # projection of points
        x1, y1 = coordSystem.get_tran_to_local_ll2xy()(lat1, lon1)
        x2, y2 = coordSystem.get_tran_to_local_ll2xy()(lat2, lon2)

        # making vector
        self.dx, self.dy, self.dz = x2 - x1, y2 - y1, height2 - height1
        #self.dx, self.dy, self.dz = x2 - x1, y2 - y1, None
        #self._dim = 2

        # transformation of covariance matrix
        from gizela.util.CoordSystemLocal3D import CoordSystemLocal3D
        csl = CoordSystemLocal3D(ellipsoidCode=coordSystem.ellipsoid.get_code(),
                                 lat=0.5*(lat1 + lat2),
                                 lon=0.5*(lon1 + lon2))
        tran = csl.get_tran_to_local_dxyz2dxyz()

        if self.covmat is not None:
            cm = self.covmat
            cm.transform_(tran)
            # reduction of covariance matrix from 3x3 to 2x2
            #cm.slice(2)
            #print cm
            self.covmat = cm



if __name__ == "__main__":

    dx =  354.799
    dy = -465.803
    dz = -164.077

    v = ObsVector(fromid="A", toid="B", dx=dx, dy=dy, dz=dz)
    
    print v.make_gama_xml()
    print v
    
    from gizela.data.obs_table import obs_vector_table
    
    v.textTable = obs_vector_table()
    print v

    from gizela.tran.Tran3D import Tran3D

    lat = 50.091153311111
    lon = 14.401833202777

    from math import pi
    
    alpha = 0
    beta = (lat - 90)*pi/180
    gamma = (lon - 180)*pi/180

    
    tr = Tran3D()
    tr.rotation_xyz(alpha, beta, gamma)
    
    v.tran_3d(tr)
    print v.make_gama_xml()
