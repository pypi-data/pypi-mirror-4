# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: PointLocalGama.py 108 2010-12-07 22:59:09Z tomaskubin $


from gizela.util.Error           import Error        # exceptions
#from gizela.text.TextTable       import TextTable    # text tables
from gizela.data.GamaCoordStatus import GamaCoordStatus    # status of coordinates
from gizela.data.GamaCoordStatus import gama_coord_status_string
from gizela.data.GamaCoordStatus import gama_coord_status_xml_attr
from gizela.data.PointCartCovMat import PointCartCovMat    # base class
from gizela.data.point_text_table import gama_coor_var_table


class PointLocalGamaError(Error): pass


class PointLocalGama(PointCartCovMat):
    '''Coordinates of geodetic point: x, y, z, status
    with variance-covariance matrix
    '''

    __slots__ = ["status"]

    def __init__(self, id, x=None, y=None, z=None,\
            status=GamaCoordStatus.unused,\
            covmat=None, index=None, textTable=None): 
        
        if textTable==None:
            textTable = gama_coor_var_table()

        super(PointLocalGama,self).__init__(id=id, x=x, y=y, z=z, \
                covmat=covmat, index=index, textTable=textTable)

        self.status=status                 # status of coordinates

    def get_status_string(self):
        '''returns status of point as string'''
        return gama_coord_status_string(self.status)
    
    #def get_num_of_coordinates(self):
    #    '''return a number of coordinates'''
    #    num = [1 for i in (self.x, self.y, self.z, self.ori) if i != None]
    #    return sum(num)
    
    def is_set_xy(self): return self.x != None and self.y != None
    def is_set_z(self): return self.z != None

    ## sets status of coordinates
    def set_fix_xy(self): 
        self.status &= ~GamaCoordStatus.active_xy
        self.status |= GamaCoordStatus.fix_xy
    
    def set_adj_xy(self): 
        self.status &= ~GamaCoordStatus.active_xy
        self.status |= GamaCoordStatus.adj_xy
    
    def set_con_xy(self): 
        self.status &= ~GamaCoordStatus.active_xy
        self.status |= GamaCoordStatus.con_xy
    
    def set_adj_XY(self): self.set_con_xy()
    
    def set_fix_z(self): 
        self.status &= ~GamaCoordStatus.active_z
        self.status |= GamaCoordStatus.fix_z
    
    def set_adj_z(self): 
        self.status &= ~GamaCoordStatus.active_z
        self.status |= GamaCoordStatus.adj_z
    
    def set_con_z(self): 
        self.status &= ~GamaCoordStatus.active_z
        self.status |= GamaCoordStatus.con_z
    
    def set_adj_Z(self): self.set_con_z()
    
    def set_fix_xyz(self): 
        self.status &= ~GamaCoordStatus.active_xyz
        self.status |= GamaCoordStatus.fix_xyz
    
    def set_adj_xyz(self): 
        self.status &= ~GamaCoordStatus.active_xyz
        self.status |= GamaCoordStatus.adj_xyz
    
    def set_adj_xyZ(self): 
        self.status &= ~GamaCoordStatus.active_xyz
        self.status |= GamaCoordStatus.adj_xyZ
    
    def set_adj_XYz(self): 
        self.status &= ~GamaCoordStatus.active_xyz
        self.status |= GamaCoordStatus.adj_XYz
    
    def set_adj_XYZ(self): 
        self.status &= ~GamaCoordStatus.active_xyz
        self.status |= GamaCoordStatus.adj_XYZ
    

    
    ## which status is set?
    def is_fix_xy(self):  return bool(self.status & GamaCoordStatus.fix_xy)
    def is_fix_z(self):   return bool(self.status & GamaCoordStatus.fix_z)
    def is_fix_xyz(self): return bool(self.status & GamaCoordStatus.fix_xyz)
    
    def is_adj_xy(self):  return bool(self.status & GamaCoordStatus.adj_xy)
    def is_con_xy(self):  return bool(self.status & GamaCoordStatus.con_xy)
    def is_adj_XY(self):  return bool(self.status & GamaCoordStatus.con_xy)
    def is_adj_z(self):   return bool(self.status & GamaCoordStatus.adj_z)
    def is_con_z(self):   return bool(self.status & GamaCoordStatus.con_z)
    def is_adj_Z(self):   return bool(self.status & GamaCoordStatus.con_z)
    def is_adj_xyz(self):  return bool(self.status & GamaCoordStatus.adj_xyz)
    def is_con_xyz(self):  return bool(self.status & GamaCoordStatus.con_xyz)
    def is_adj_XYZ(self):  return bool(self.status & GamaCoordStatus.con_xyz)
    
    def is_adj_xyz(self): return bool(self.status & GamaCoordStatus.adj_xyz)
    def is_adj_xyZ(self): return bool(self.status & GamaCoordStatus.adj_xyZ)
    def is_adj_XYz(self): return bool(self.status & GamaCoordStatus.adj_XYz)
    def is_adj_XYZ(self): return bool(self.status & GamaCoordStatus.adj_XYZ)
    
    #def is_active_x(self):   return bool(self.status & GamaCoordStatus.active_x)
    #def is_active_y(self):   return bool(self.status & GamaCoordStatus.active_y)
    def is_active_z(self):   return bool(self.status & GamaCoordStatus.active_z)
    def is_active_xy(self):  return bool(self.status &\
                                         GamaCoordStatus.active_xy)
    def is_active_xyz(self):  return bool(self.status &\
                                          GamaCoordStatus.active_xyz)
    def is_active(self):     return bool(self.status & GamaCoordStatus.active)
    

    # status for coordinates
    def is_x_fix(self): return self.is_fix_xy() or self.is_fix_xyz()
    def is_y_fix(self): return self.is_x_fix()
    def is_z_fix(self): return self.is_fix_z() or self.is_fix_xyz()

    def is_x_con(self): return self.is_con_xy() or self.is_con_xyz()\
                               or self.is_adj_XYz()
    def is_y_con(self): return self.is_x_con()
    def is_z_con(self): return self.is_con_z() or self.is_con_xyz()\
                               or self.is_adj_xyZ()

    def is_x_adj(self): return self.is_adj_xy() or self.is_adj_xyz()\
                               or self.is_adj_xyZ()
    def is_y_adj(self): return self.is_x_adj()
    def is_z_adj(self): return self.is_adj_z() or self.is_adj_xyz()\
                               or self.is_adj_XYz()

    def is_xy_adj(self): return self.is_adj_xy() or self.is_adj_xyz()\
                               or self.is_adj_xyZ()
    def is_xy_con(self): return self.is_con_xy() or self.is_con_xyz()\
                               or self.is_adj_XYz()
    def is_xy_fix(self): return self.is_fix_xy() or self.is_fix_xyz()

    ## addition and subtraction of coordinates and covariance matrices
    def __add__(self, other):
        
        p = super(PointLocalGama, self).__add__(other)
        p.status = self.status
        return p
    
    def __sub__(self, other):
        '''subtraction of two points with covariance matrix'''
        
        p = super(PointLocalGama, self).__sub__(other)
        p.status = self.status
        return p

    def __eq__(self, other):
        "are points equal"
        if isinstance(other, PointLocalGama):
            return super(PointLocalGama, self).__eq__(other) and \
                   self.status == other.status
        else:
            return super(PointLocalGama, self).__eq__(other)
            
    
    def make_table_row(self): 
        row = [self.id, self.x, self.y, self.z]
        ncols = self.textTable.get_num_of_col()
        row.append(self.get_status_string())
        if ncols > 5:
            row.extend(self.var)
        if ncols > 5 + 3:
            row.extend(self.cov)

                #print self.textTable
        return self.textTable.make_table_row(row)

    def make_gama_xml(self):
        #if self.id is None:
        #    return None

        str = ""

        if self.is_active_xy() or self.is_active_xyz():
            if self.x != None:
                str += 'x="%.4f"' % self.x
            if self.y != None:
                str += ' y="%.4f"' % self.y

        if self.is_active_z() or self.is_active_xyz():
            if self.z != None:
                str += ' z="%.4f"' % self.z

        return " ".join(['<point id="%s"' % self.id,\
                str,\
                gama_coord_status_xml_attr(self.status),\
                "/>"])
    
    def plot_(self, figure, plotLabel=True):
        """
        plot point coordinates and its id
        figure: Figure instance
        plotStyle: PointStyleGama instance: properies of drawing
        """
        
        if self.x != None and self.y != None:
            if self.is_xy_fix():
                figure.plot_point_fix_dot(self)
                if plotLabel:
                    figure.plot_point_fix_label(self)
            elif self.is_xy_con():
                figure.plot_point_con_dot(self)
                if plotLabel:
                    figure.plot_point_con_label(self)
            elif self.is_xy_adj():
                figure.plot_point_adj_dot(self)
                if plotLabel:
                    figure.plot_point_adj_label(self)

    def plot_x(self, figure, x):
        "plot x coordinate to y axis"
        
        if self.x != None:
            if self.is_x_fix():
                figure.plot_point_fix_x(self, x)
            elif self.is_x_con():
                figure.plot_point_con_x(self, x)
            elif self.is_x_adj():
                figure.plot_point_adj_x(self, x)

    def plot_y(self, figure, x):
        "plot y coordinate to y axis"
        
        if self.y != None:
            if self.is_y_fix():
                figure.plot_point_fix_y(self, x)
            elif self.is_y_con():
                figure.plot_point_con_y(self, x)
            elif self.is_y_adj():
                figure.plot_point_adj_y(self, x)

    def plot_z(self, figure, x):
        "plot z coordinate to y axis"
        
        if self.z != None:
            if self.is_z_fix():
                figure.plot_point_fix_z(self, x)
            elif self.is_z_con():
                figure.plot_point_con_z(self, x)
            elif self.is_z_adj():
                figure.plot_point_adj_z(self, x)
    

    def proj_xy(self, coordSystemLocal):
        "projects with proj to xy"

        super(PointLocalGama, self).proj_xy(coordSystemLocal)

        if self.status == GamaCoordStatus.fix_xyz:
            self.status = GamaCoordStatus.fix_xy

        if self.status == GamaCoordStatus.con_xyz:
            self.status = GamaCoordStatus.con_xy

        if self.status == GamaCoordStatus.adj_xyz:
            self.status = GamaCoordStatus.adj_xy


    def update(self, other):
        """
        updates parameters of self from other
        """

        from gizela.data.PointCart import PointCart

        if isinstance(other, PointCart):
            self.id = other.id
            self.x  = other.x
            self.y  = other.y 
            self.z  = other.z
            self.textTable = other.textTable
            
        if isinstance(other, PointLocalGama):
            self.status = other.status
    

