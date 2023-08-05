# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: CovMat.py 119 2011-01-11 23:44:34Z tomaskubin $


from gizela.util.Error import Error


class CovMatError(Error):
    '''Exception for CovMat class'''
    pass

class CovMat(object):
    '''class for variance-covariance matrix
    data stored in list of lists by rows
    '''

    __slots__ = ["_data", "_dim", "_band", 
            "_rowlen", "_row", "_col", "_allElements"]

    def __init__(self, dim=0, band=None):
        '''dim  ... dimension of covariance matrix
        band ... band width of covariance matrix
        '''
        
        self._set_dim(dim)  # initialization of list of lists
        if band is None:
            band = dim - 1
        self._set_band(band)
        self._rowlen=band+1 # length of row vector
        self._row=0         # row index
        self._col=0         # index in actual row - 0 means 
                            # diagonal element 
        self._allElements=False # are there all elements in covmat
                                # appended by method append_value?

    def _get_dim(self): return self._dim
    def _get_band(self): return self._band
    def _set_dim(self, dim): 
        '''sets dimension of matrix and initialize list of rows'''
        if dim < 0: raise CovMatError, "dim < 0"
        self._dim = dim
        # inicialization
        self._data = [[] for i in xrange(dim)]
            # list of lists of covariance matrix
            # values by rows
            # initialization of list of rows
    
    def _set_band(self, band):
        '''sets band width of matrix'''
        if band < -1: raise CovMatError, "band < -1"
        #if band > self._dim - 1: raise CovMatError, "band > dim -1"
        self._band = band
        self._rowlen = band + 1
    
    dim = property(_get_dim, _set_dim)
    band = property(_get_band, _set_band)

    def extend_dim(self, num=1):
        "extends dimension by mun of current covmat"
        [self._data.append([]) for i in xrange(num)]
        self._dim += num
        self._allElements = False
        self._rowlen = min(self._band + 1, self.dim - self._row)

    def _get_var(self): 
        #return [len(row)==0 and None or row[0] for row in self._data]
        return [row[0] for row in self._data]
    
    def _set_var(self, var):
        #if type(var) == int or type(var) == float:
        #    if self._dim > 0:
        #        self._data[0][0] = var
        #        return
        if len(var) > self._dim:
            raise CovMatError, "The number of variances exceeds dimension"
        for i in xrange(len(var)):
            if len(self._data[i]) == 0:
                self._data[i].append(var[i])
            else:
                self._data[i][0] = var[i]

    var = property(_get_var, _set_var)

    #def _get_cov(self): 
    #    cov = []
    #    for i in xrange(self.dim):
    #        cov.extend(self.data[i][1:min(self.dim-i, self.band+1)])
    #    return cov

    #cov = property(_get_cov)

    def _get_data(self): return self._data
    def _set_data(self, data):
        if type(data) != list:
            raise CovMatError, "List expected for data"
        if len(data) != self._dim:
            raise CovMatError, "The number of rows and dimension are not the same"
        self._data = data

    data = property(_get_data, _set_data)

    def _get_stdev(self): 
        from math import sqrt
        var = self._get_var()
        return [sqrt(row) for row in self._get_var()]

    def _set_stdev(self, stdev):
      #  if type(stdev) == int or type(stdev) == float:
      #      self._set_var(stdev*stdev)
      #  else:
        self._set_var([d*d for d in stdev])

    stdev = property(_get_stdev, _set_stdev)
    
    def make_test(self):
        '''counts elements in covariance matrix and 
        tests dimension and band width
        OK - False'''

        sum = 0
        for row in self._data: sum += len(row)
        num = self._dim*(self._dim + 1)/2 - \
                (self._dim - self._band)*\
                (self._dim - self._band - 1)/2
        #import sys
        #print >>sys.stderr, "SUM:", sum, " NUM:", num
        return sum != num

    def is_readed(self):
        return self._allElements

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
        self._data[self._row].append(val)
        self._col += 1

    def set_var(self, row, var):
        '''sets variance var in row in matrix'''
        if row >= self._dim:
            raise CovMatError("Row number (%i) exceeds dimension (%i)" %\
                    (row, self._dim))
        if len(self._data[row]) == 0:
            self._data[row]=[var]
        else:
            self._data[row][0] = var

    def set_cov(self, row, col, cov):
        '''sets covariance cov in row, col in matrix'''
        if row >= self._dim:
            raise CovMatError("Row number (%i) exceeds dimension (%i)" %\
                    (row, self._dim))
        if col >= self._dim:
            raise CovMatError("Column number exceeds dimension")
        if abs(row-col) > self._band:
            raise CovMatError, "Covariance (%i,%i) exceeds band width (%i)"\
                    % (row, col, self._band)
        if col < row:
            tmp = row; row = col; col = tmp
        #print col, "**", row
        colr = col - row
        rowlen = len(self._data[row])
        if rowlen < colr + 1:
            self._data[row].extend([None for i in range(len(self._data[row]), colr)])
            self._data[row].append(cov)
        else:
            self._data[row][colr] = cov


    def get_var(self, row):
        '''returns variance
        row ... index of row - starts from 0'''
        if type(row) != int:
            raise CovMatError("Row number (%s) must be an integer" % row)
        if row >= self._dim:
            raise CovMatError("Row number (%i) exceeds dimension (%i)" %\
                    (row, self._dim))
        try:
            return self._data[row][0]
        except IndexError:
            return None
            #raise CovMatError("No variance (row=%i) set" % row)

    def get_cov(self, row, col):
        '''returns covariance
        row, col ... index of row and column - starts from 0'''
        if type(row) != int:
            raise CovMatError("Row number (%s) must be an integer" % row)
        if type(col) != int:
            raise CovMatError("Column number (%s) must be an integer" % col)
        if row >= self._dim:
            raise CovMatError("Row number (%i) exceeds dimension (%i)" %\
                    (row, self._dim))
        if col >= self._dim:
            raise CovMatError("Column number exceeds dimension")
        #if abs(row-col) > self._band:
        #    raise CovMatError("Covariance (%i,%i) exceeds band width" % (row,col))
        try:
            if col > row : # upper triangle
                return self._data[row][col-row]
            else: # lower triangle or diagonal
                return self._data[col][row-col]
        except IndexError:
            return 0.0
            #return None

    def __add__(self, other):
        'addition of two covariance matrix'
        if self.dim != other.dim:
            raise CovMatError("Cannot add up matrix with different dimensions")
        covmat = self.__class__(self.dim, self.band)
        if self.band > other.band:
            covmat.band = other.band
        else:
            covmat.band = self.band
        #if self.band != other.band:
        #    raise CovMatError("Cannot add up matrix witdh different band widths")
        covmat._data = []
        for row1, row2 in zip(self._data, other.data):
            row = []
            for val1, val2 in zip(row1, row2):
                if val1 != None and val2 != None: row.append(val1 + val2)
                else: row.append(None)
            covmat._data.append(row)

        return covmat

       # def get_sub_cov_mat(self, dim, band=None, row=0):
       #     """
       #     returns main submatrix with dimension dim 
       #     starting at row row (first index is zero)
       #     """
       #     if not self._allElements:
       #             raise CovMatError, "All elements in covariance matrix are not present"
       #     
       #     if dim+row > self._dim:
       #             raise CovMatError, "Dimension (dim + row) exceeds dimension of covariance matrix %i > %i" % (dim+row, self._dim)
       #     if dim == self._dim:
       #             return self
       #     if band == None:
       #             band = dim - 1
       #     if band >= dim:
       #             raise CovMatError, "Band width exceeds dim-1"
       #     if band > self._band:
       #             band = self._band
       #     cmat = CovMat(dim=dim, band=band)
       # 
       #     for i in xrange(dim):
       #         cmat.data[i] = self.data[row+i][:min(dim-i, band+1)]
       # 
       #     return cmat
        
    def slice(self, dim, band=None):
        """
        slices covariance matrix to dimension dim and band width band 
        """
        if not self._allElements:
            print self
            print self.data
            raise CovMatError, "All elements in covariance matrix are not present"
        
        if dim > self._dim:
                raise CovMatError, "Dimension dim exceeds dimension of covariance matrix %i > %i" % (row, self._dim)
        if dim == self._dim:
                return
        if band == None:
                band = dim - 1
        if band >= dim:
                raise CovMatError, "Band width exceeds dim-1"
        if band > self._band:
                band = self._band
        
        for i in xrange(dim):
            self._data[i] = self._data[i][:min(dim-i, band+1)]
        for i in xrange(dim, self._dim):
            self._data.pop()
        
        self._dim = dim
        self._band = band


    def __str__(self):
        return "dim:  %i  band: %i" % (self._dim, self._band)

    def __iter__(self): return iter(self._data)

    def make_gama_xml(self):
        str = ['<cov-mat dim="%i" band="%i">' % (self._dim, self._band)]
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
                        str1.append("%14.7e" % (val*1e6))
            str.append("  ".join(str1))
        str.append("</cov-mat>")

        return "\n".join(str)
        

    #def __mul__(self, other):
    #    " covmat * scalar "
    #    if type(other) == int or type(other) == float:
    #        cm = CovMat(dim=self.dim, band=self.band)
    #        data = self.data
    #        for i in xrange(len(data)):
    #            for j in xrange(len(data[i])):
    #                data[i][j] *= other
    #        cm._data = data
    #        return cm
    #    else:
    #        raise CovMatError, "Divison by unknown type '%s'" % type(other)

    def _get_mat(self):
        "returns NumPy matrix of self"

        from numpy import zeros, diagonal, diag, matrix, float_

        a = zeros(shape=(self._dim,self._dim), dtype=float_)
        
        i = 0
        for row in self.data:
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
                self.data[i].append(float(mat[i,j]))
    
    mat = property(_get_mat, _set_mat)

    def transform_(self, tran):
        "transformation of covariance matrix"
        
        # maximum band width
        self.band = self.dim - 1
        #print "MAT", self.data
        self.mat = tran.transform_cov_mat(self)
        #print "MAT", self.data


    def scale_(self, factor):
        "scale covariance matrix with factor**2"
        f2 = factor**2
        self._data = [[i*f2 for i in row] for row in self._data]
        #for row in self._data:
            #row = [i*f2 for i in row]


    def empty_copy(self):
        """
        returns copy of self with no data
        """
        return  CovMat(dim=self.dim, band=self.band)



