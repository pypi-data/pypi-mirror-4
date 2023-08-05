# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.pyplot.FigureLayoutEpochList1D import FigureLayoutEpochList1D
from gizela.pyplot.PlotPoint import PlotPoint
#from gizela.util.Error import Error


#class FigureLayoutEpochList1DError(Error): pass


class FigureLayoutEpochList1DTest(FigureLayoutEpochList1D):
    """
    use for graph with dates on x axis 
    with test results
    """

    def __init__(self, 
                 displScale=1.0,
                 title=None,
                 subtitle=None,
                 confProb=0.95,
                 configFileName=None):
        """
        displScale: relative scale ratio for displacements
        title: figure title
        subtitle: figure subtitle
        confProb: confidence probability
        configFileName: file name of configuration file
        """
        
        super(FigureLayoutEpochList1DTest,
              self).__init__(displScale=displScale,
                             title=title,
                             subtitle=subtitle,
                             confProb=confProb,
                             configFileName=configFileName)

    def plot_point_z_stdev(self, point, x):
        if point.testPassed is None:
            PlotPoint.plot_y_stdev(self, x, point.z, 
                   self.errScale*self.stdev.get_conf_scale_1d()*point.displ.stdevz,
                   style="stdevStyle")
        elif point.testPassed:
            PlotPoint.plot_y_stdev(self, x, point.z, 
                   self.errScale*self.stdev.get_conf_scale_1d()*point.displ.stdevz,
                   style="stdevPassedStyle")
        else:
            PlotPoint.plot_y_stdev(self, x, point.z, 
                   self.errScale*self.stdev.get_conf_scale_1d()*point.displ.stdevz,
                   style="stdevFailedStyle")
    
    
    def append_comment_testType(self, epochList):
        if epochList.testType is None:
            testType = "# coord"
        else:
            from gizela.stat.DisplacementTestType import DisplacementTestType
            testType = DisplacementTestType.get_string(epochList.testType)
            
        label = self.config["testType"]["label"]
        #print "Label:", label, testType
        self.append_comment_line(label + ": " + testType)
