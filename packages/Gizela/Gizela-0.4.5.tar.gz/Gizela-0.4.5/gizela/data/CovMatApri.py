# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$


from gizela.util.Error import Error
from gizela.data.CovMat import CovMat


class CovMatApriError(Error):
    '''Exception for CovMatApri class'''
    pass

class CovMatApri(CovMat):
    '''
    class for variance-covariance matrix
    with apriori/aposteriori values
    internally stores apriori variances covariances
    '''

    def __init__(self, dim=0, band=None, apriori=1.0, aposteriori=1.0, 
                 useApriori=True):
        '''
        dim  ... dimension of covariance matrix
        band ... band width of covariance matrix
        apriori ... apriori value of unit standard devition
        aposteriori ... aposteriori value of unit standard deviation
        useApriori ... get/set apriori values?
        '''
       
        super(CovMatApri, self).__init__(dim=dim, band=band)
        
        self._apriori = apriori # apriori standard deviations
        self._aposteriori = aposteriori # aposteriori standard deviation
        self.useApriori = useApriori # get/set apriori values?

    def _get_apriori(self): return self._apriori
    def _get_aposteriori(self): return self._aposteriori

    def _set_apriori(self, apriori):
        self._apriori = apriori
        self._compute_ratio()

    def _set_aposteriori(self, aposteriori):
        self._aposteriori = aposteriori
        self._compute_ratio()

    aposteriori = property(_get_aposteriori, _set_aposteriori)
    apriori = property(_get_apriori, _set_apriori)

    def _set_use_apriori(self, useApriori):
        self._useApriori = useApriori
        self._compute_ratio()

    def _get_use_apriori(self): return self._useApriori

    useApriori = property(_get_use_apriori, _set_use_apriori)

    def _compute_ratio(self):
        if self.useApriori:
            self._ratio = 1.0
        else:
            self._ratio = self._aposteriori**2 / self._apriori**2

    def _get_var(self): 
        var = super(CovMatApri, self)._get_var()
        return [v*self._ratio for v in var]
    
    def _set_var(self, var):
        var = [v/self._ratio for v in var]
        super(CovMatApri, self)._set_var(var)

    var = property(_get_var, _set_var)



    def append_value(self, val):
        '''append value to covariance matrix
        with respect to dim and band'''
                
        if self._allElements:
            raise CovMatError, "All elements in covariance matrix are allready appended"
        
        if self._col == self._rowlen : # junp to a new row
            self._row += 1
            self._col = 0
            if self._row == self._dim - 1: # last row
                self._allElements = True
            if self._row > self._dim - self._band - 1:
                self._rowlen -= 1
    
        #print "ROW:", self._row, " COL:", self._col, " ROW_LEN:", self._rowlen
        self._data[self._row].append(val/self._ratio)
        self._col += 1

    def set_var(self, row, var):
        '''sets variance var in row in matrix'''
        var= var/self._ratio
        super(CovMatApri, self).set_var(row, var)

    def set_cov(self, row, col, cov):
        '''sets covariance cov in row, col in matrix'''
        cov = cov/self._ratio
        super(CovMatApri, self).set_cov(row, col, cov)


    def get_var(self, row):
        '''returns variance
        row ... index of row - starts from 0'''
        return super(CovMatApri, self).get_var(row)*self._ratio

    def get_cov(self, row, col):
        '''returns covariance
        row, col ... index of row and column - starts from 0'''
        return super(CovMatApri, self).get_cov(row, col)*self._ratio


    def __str__(self):
        str = [super(CovMatApri, self).__str__(),
               "apriori: %e" % self.apriori,
               "aposteriori %e" % self.aposteriori,
               "use: %s" % (self.useApriori and "apriori" or "aposteriori")]
        return "  ".join(str)


    def make_gama_xml(self):
        str = ['<cov-mat dim="%i" band="%i"><!--%s-->' % (self._dim,
                                                          self._band,
                            self.useApriori and "apriori" or "aposteriori")]
        for irow in xrange(self._dim):
            rowlen = min(self._band + 1, self._dim - irow)
            str1 = []
            for i in xrange(rowlen):
                try:
                    val = self.data[irow][i]
                except IndexError:
                    str1.append("%14.7e" % 0)
                else:
                    if val == None:
                        str1.append("%14.7e" % 0)
                    else:
                        str1.append("%14.7e" % (val*self._ratio*1e6))
            str.append("  ".join(str1))
        str.append("</cov-mat>")

        return "\n".join(str)
        

    def _get_mat(self):
        "returns NumPy matrix of self"

        from numpy import zeros, diagonal, diag, matrix, float_

        a = zeros(shape=(self._dim,self._dim), dtype=float_)
        
        i = 0
        for row in self.data:
            row = [r*self._ratio for r in row]
            a[i,i:i+len(row)] = row
            i += 1

        a = a + a.T - diag(a.diagonal())
        return matrix(a, copy=False)

    def _set_mat(self, mat):
        "sets self from NumPy matrix"

        if (self.dim, self.dim) != mat.shape:
            raise CovMatError, "wrong dimension of matrix: dim=%i shape=%i,%i"%\
                                (self.dim, mat.shape[0], mat.shape[1])

        for i in xrange(self.dim):
            self.data[i] = []
            for j in xrange(i, self.dim):
                self.data[i].append(float(mat[i,j])/self._ratio)
    
    mat = property(_get_mat, _set_mat)


    def empty_copy(self):
        """
        returns copy of self with no data
        """
        return  CovMatApri(dim=self.dim, band=self.band,
                           apriori=self.apriori,
                           aposteriori=self.aposteriori,
                           useApriori=self.useApriori)


if __name__ == "__main__":
    cd=CovMatApri()
    cd.dim = 4 # set dimension of matrix
    cd.band = 3 # set band width
    cd.apriori = 10.0
    cd.aposteriori = 20.0
    cd.useApriori = True
    # insert values of covariance matrix
    for i in range(4):
        for j in range(4-i):
            cd.append_value(2)
    
    print cd.data

    print cd
    print cd.var
    print cd.stdev
    print cd.get_var(0)
    print cd.get_cov(0,1)

    cd.set_var(0, 10)
    cd.set_cov(0, 1, 10)
    
    print cd.data
    
    cd.var = [1,2,3,4]
    print cd.data
    cd.stdev = [1,2,3,4]
    print cd.data
    print cd.make_gama_xml()

    cd.useApriori = False
    print cd
    print cd.var
    print cd.stdev
    print cd.get_var(0)
    print cd.get_cov(0,1)

    cd.set_var(0, 10)
    cd.set_cov(0, 1, 10)
    
    print cd.data
    
    cd.var = [1,2,3,4]
    print cd.data
    cd.stdev = [1,2,3,4]
    print cd.data
    print cd.make_gama_xml()



    # Numpy matrix
    print "numpy matrix"
    print cd.mat
    from numpy import zeros, float_
    m = zeros(shape=(4,4), dtype=float_)
    cd.mat = m+5
    print cd.data
    cd.useApriori = True
    cd.mat = m+5
    print cd.data
    print cd.mat

