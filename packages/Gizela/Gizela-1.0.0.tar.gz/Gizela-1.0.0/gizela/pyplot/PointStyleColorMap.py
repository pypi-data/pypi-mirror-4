# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.pyplot.PointStyle import PointStyle

import matplotlib.colors as colors
import matplotlib.cm as cm  # color maps

class PointStyleColorMap(PointStyle):
    "point style with color of point from color map"
    
    def __init__(self, cmapName="hsv", indexMin=0, indexMax=1):
        """
        cmapName: color map name
        indexMin, indexMax: mininal and maximal value of index used
                            used for normalization
        """

        self.cmap = cm.cmap_d[cmapName] # color map instance
        self.norm = colors.normalize(indexMin, indexMax) # normalize instance
        
        self.set_color(indexMin) # implicit setting of point color

    def set_index(self, index):
        """
        sets color of point according to index
        from range indexMin:indexMax from colormap
        """

        color = self.cmap(self.norm(index))
        self.lineProp["markerfacecolor": color]

