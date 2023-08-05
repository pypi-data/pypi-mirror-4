# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.pyplot.PlotStyle import PlotStyle

class ConfStyle(PlotStyle):
    """
    properties for drawind confidence interval
    """
           
    # line properties for confidence interval
    lineProp = {"linestyle": "solid",
                "linewidth": 10,
                "alpha": 0.3,
                "color": "red"
               }
