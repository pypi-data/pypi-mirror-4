# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.pyplot.PlotStyle import PlotStyle

import matplotlib.dates


class DateStyle(PlotStyle):
    """
    properties for drawind with date x axis
    """
           
    lineProp = {"linestyle": "solid",
                "linewidth": 1,
                "alpha": 1,
                "color": "black",
                "marker": 'o',
                "markersize": 5,
                "markerfacecolor": "red",
                "markeredgewidth": 1,
                "markeredgecolor": "black"
               }

    miscProp = {"majorTicksLocator" : matplotlib.dates.YearLocator(),
                "lineProp": {"linestyle": ":", # property for missing epoch
                             "linewidth": 1,
                             "alpha": 1,
                             "color": "black",
                             "marker": "",
                            }
               }

