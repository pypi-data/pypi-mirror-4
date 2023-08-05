# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.pyplot.PlotStyle import PlotStyle

class VecStyle(PlotStyle):
    """
    properties for vector drawings
    """
           
    lineProp = {"linestyle": "-",
                "linewidth": 1,
                "alpha": 1,
                "color": "black",
                "zorder": -10
               }
    miscProp = {"lineProp": {"linestyle": ":",
                             "linewidth": 1,
                             "alpha": 1,
                             "color": "black",
                             "zorder": -10
                            }
               }

    #markerProp = {"marker": 'o',
    #              "markersize": 5,
    #              "markerfacecolor": "white",
    #              "markeredgewidth": 1,
    #              "markeredgecolor": "black",
    #              "markevery": (1,1)
    #             }

