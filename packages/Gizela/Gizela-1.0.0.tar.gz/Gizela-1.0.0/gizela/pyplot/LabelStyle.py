# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.pyplot.PlotStyle import PlotStyle

class LabelStyle(PlotStyle):
    """
    properties for 
        point text label (id)
    """
           
    # label
    textProp = {#"fontproperties": xxx,
                "fontsize": "medium",
                "fontstyle": "normal",
                "fontweight": "normal",
                "verticalalignment": "top",
                "horizontalalignment": "left"
               }
    miscProp = { "textOffsetX" : 5, #points (1/72inch)
                 "textOffsetY" :-5 #points (1/72inch)
               }

    @staticmethod
    def get_text_trans(dpi_scale_trans):
        "return transformation for text labels"
        from matplotlib.transforms import ScaledTranslation
        return ScaledTranslation(LabelStyle.miscProp["textOffsetX"]/72.0, 
                                 LabelStyle.miscProp["textOffsetY"]/72.0, 
                                 dpi_scale_trans)