if __name__ == "__main__":

    c = PointLocalGama(id="A", x=10, y=20, z=30, status=GamaCoordStatus.fix_xyz)
    c.varx =     1.0
    c.vary =     2.0
    c.varz =     3.0
    c.covxy =   -.10
    c.covxz =   -.20
    c.covyz =   -.30

    print c
    
    from gizela.data.point_text_table import gama_coor_table
    c.textTable = gama_coor_table()
    print c
    
    from gizela.data.point_text_table import gama_coor_var_table
    c.textTable = gama_coor_var_table()
    print c
    
    from gizela.data.point_text_table import gama_coor_cov_table
    c.textTable = gama_coor_cov_table()
    print c
    
    # addition and subrtaction
    c2 = PointLocalGama(id="B", x=110, y=120, z=130,
                        status=GamaCoordStatus.adj_XYz)
    c2.var = (1,2,3)
    c2.cov = (.1,.2,.3)
    
    print "adding"
    print c + c2
    print "subtracting"
    print c - c2

    # bigger covariance matrix
    c3 = PointLocalGama(id="C", x=50, y=60, z=70,
                        status=GamaCoordStatus.adj_xyZ)

    from gizela.data.CovMat import CovMat
    c3.covmat = CovMat(dim=5,band=4)
    for i in xrange(5+4+3+2+1): c3.covmat.append_value(i)
    c3.index = (2,3,4)
    c3.textTable = gama_coor_cov_table()

    print c3.covmat.data

    print c3
    rozdil = c3 - c2
    rozdil.textTable = gama_coor_cov_table()
    print rozdil

    rozdil.status = GamaCoordStatus.fix_xyz

    print rozdil.make_gama_xml()
    
    # graph
    from gizela.pyplot.FigureLayoutBase import FigureLayoutBase
    fig = FigureLayoutBase(errScale=10.0)
    c.plot_(fig)
    c.plot_error_ellipse(fig)
    c2.plot_(fig)
    c2.plot_error_ellipse(fig)
    c2.plot_error_ellipse(fig)
    c3.var = (2,2,2)
    c3.cov = (0,0,0)
    print c3.covmat.data
    c3.plot_(fig)
    c3.plot_error_ellipse(fig)
    fig.set_free_space()
    fig.show_()
