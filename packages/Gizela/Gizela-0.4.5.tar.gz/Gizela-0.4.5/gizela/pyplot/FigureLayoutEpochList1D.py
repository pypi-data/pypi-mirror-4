# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.pyplot.FigureLayoutEpochList2D import FigureLayoutEpochList2D
from gizela.pyplot.PlotPoint import PlotPoint
from gizela.util.Error import Error


class FigureLayoutEpochList1DError(Error): pass


class FigureLayoutEpochList1D(FigureLayoutEpochList2D):
    """
    use for graph with dates on x axis 
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
        
        super(FigureLayoutEpochList1D,
              self).__init__(figScale=None, 
                             displScale=displScale,
                             title=title,
                             subtitle=subtitle,
                             confProb=confProb,
                             configFileName=configFileName)

    def append_comment_figScale(self, par): pass
    def append_comment_axesOri(self, par): pass
    def append_comment_displScale(self, unusedParameter):
        label = self.config["displScale"]["label"]
        self.append_comment_line(label + ": " + \
         self.get_scale_ratio_string(self.errScale))

    def update_(self, epochList):
        "update figure settings and y axes"
        
        self.set_color_style(epochList)
        self.set_scale_ratio_y(self.errScale) # set scale ratio for y axis
        self.set_comment(epochList)
        self.set_legend(epochList)

        

    

