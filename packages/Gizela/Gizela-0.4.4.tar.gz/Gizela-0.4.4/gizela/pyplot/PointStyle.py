# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.pyplot.PlotStyle import PlotStyle

class PointStyle(PlotStyle):
    """
    properties for 
        point marker
        point text label (id)
    """
           
    # marker
    lineProp = {"marker": 'o',
                "markersize": 5,
                "markerfacecolor": "red",
                "markeredgewidth": 1,
                "markeredgecolor": "black",
                "alpha": 1.0
               }

    # label
    textProp = {#"fontproperties": xxx,
                "fontsize": "medium",
                "fontstyle": "normal",
                "fontweight": "normal",
                "verticalalignment": "top",
                "horizontalalignment": "left"
               }
    
    miscProp = {"textOffsetX" : 5, #points (1/72inch)
                "textOffsetY" : 5  #points (1/72inch)
               }

    def get_text_trans(cls, figure):
        "return transformation for text labels"
        from matplotlib.transforms import offset_copy
        return offset_copy(figure.gca().transData, figure.figure, 
                           cls.miscProp["textOffsetX"], 
                           cls.miscProp["textOffsetY"], 
                           units="points")

    
    def set_point_color(self, faceColor, edgeColor="black"):
        "sets color of point marker"
        self.lineProp["markerfacecolor"] = faceColor
        self.lineProp["markeredgecolor"] = edgeColor

    
    def set_point_size(self, size):
        "sets point size: size is in milimeters"
        self.lineProp["markersize"] = size / 25.4 * 72.0 # points

    
    def set_label_size(self, size):
        "sets point label size: size is in milimeters"
        self.textProp["fontsize"] = size / 25.4 * 72.0




if __name__ == "__main__":

    ps = PointStyle()
    ps.lineProp["alpha"] = 2.0

    print PointStyle.lineProp["alpha"]
    print ps.lineProp["alpha"]

    ps.set_point_size(1)
    print PointStyle.lineProp["markersize"]
    print ps.lineProp["markersize"]

    ps.set_point_color("xxx")
    print PointStyle.lineProp["markerfacecolor"]
    print ps.lineProp["markerfacecolor"]

