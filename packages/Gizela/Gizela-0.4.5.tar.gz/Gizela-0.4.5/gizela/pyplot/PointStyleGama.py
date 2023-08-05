# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.pyplot.PointStyle import PointStyle

class PointStyleGama(PointStyle):
    """
    point style for gama point: fixed, adjusted and constrained
    """

    fix = PointStyle()
    con = PointStyle()
    adj = PointStyle()

    fix.lineProp["marker"] = "^"
    fix.lineProp["markerfacecolor"] = "red"
    
    con.lineProp["marker"] = "s"
    con.lineProp["markerfacecolor"] = "blue"

    adj.lineProp["marker"] = "o"
    adj.lineProp["markerfacecolor"] = "green"
    
    def __new__(cls):

        instance = super(PointStyleGama, cls).__new__(cls)

        # copy class attributes into instance
        import copy
        instance.fix = copy.deepcopy(cls.fix)
        instance.con = copy.deepcopy(cls.con)
        instance.adj = copy.deepcopy(cls.adj)

        return instance

    def __init__(self):

        super(PointStyleGama, self).__init__()
    

    def set_point_color(self, faceColor, edgeColor="black"):
        super(PointStyleGama, self).set_point_color(faceColor, edgeColor)
        self.fix.set_point_color(faceColor, edgeColor)
        self.con.set_point_color(faceColor, edgeColor)
        self.adj.set_point_color(faceColor, edgeColor)

    
    def set_point_size(self, size):
        super(PointStyleGama, self).set_point_size(size)
        self.fix.set_point_size(size)
        self.con.set_point_size(size)
        self.adj.set_point_size(size)

    
    def set_label_size(self, size):
        super(PointStyleGama, self).set_label_size(size)
        self.fix.set_label_size(size)
        self.con.set_label_size(size)
        self.adj.set_label_size(size)


if __name__ == "__main__":
    
    ps = PointStyleGama()
    print ps.fix.textProp["fontsize"]

    ps.set_label_size(2)
    print ps.fix.textProp["fontsize"]

    ps2 = PointStyleGama()
    ps2.set_point_color("xxx")
    print ps.adj.lineProp["markerfacecolor"]
    print ps2.adj.lineProp["markerfacecolor"]
