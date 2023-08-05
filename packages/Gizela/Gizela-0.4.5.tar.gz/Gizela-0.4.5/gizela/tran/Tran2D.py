# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: Tran2D.py 117 2011-01-05 23:28:15Z tomaskubin $


from gizela.util.Error import Error
from gizela.tran.TranBase import TranBase

import numpy as np


class Tran2DError(Error): pass


class Tran2D(TranBase):
    """
    class for 2D affine transformation
    """

    def __init__(self):
        
        
        trmat = np.mat(np.eye(3))
        # r11 r12 tx
        # r21 r22 ty
        # 0   0   1
        #
        # transformation matrix for homogenous coordinates
        # [x, y, 1]

        super(Tran2D, self).__init__(dim=2, trmat=trmat)
    

    def set_trn_key(self, trnKey):
        """
        sets transformation matrix with trnKey
        trnKey: (a,b,c,d,e,f)
        
        trmat=[[a, b, e]
               [c, d, f]
               [0, 0, 1]]
        """

        if len(trnKey) != 6:
            raise Tran2DError, "trnKey with six items expected"

        self.trmat[0,0:2] = trnKey[0:2]
        self.trmat[1,0:2] = trnKey[2:4]
        self.trmat[0,2] = trnKey[4]
        self.trmat[1,2] = trnKey[5]


    def transform_xy(self, x, y):
        """
        transformation of coordinates x, y
        returns tuple of coordinates
        """
        cmat = np.mat([x, y, 1]).T
        cmattr = self.trmat * cmat
        return float(cmattr[0]), float(cmattr[1])

    def __call__(self, x, y):
        """
        transform coordinates x, y
        """
        return self.transform_xy(x=x, y=y)

    def translation_xy(self, tx, ty):
        "sets tx and ty"
        self.trmat[0,2] = tx
        self.trmat[1,2] = ty

    def rotation_(self, theta):
        "sets rotation matrix, theta in radians"
        from math import sin, cos
        self.trmat[0,0:2] =  cos(theta), sin(theta)
        self.trmat[1,0:2] = -sin(theta), cos(theta)

    def scale_(self, scale):
        "sets scale factor - translations not affected"
        self.trmat[0:2,0:2] *= scale

    def __str__(self):
        return self.trmat.__str__()

if __name__ == "__main__":

    tr = Tran2D()
    print tr
    
    # translation
    tr.translation_xy(10,20)
    print tr

    # rotation
    from math import pi
    tr.rotation_(pi)
    print tr
    
    # transformation
    x, y = tr.transform_xy(5,6)
    print x, y
    x, y = tr(5, 6)
    print x, y
    
    #scale
    tr.scale_(2)
    print tr
    x, y = tr.transform_xy(5,6)
    print x, y
