# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$


class PlotStyle(object):
    "base class for plotting styles"
    
    lineProp={}
    textProp={}
    patchProp={}
    miscProp={}

    def __new__(cls):

        instance = super(PlotStyle, cls).__new__(cls)

        # copy class attributes into instance
        import copy
        instance.lineProp = copy.deepcopy(cls.lineProp)
        instance.textProp = copy.deepcopy(cls.textProp)
        instance.patchProp = copy.deepcopy(cls.patchProp)
        instance.miscProp = copy.deepcopy(cls.miscProp)

        return instance

    def __init__(self):
        pass


if __name__ == "__main__":
    
    ps = PlotStyle()
    ps.lineProp["alpha"] = 1

    print PlotStyle.lineProp
    print ps.lineProp


