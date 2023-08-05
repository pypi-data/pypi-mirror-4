# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: Tran3D.py 76 2010-10-22 21:19:21Z tomaskubin $


from gizela.util.Error import Error
from gizela.tran.TranBase import TranBase

import numpy as np


class Tran3DError(Error): pass


class Tran3D(TranBase):
    """
    class for 3D affine transformation
    """

    def __init__(self):
        
        trmat = np.mat(np.eye(4))
        # r11 r12 r13 tx
        # r21 r22 r23 ty
        # r31 r32 r33 tz
        # 0   0   0   1
        #
        # transformation matrix for homogenous coordinates
        # [x, y, z, 1]
        
        super(Tran3D, self).__init__(dim=3, trmat=trmat)

    def transform_xyz(self, x, y, z):
        """
        transformation of coordinates x, y, z
        returns tuple of coordinates
        """
        
        cmat = np.mat([x, y, z, 1]).T
        cmattr = self.trmat * cmat
        return float(cmattr[0]), float(cmattr[1]), float(cmattr[2])

    def __call__(self, x, y, z):
        """
        transform coordinates x, y, z
        """
        return self.transform_xyz(x=x, y=y, z=z)

    def set_inverse(self):
        self.trmat = self.trmat.I 

    def translation_xyz(self, tx, ty, tz):
        "sets translations tx, ty and tz"
        
        self.trmat[0,3] = tx
        self.trmat[1,3] = ty
        self.trmat[2,3] = tz

    def rotation_xyz(self, alpha, beta, gamma):
        """
        sets rotation matrix, angles in raians
        alpha - x axis, beta - y axis, gamma - z axis
        """
        
        from math import sin, cos
        rx = np.mat([[1.0,    0.0,          0.0    ],
                     [0.0,  cos(alpha),  sin(alpha)],
                     [0.0, -sin(alpha),  cos(alpha)]])

        ry = np.mat([[cos(beta),  0.0, -sin(beta)],
                     [  0.0,      1.0,    0.0    ],
                     [sin(beta),  0.0,  cos(beta)]])

        rz = np.mat([[ cos(gamma),  sin(gamma),  0.0],
                     [-sin(gamma),  cos(gamma),  0.0],
                     [   0.0,         0.0,       1.0]])

        self.trmat[0:3,0:3] = ry*rx*rz

    def scale_(self, scale):
        "sets scale factor - translations not affected"
        self.trmat[0:3,0:3] *= scale

    def __str__(self):
        return self.trmat.__str__()

if __name__ == "__main__":

    tr = Tran3D()
    print tr
    
    # translation
    tr.translation_xyz(10, 20, 30)
    print tr
    
    # transformation
    x, y, z = tr.transform_xyz(5, 6, 7)
    print x, y, z
    x, y, z = tr(5, 6, 7)
    print x, y, z

    # rotation
    from math import pi
    tr.rotation_xyz(pi, pi, pi)
    print tr
    x, y, z = tr.transform_xyz(5, 6, 7)
    print x, y, z
    
    # scale
    tr.scale_(2)
    print tr
    x, y, z = tr.transform_xyz(5, 6, 7)
    print x, y, z

    # testing
    lat = 50.091153311111
    lon = 14.401833202777
    
    from math import pi
    alpha = 0
    beta = (lat - 90)*pi/180
    gamma = (lon - 180)*pi/180

    tr = Tran3D()
    tr.rotation_xyz(alpha, beta, gamma)

    x =  354.799
    y = -465.803
    z = -164.077

    xx, yy, zz = tr.transform_xyz(x, y, z)
    
    xx_ = -2.80000067792702e+02
    yy_ =  5.39411154139838e+02
    zz_ =  2.02878279914393e+01

    print xx - xx_, yy - yy_, zz - zz_