if __name__ == "__main__":
    cd=CovMat()
    cd.dim = 6 # set dimension of matrix
    cd.band = 5 # set band width
    print cd
    # insert values of covariance matrix
    for i in range(6):
        for j in range(6-i):
            cd.append_value(i+j)
    
    print cd.data

    print cd.get_var(2)
    print cd.get_cov(2,2)
    print cd.get_cov(1,0)
    print cd.get_cov(0,1)
    
    cdd = cd + cd
    print cdd
    print cdd.data

    # adding covmats with different band widths
    print "different band widths"
    cd3 = CovMat(dim=6, band=1)
    for i in xrange(2*5+1): cd3.append_value(i)
    print cd.data
    print cd3.data
    souc = cd3 + cd
    print souc
    print souc.data
    print souc.make_gama_xml()

    # using set_ functions
    print "using set_ functions"
    cd2=CovMat(dim=6,band=5)
    #cd2.get_var(0)
    cd2.set_var(0,0.0)
    cd2.set_var(1,10)
    cd2.set_var(4,40)
    cd2.set_var(5,50)
    cd2.set_cov(3,3,30)
    cd2.set_cov(2,3,20)
    cd2.set_cov(0,3,0.3)
    print cd2.get_cov(4,5)
    print cd2
    print cd2.data
    print cd2.make_gama_xml()

    cdd2 = cd + cd2
    cdd3 = cd2 + cd
    print cdd2.data
    print cdd3.data

    # multiplication
    #print cd.data
    #cd *= 2.0
    #print cd.data
    
    # iterator
    print "iterator"
    for row in cd:
        for val in row:
            print "value: %.1f" % val
    
    # get vars and covs
    print "get vars and covs"
    print cd.var
    #print cd.cov
    print cd3
    print cd3.data
    print cd3.var
    #print cd3.cov

    # Numpy matrix
    print "numpy matrix"
    print cd.mat
    from numpy import zeros, float_
    m = zeros(shape=(6,6), dtype=float_)
    cd.mat = m
    print cd.data

    # transformation
    print "transformation"
    from gizela.tran.Tran3D import Tran3D
    tr = Tran3D()
    from math import pi
    tr.rotation_xyz(pi/2, pi/2, pi/2)
    cm =CovMat(dim=3)
    cm.data=[[1.0, 2.0, 3.0], [4.0, 5.0], [6.0]]
    print cm.data
    cm.transform_(tr)
    print cm.data

    # empty copy
    print cm
    print cm.data
    new_cm = cm.empty_copy()
    print new_cm
    print new_cm.data
