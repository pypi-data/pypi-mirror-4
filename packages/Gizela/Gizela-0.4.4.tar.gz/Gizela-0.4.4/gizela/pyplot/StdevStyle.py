# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.pyplot.PlotStyle import PlotStyle

class StdevStyle(PlotStyle):
    """
    properties for drawind confidence interval
    for standart deviation
    """
           
    # line properties for 1stdev interval
    lineProp = {"linestyle": "solid",
                "linewidth": 10,
                "alpha": 0.3,
                "color": "green",
                "marker": "",
                "zorder":-100
               }
    
