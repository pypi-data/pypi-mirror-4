# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

import matplotlib.colors as colors
import matplotlib.cm as cm  # color maps

class ColorMap(object):
    "color map extension"
    
    def __init__(self, cmapName="hsv", indexMin=0, indexMax=1):
        """
        cmapName: color map name
        indexMin, indexMax: mininal and maximal value of index used
                            used for normalization
        """

        #self.cmap = cm.cmap_d[cmapName] # color map instance
        self.cmap = cm.get_cmap(cmapName) # color map instance
        self.norm = colors.normalize(indexMin, indexMax) # normalize instance
        
    def get_color(self, index):
        """returns color"""
        return self.cmap(self.norm(index))

