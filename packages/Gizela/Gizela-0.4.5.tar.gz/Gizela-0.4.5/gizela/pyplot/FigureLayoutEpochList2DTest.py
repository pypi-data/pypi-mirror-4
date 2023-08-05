# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.pyplot.FigureLayoutEpochList2D import FigureLayoutEpochList2D
from gizela.pyplot.PlotPoint import PlotPoint
#from gizela.util.Error import Error

#class FigureLayoutEpochList2DError(Error): pass


class FigureLayoutEpochList2DTest(FigureLayoutEpochList2D):
    """
    class with layout for EpochList with points tested
    """

    def __init__(self, 
                 figScale=None,
                 displScale=1.0,
                 title="",
                 subtitle="",
                 confProb=0.95,
                 configFileName=None):
        """
        data: EpochList instance
        figScale: scale ratio of axes for data
        displScale: relative scale ratio for displacements
        title: figure title
        subtitle: figure subtitle
        confProb: confidence probability
        configFileName: file name of configuration file
        """
        
        super(FigureLayoutEpochList2DTest,
              self).__init__(figScale=figScale, 
                             displScale=displScale,
                             title=title,
                             subtitle=subtitle,
                             confProb=confProb,
                             configFileName=configFileName)

    def plot_point_error_ellipse(self, point):
        #print "point", point.id, ":", point.testPassed
        if point.testPassed is None:
            PlotPoint.plot_point_error_ellipse(self, point,
                           self.errScale*self.stdev.get_conf_scale_2d(),
                           style="errorEllipseStyle")
        elif point.testPassed:
            PlotPoint.plot_point_error_ellipse(self, point,
                           self.errScale*self.stdev.get_conf_scale_2d(),
                           style="errorEllipsePassedStyle")
        else:
            PlotPoint.plot_point_error_ellipse(self, point,
                           self.errScale*self.stdev.get_conf_scale_2d(),
                           style="errorEllipseFailedStyle")

    def plot_point_error_z(self, point):
        if point.testPassed is None:
            PlotPoint.plot_y_stdev(self, point.x, point.y,
                   self.errScale*self.stdev.get_conf_scale_1d()*point.stdevz,
                   style="errorZStyle")
        elif point.testPassed:
            PlotPoint.plot_y_stdev(self, point.x, point.y,
                   self.errScale*self.stdev.get_conf_scale_1d()*point.stdevz,
                   style="errorZPassedStyle")
        else:
            PlotPoint.plot_y_stdev(self, point.x, point.y,
                   self.errScale*self.stdev.get_conf_scale_1d()*point.stdevz,
                   style="errorZFailedStyle")


    def append_comment_testType(self, epochList):
        if epochList.testType is None:
            testType = "# coord"
        else:
            from gizela.stat.DisplacementTestType import DisplacementTestType
            testType = DisplacementTestType.get_string(epochList.testType)
            
        label = self.config["testType"]["label"]
        #print "Label:", label, testType
        self.append_comment_line(label + ": " + testType)
