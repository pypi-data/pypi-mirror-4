# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: TranBase.py 119 2011-01-11 23:44:34Z tomaskubin $


from gizela.util.Error     import Error
#from gizela.text.TextTable import TextTable


class TranBaseError(Error): pass


class TranBase(object):
    '''
    base class for transformations
    '''
    def __init__(self, dim, trmat):
        self._dim = dim # dimension of transformation
        self.trmat = trmat # transformation matrix

    def _get_matrot(self):
        "return matrix of rotation"
        return self.trmat[0:self.dim, 0:self.dim]

    matrot = property(_get_matrot)

    def _get_dim(self): return self._dim

    dim = property(_get_dim)
        
    def transform_cov_mat(self, covmat):
        """
        transforms covariance matrix

        covmat: CovMat instance
        """

        if self.dim != covmat.dim:
            raise TranBaseError,\
                    "Dimension of covmat and transform are not equal (%i!=%i)"\
                                    % (covmat.dim, self.dim)

        mr = self.matrot

        return mr * covmat.mat * mr.T


    def mirror_y(self):
        "set y to -y"
        self.trmat[1,:] *= -1

    def __call__(self):
        raise NotImplementedError, "Method __call__ not implemented"
