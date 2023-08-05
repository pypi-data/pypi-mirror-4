# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: PointListCovMat.py 119 2011-01-11 23:44:34Z tomaskubin $


from gizela.util.Error     import Error
from gizela.text.TextTable import TextTable
from gizela.data.PointBase import PointBase
from gizela.data.CovMat    import CovMat
from gizela.data.PointList import PointList
from gizela.data.DUPLICATE_ID import DUPLICATE_ID
from gizela.data.PointCartCovMat import PointCartCovMat
from gizela.data.point_text_table import coor_var_table

class PointListCovMatError(Error): pass

class PointListCovMat(PointList):
    """List of geodetic points PointBase with covariance matrix"""

    __slots__ = ["_covmat", "_numCoord"]
    
    def _get_covmat(self): return self._covmat
    def _set_covmat(self, covmat): 
        if isinstance(covmat, CovMat):
            self._covmat = covmat
            for point in self.list: point.covmat = covmat # sharing does not work
        else:
            raise PointListCovMatError, "CovMat instance expected"

    covmat = property(_get_covmat, _set_covmat)

    def __init__(self, covmat=None, textTable=None, duplicateId=DUPLICATE_ID.error, sort=False):
        '''
        duplicateId ... what to do with duplicit point
        textTable ... format of table for text output
        sort   ... sort output by id?
        '''

        if textTable == None:
            textTable = coor_var_table()
        super(PointListCovMat, self).__init__(textTable=textTable, 
                                              duplicateId=duplicateId,
                                              sort=sort)

        if covmat == None:
            self.covmat = CovMat(dim=0, band=-1)
        else:
            self.covmat = covmat

        self._numCoord = 0 # covmat row index of last coordinate

    
    def add_point(self, point, withCovMat=False):
        '''
        adds PointCartCovMat into list 
        and sets covariance matrix of point
        point index (of rows in covariance matrix)
        is set as position number of coordinates in
        all point list
        '''

        if isinstance(point, PointCartCovMat):
            if not withCovMat:
                point.covmat = self._covmat
                index = point.index
                #print index
                for i in xrange(len(index)):
                    if index[i] != None:
                        index[i] = self._numCoord
                        self._numCoord += 1
                point.index = index
            super(PointListCovMat, self).add_point(point)
        else:
            raise PointListCovMatError, \
                "PointCartCovMat or PointLocalGama instance expected"


    def get_num_coord(self):
        "returns the number of coordinates in point list"
        return self._numCoord

    #def update_covmat(self):
    #    """updating covariance matrix in each point - sharing does not work"""
    #    for point in self._list: point.covmat = self._covmat

    #def is_cov_mat_dim_ok(self):
    #    maxind = 0
    #    for point in self._list:
    #        maxind_ = max(point.index)
    #        if maxind_ > maxind: maxind = maxind_

    #    return maxind + 1 == self._covmat.dim 

    def is_cov_mat_dim(self):
        "is covariance matrix with proper dimension present?"
        #if self.covmat == None: return False
        return self._numCoord == self.covmat.dim

    def make_table(self):
        #if self._numCoord != self.covmat.dim:
        #    raise PointListCovMatError, "Wrong dimension of covariance matrix: expected %i, got %i" % (self._numCoord, self.covmat.dim)
                
        return super(PointListCovMat, self).make_table()

    def make_gama_xml(self):
        """
        make gama-local xml with covariance matrix - tag <coordinates>
        """

        str = []
        #if self._numCoord != self.covmat.dim:
        #    raise PointListCovMatError, "Wrong covariance matrix dimension: expected %i, got %i" % (self._numCoord, self.covmat.dim)

        str.append("<coordinates>")
        str.extend([point.make_gama_xml() for point in self])
        str.append(self.covmat.make_gama_xml())
        str.append("</coordinates>")
        return "\n".join(str) 


    def __add__(self, other):
        "addition of two point lists"
        raise NotImplementedError, "__add__ not implemented"

    def plot_error_ellipse(self, figure):
        "plots error ellipses of points from covariance matrix"

        for point in self.list: 
            point.plot_error_ellipse(figure)

    def set_use_apriori(self, use):
        """
        sets use of apriori/aposteriori standard deviation

        use: True/False
        """
        for point in self:
            point.covmat.useApriori=use


if __name__ == "__main__":
    
    # points
    c1 = PointCartCovMat(id="A",x=1,y=2,z=3)
    c1.var = (3,2,3)
    print c1
    c2 = PointCartCovMat(id="B",x=3,y=5,z=6)
    c2.var = (9,9,9)
    c3 = PointCartCovMat(id="C",x=2,y=4)
    c4 = PointCartCovMat(id="D",z=6)

    # covariance matrix
    covmat = CovMat(9,8)
    for i in xrange(9,0,-1): 
        for j in xrange(i): covmat.append_value((j+10.0-i)*1e-5)
    print covmat.data
    
    # point list
    pd=PointListCovMat()
    print pd
    print pd.make_gama_xml()
    pd.add_point(c1)
    pd.add_point(c2)
    pd.add_point(c3)
    pd.add_point(c4)
    pd.covmat = covmat
    
    # adjusting variances
    pd.get_point("A").var = (0.01**2, 0.02**2, 0.02**2)
    c2.var = (0.02**2, 0.01**2, 0.01**2)
    c3.var = (0.03**2, 0.03**2)
    c4.varz = 0.04**2

    #print pd
    print c1.covmat
    print pd
    print pd.make_gama_xml()

    # graph
    try:
        from gizela.pyplot.FigureLayoutBase import FigureLayoutBase
    except:
        print "import of graphic failed"
    else:
        fig = FigureLayoutBase()
        fig.set_axes_ori("ne")
        fig.errScale = 2
        pd.plot_(fig)
        pd.plot_error_ellipse(fig)
        fig.set_free_space()
        fig.show_()
