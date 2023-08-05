# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.pyplot.PlotStyle import PlotStyle

class ErrEllStyle(PlotStyle):
    """
    properties for 
        error ellipse
    """
           
    patchProp = {"facecolor": "blue",
                 "edgecolor": "blue",
                 "alpha": 0.3,
                 "zorder":-100
                }

