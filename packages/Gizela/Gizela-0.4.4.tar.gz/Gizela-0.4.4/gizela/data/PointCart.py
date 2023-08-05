# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: PointCart.py 118 2011-01-06 15:29:07Z kubin $

from gizela.util.Error import Error
from gizela.text.TextTable import TextTable
from gizela.data.PointBase import PointBase 
from gizela.data.point_text_table import coor_table
from gizela.tran.Tran2D import Tran2D
from gizela.tran.Tran3D import Tran3D


class PointCartError(Error): pass


class PointCart(PointBase):
    "class for geodetic cartesian coordinates x, y, z"

    __slots__ = ["x", "y","z"]

    def __init__(self, id, x=None, y=None, z=None, textTable=None):
        """id, coordinates x, y, z
        and format of text table output
        """
        
        self.x=x; self.y=y; self.z=z

        if textTable == None:
            textTable = coor_table()        
        super(PointCart, self).__init__(id, textTable)

    def get_xy(self): return (self.x, self.y)
    def get_xyz(self): return (self.x, self.y, self.z)

    def set_xy(self, x, y): self.x = x; self.y = y
    def set_xyz(self, x, y, z): self.x = x; self.y = y; self.z = z

    def is_set_xyz(self): 
        return self.x != None and self.y != None and self.z != None
    def is_set_xy(self): 
        return self.x is not None and self.y is not None
    def is_set_z(self): 
        return self.z is not None
    
    def __add__(self, other):
        "returns self + other"
        if not isinstance(other, PointCart):
            raise PointCartError, "addition of two points supported"
        
        x, y, z = None, None, None
        if self.x != None and other.x != None: x = self.x + other.x
        if self.y != None and other.y != None: y = self.y + other.y
        if self.z != None and other.z != None: z = self.z + other.z
        
        import copy
        p = copy.deepcopy(self)
        p.x = x; p.y = y; p.z = z
        return p
    
    def __sub__(self, other):
        "returns self - other"
        if not isinstance(other, PointCart):
            raise PointCartError, "subtraction of two points supported"
        
        x, y, z = None, None, None
        if self.x != None and other.x != None: x = self.x - other.x
        if self.y != None and other.y != None: y = self.y - other.y
        if self.z != None and other.z != None: z = self.z - other.z
        
        import copy
        p = copy.deepcopy(self)
        p.x = x; p.y = y; p.z = z
        return p
    
    def __mul__(self, other):
        "returns multiplication of point coordinates with scalar"
        if type(other) != float and type(other) != int:
            raise PointCartError, "only multiplication with scalar supported"
        
        x, y, z = None, None, None
        if self.x != None: x = self.x*other
        if self.y != None: y = self.y*other
        if self.z != None: z = self.z*other
        
        import copy
        p = copy.deepcopy(self)
        p.x = x; p.y = y; p.z = z
        return p

    def __eq__(self, other):
        "are points equal?"
        if other == None:
            # Point with all Nones
            return self.id == None and self.x == None and\
                   self.y  == None and self.z == None
        
        elif isinstance(other, PointCart):
            # compare all coordinates
            return self.id == other.id and self.x == other.x and\
                   self.y  == other.y  and self.z == other.z
        
        elif type(other) is str or type(other) is unicode:
            # compare id
            return self.id == other
        
        else:
            raise PointCartError, "PointCart instance expected"

    def __ne__(self, other):
        return not self.__eq__(other)
    
    
    def make_table_row(self): 
        return self.textTable.make_table_row(self.id, self.x, self.y, self.z)

    def make_gama_xml(self):
        #if self.id is None:
        #    return None

        str = ['<point id="%s"' % self.id]

        if self.x != None: str.append('x="%.4f"' % self.x)
        if self.y != None: str.append('y="%.4f"' % self.y)
        if self.z != None: str.append('z="%.4f"' % self.z)
        
        str.append('/>')

        return " ".join(str)
    
    def plot_(self, figure, plotLabel=True):
        """
        plot point coordinates and optionally its id
        figure: Figure instance
        plotLabel: draw point label?
        """
        
        if self.x != None and self.y != None:
            figure.plot_point_dot(self)
            if plotLabel:
                figure.plot_point_label(self)
    
    
    def plot_label(self, figure):
        """
        plot only point label
        figure: Figure instance
        """
        
        if self.x != None and self.y != None:
            figure.plot_point_label(self)

    def plot_x(self, figure, x):
        "plot x coordinate to y axis"
        
        if self.x != None:
            figure.plot_point_x(self, x)

    def plot_y(self, figure, x):
        "plot x coordinate to y axis"
        
        if self.y != None:
            figure.plot_point_y(self, x)

    def plot_z(self, figure, x):
        "plot x coordinate to y axis"
        
        if self.z != None:
            figure.plot_point_z(self, x)


    def get_point_geo(self, ellipsoid):
        """
        returns PointGeodetic instance
        lattitude, longitude and height
        """
        pass

    def proj_xy(self, coordSystemLocal2D):
        """
        converts xyz geocentric coordinates
        to xy throught projection from proj4String
        """

        if not self.is_set_xyz():
            raise PointCartError, "Geocentric coordinates not set"

        coordSystemLocal2D.proj_pointCart(self)


    def update(self, other):
        """
        updates parameters of self from other
        """

        if not isinstance(other, PointCart):
            raise PointCartError, "PointCart instance expected"

        self.id = other.id
        self.x  = other.x
        self.y  = other.y 
        self.z  = other.z
        self.textTable = other.textTable


    def tran_(self, tran):
        """
        transforms point with given transformation
        """

        if isinstance(tran, Tran2D):
            for point in self:
                if point.is_set_xy():
                    point.x, point.y = tran.transform_xy(point.x, point.y)
                else:
                    import sys
                    print >>sys.stderr, "Point id=%s not transformed" % point.id

        elif isinstance(tran, Tran3D):
            for point in self:
                if point.is_set_xyz():
                    point.x, point.y, point.z = \
                            tran.transform_xy(point.x, point.y, point.z)
                else:
                    import sys
                    print >>sys.stderr, "Point id=%s not transformed" % point.id

        else:
            raise PointListError, "Tran2D or Tran3D instance expected"


if __name__=="__main__":

    c1 = PointCart(id="A", x=1, y=2)
    c2 = PointCart(id="A2", x=2, y=4, z=4)
    c2.z = 3
    print c1.textTable.type
    c2.textTable.type = "plain"

    print c1
    print 
    print c2
    print c2.make_gama_xml()

    print c1 * 2
    print c1 * 2.0
    print (c1 * 2) + c1
    print c1 - c1

    print "# comparison"
    print c1 == c2
    print c1 != c2
    print c1 == "A"
    print c1 != "A"
    print "A" == c1

    # graph
    from gizela.pyplot.FigureLayoutBase import FigureLayoutBase
    fig = FigureLayoutBase()
    c1.plot_(fig)
    c2.plot_(fig)
    c2.plot_x(fig, 5)
    c2.plot_y(fig, 5)
    c2.plot_z(fig, 5)
    fig.set_free_space()
    fig.set_aspect_equal()
    fig.show_()
