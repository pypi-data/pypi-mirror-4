# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$


from gizela.data.PointLocalGama import PointLocalGama
from gizela.stat.PointDisplBase import PointDisplBase
from gizela.stat.TestResult import TestResult
from gizela.data.GamaCoordStatus import GamaCoordStatus
from gizela.stat.DisplacementTestType import DisplacementTestType
from gizela.stat.displ_test_text_table import displ_test_text_table


class PointLocalGamaDisplTest(PointLocalGama, PointDisplBase, TestResult):
    """
    class for gama-local point with displacement and test results
    point: x, y, z, status, covmat
    displ: dx, dy, dz, dcovmat
    test: testStat, testPassed, testPValue, testReliability, testType
    """

    def __init__(self, id,
                 x=None, y=None, z=None,
                 status=GamaCoordStatus.unused,
                 covmat=None, index=None,
                 dx=None, dy=None, dz=None,
                 dcovmat=None, dindex=None,
                 testStat=None,
                 testPassed=None, 
                 testPValue=None,
                 testReliability=None,
                 testType=DisplacementTestType.none,
                 textTable=None,
                 epochIndex=None):

        if isinstance(id, PointLocalGama):
            p = id
            id = p.id; x = p.x; y = p.y; z = p.z;
            status = p.status; covmat = p.covmat; index = p.index
        
        if textTable == None:
            textTable = displ_test_text_table()

        PointLocalGama.__init__(self, id=id, x=x, y=y, z=z,
                                status=status, covmat=covmat, index=index)

        PointDisplBase.__init__(self, id=id, dx=dx, dy=dy, dz=dz,
                                covmat=dcovmat, index=dindex)
        
        TestResult.__init__(self, testStat=testStat, testPassed=testPassed,
                            testPValue=testPValue,
                            testReliability=testReliability,
                            testType=testType, textTable=textTable)

        self.epochIndex = epochIndex


    def make_table_row(self): 
        row = [self.id, self.x, self.y, self.z]
        row.append(self.get_status_string())
        row.extend(self.var)
        row.extend([self.displ.x, self.displ.y, self.displ.z])
        row.extend(self.displ.var)
        row.extend([self.testStat, self.testPassed, self.testPValue,
                    self.testReliability, self.get_test_type_string(),
                    self.get_test_dim()])

        return self.textTable.make_table_row(row)



if __name__ == "__main__":

    p0 = PointLocalGama(id="AB", x=1e6, y=2e6, z=3e6)
    p = PointLocalGamaDisplTest(id="AB", x=1e6, y=2e6, z=3e6)
    p = PointLocalGamaDisplTest(p0)
    p.set_test_result(testPValue=0.97, testType=DisplacementTestType.xyz,
               testPassed=True)

    from gizela.data.PointCartCovMat import PointCartCovMat
    p.set_displacement(PointCartCovMat(id=None, x=0.1, y=0.2, z=0.3))

    print p

    from gizela.data.PointCart import PointCart
    print isinstance(p, PointCart)
