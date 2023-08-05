# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$


from gizela.util.Error import Error
from gizela.data.PointCartCovMat import PointCartCovMat
from gizela.stat.displ_test_text_table import displ_text_table

class PointDisplBaseError(Error): pass


class PointDisplBase(object):
    """
    base class for classes of points with displacements
    """

    def __init__(self, id, dx=None, dy=None, dz=None, 
                 index=None, covmat=None, textTable=None):
        """
        dx, dy, dz: displacements
        covmatd: covariance matrix of displacement
        """

        if textTable == None:
            textTable = displ_text_table()

        self.displ = PointCartCovMat(id=id, x=dx, y=dy, z=dz,
                                     index=index, covmat=covmat,
                                     textTable=textTable)

    def set_displacement(self, displ):
        """
        displ: PointCartCovMat instance with displacements
        """

        if not isinstance(displ, PointCartCovMat):
            raise PointDisplBaseError, "PointCartCovMat instance expected"

        # set id
        displ.id = self.displ.id
        
        # set textTable
        #displ.textTable = self.displ.textTable
        
        self.displ = displ
    

    def __str__(self):
        return self.displ.__str__()

if __name__ == "__main__":

    p = PointDisplBase(id="A", dx=1.0, dy=5.0)
    p.displ.var = (1,2)

    print p
