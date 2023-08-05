# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$


from gizela.util.Error import Error
from gizela.stat.displ_test_text_table import test_text_table
from gizela.stat.DisplacementTestType import DisplacementTestType


class TestResult(object):
    """
    class for results of statistical testing
    """

    def __init__(self,
                 testStat=None,
                 testPassed=None, 
                 testPValue=None,
                 testReliability=None,
                 testType=DisplacementTestType.none,
                 textTable=None):
        """
        tstat: test statistic
        passed: result of test passed/failed
        pvalue: p-value of test
        reliability: reliability of test
        type: type of test
        """

        if textTable == None:
            textTable = test_text_table()

        self.testStat=testStat
        self.testPassed=testPassed
        self.testPValue=testPValue
        self.testReliability=testReliability
        self.testType=testType
        self.textTable=textTable

    
    def set_test_result(self, testStat=None, testPassed=None, testPValue=None, 
                        testReliability=None, testType=None):
        self.testStat=testStat
        self.testPassed=testPassed
        self.testPValue=testPValue
        self.testReliability=testReliability
        self.testType=testType


    def get_test_type_string(self):
        return DisplacementTestType.get_string(self.testType)

    
    def get_test_dim(self):
        return DisplacementTestType.get_dim(self.testType)


    def make_table_row(self):
        return self.textTable.make_table_row(self.testStat, 
                                                 self.testPValue,
                                                 self.testReliability,
                                DisplacementTestType.get_string(self.testType),
                                DisplacementTestType.get_dim(self.testType),
                                    self.testPassed and "passed" or "failed")

        
    def __str__(self):
        return "".join([self.textTable.make_table_head(),
                        self.make_table_row(),
                        self.textTable.make_table_foot()])

if __name__ == "__main__":

    tr = TestResult(testStat=2.5434,
                    testPassed=True,
                    testPValue=0.923,
                    testReliability=0.952,
                    testType=DisplacementTestType.xy)

    print tr

    tr.set_test_result(testPValue=0.99)
    print tr
