# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: PointList.py 118 2011-01-06 15:29:07Z kubin $

'''
class for list of points with dictionary for searching by point id

PointList.list = [<Point id="A", x, y, z>,
                  <Point id="B", x, y, z>,
                  <Point id="C", x, y, z>, <--o 
                  ...]       |_______     ____|
                                     |   |
PointList.index = { "A": 0, "B": 1, "C": 2, ...}
'''


from gizela.util.Error     import Error
from gizela.text.TextTable import TextTable
from gizela.data.PointBase import PointBase
from gizela.data.point_text_table import coor_table
from gizela.data.DUPLICATE_ID import DUPLICATE_ID

class PointListError(Error): pass

class PointList(object):
    """List of geodetic points CoordBase"""

    #__slots__ = ["index", "list", "duplicateId", "_textTable", "sortOutput"]

    def __init__(self, textTable=None, duplicateId=DUPLICATE_ID.error, sort=False):
        '''
        duplicateId ... what to do with duplicit id of point
        textTable ... format of table for text output
        sort   ... sort output by id?
        '''

        self.index     = {}        # dictionary id: list index
        self.list      = []         # list of points
        self.duplicateId  = duplicateId
        if textTable == None:
            self.textTable = coor_table()
        else:
            self.textTable  = textTable    # TextTable instance
        self.sortOutput = sort         # sort output?


    def _get_textTable(self): return self._textTable
    def _set_textTable(self,textTable):
        if isinstance(textTable, TextTable):
            self._textTable = textTable
            for point in self.list: point.textTable = textTable
        else:
            raise PointListError, "TextTable instance expected"

    textTable = property(_get_textTable, _set_textTable)

    def set_sort(self): self.sortOutput = True
    def unset_sort(self): self.sortOutput = False

    
    def add_point(self, point):
        '''adds PointBase instance into list'''
        if not isinstance(point,PointBase):
            #import sys
            #print >>sys.stderr, type(point)
            raise PointListError("Requires PointBase or its inheritance")
        
        # handle duplicateId
        id = point.id
        if id in self.index:
            
            if self.duplicateId == DUPLICATE_ID.hold: 
                "hold old point"
                pass

            elif self.duplicateId == DUPLICATE_ID.overwrite:
                "owerwrite old poitn with the new one"
                self.list[self.index[id]]=point

            elif self.duplicateId == DUPLICATE_ID.error:
                "raise exception"
                raise PointListError, "Duplicit point id '%s'" % id

            elif self.duplicateId == DUPLICATE_ID.compare:
                "compare coordinates: raise error when differs"
                p = self.list[self.index[id]]
                if p != point:
                    print p, point
                    raise PointListError, \
                    "Point \"%s\" differs with point allready in list" % id

            else:
                raise PointListError, "Unsupported DUPLICATE_ID value '%s'" % self.duplicateId

        else:
            index = len(self.list)
            self.index[id] = index
            point.lindex = index
            self.list.append(point)


        # set text table
        point.textTable = self._textTable


    def replace_point(self, point):
        """
        replace existing point with new point
        """
        if point.id not in self.index:
            raise PointListError, "Error replacing point id=", point.id

        ind = self.index[point.id]
        self.list[ind] = point
        
    
    def get_point(self, id):
        '''returns PointBase instance'''
        try:
            return self.list[self.index[id]]
        except KeyError:
            raise PointListError("Unknown point \"%s\"" % id)

    def del_point(self, id):
        """deltes point from poitList"""

        # delete: 1. remove key from self.index dictionary
        #         2. replace point in self.list list with None

        try:
            ind = self.index.pop(id)
            self.list[ind] = self.list[ind].__class__(id=None)
            #self.list.pop(ind)
            #import sys
            #print >>sys.stderr, "Point %s removed" % id
        except KeyError:
            raise PointListError, "Point id=\"%s\" does not exist" % id


    def __len__(self):
        '''number of points in dictionary'''
        len = 0
        for i in self.list:
            if i is not None: 
                len += 1
        return len

    def __iter__(self):
        """point generator"""
        for p in self.list:
            if p is not None:
                yield p

    def iter_id(self):
        """iterator throught id"""
        return iter(self.index)

    def extend(self, other):
        """
        extends with other PointList
        """

        if not isinstance(other, PointList):
            raise PointListError, "PointList instance expected"

        for point in other:
            self.add_point(point)
    
    def make_table(self):
        """makes text table of points in dictionary"""
        
        if not self.list:
            return "Empty pointList"

        #ids
        ids = [id for id in self.index]
        if self.sortOutput:
            ids.sort()
            return  self.list[self.index[ids[0]]].make_header() +\
                "".join([self.list[self.index[id]].make_table_row() for id in ids]) +\
                self.list[self.index[ids[0]]].make_footer()
        else:
            return  self.list[0].make_header() +\
                "".join([point.make_table_row() \
                         for point in self.list if point is not None]) +\
                self.list[0].make_footer()


    def __add__(self, other):
            "addition of two lists of points"
            
            if not isinstance(other, PointList):
                    raise PointListError, "PointList instance expected"
            
            import copy
            pl = copy.deepcopy(self)
            
            for point in other.list:
                    pl.add_point(point)

            return pl
                

    def __str__(self):
        return self.make_table()

    def make_gama_xml(self):
        return "\n".join([point.make_gama_xml() \
                          for point in self.list if point != None])

    def plot_(self, figure):
        for point in self.list:
            if point is not None: 
                point.plot_(figure)

    def proj_xy(self, coordSystemLocal):
        for point in self.list:
            if point.is_set_xyz(): 
                point.proj_xy(coordSystemLocal)

    #def change_id(self, idDict):
    #    for point in self.list:
    #        point.change_id(idDict)


    def update_point(self, point):
        """
        update point if point exists 
        otherwise add new point
        """
        if point.id in self.iter_id():
            p = self.get_point(point.id)
            p.update(point)
        else:
            self.add_point(point)


    def tran_point(self, tran):
        """
        transforms points with given transformation
        tran: instance Tran2D or Tran3D
        """

        for point in self:
            point.tran_(tran)




if __name__ == "__main__":
    
    from gizela.data.PointCart import PointCart
    
    c1 = PointCart(id="C",x=1,y=2,z=3)
    c2 = PointCart(id="B",x=4,y=5,z=6)

    pd=PointList() 

    print pd

    pd.add_point(c1)
    pd.add_point(c2)
    pd.add_point(PointCart(id="A",x=7,y=8,z=9))
    pd.add_point(PointCart(id="AA",x=7,y=8,z=9))
    
    print pd
    print pd.get_point("A")
    print "C" in pd
    print "c" in pd
    for point in pd: print point

    #delete
    print "delete point A"
    pd.del_point("A")
    print pd
    print pd.make_gama_xml()
    for id in pd.iter_id():
        print id
    for p in pd:
        print p

    # sort
    print "sort"
    pd.set_sort()
    print pd
    pd.unset_sort()

    # duplicateId
    pd.duplicateId = DUPLICATE_ID.overwrite
    pd.add_point(PointCart(id="C",x=10,y=20,z=30))
    pd.duplicateId = DUPLICATE_ID.hold
    pd.add_point(PointCart(id="AA",x=70,y=80,z=90))
    print pd

    # gama-xml
    pd.make_gama_xml()

    # adding
    print "adding"
    pd2=PointList() 
    pd2.add_point(PointCart(id="AB",x=0,y=5,z=30))
    pd2.add_point(PointCart(id="BB",x=10,y=10,z=30))
    pd2.extend(pd)
    print pd
    print pd2

    # graph
    try:
        from gizela.pyplot.FigureLayoutBase import FigureLayoutBase
    except:
        print "import of graphics failed"
    else:
        fig = FigureLayoutBase()
        pd.plot_(fig)
        pd2.plot_(fig)
        fig.set_free_space()
        fig.show_()

    # test of coordinates update
    from gizela.data.PointLocalGama import PointLocalGama
    from gizela.data.GamaCoordStatus import GamaCoordStatus
    point1 = PointLocalGama(id="A", x=1, y=2, status=GamaCoordStatus.fix_xy)
    point2 = PointLocalGama(id="B", x=100, y=200, status=GamaCoordStatus.adj_xy)
    point3 = PointLocalGama(id="A", x=10, y=20, status=GamaCoordStatus.adj_xy)
    pl = PointList()
    pl.add_point(point1)
    p = pl.get_point(id="A")
    p.x=10
    print pl

    pl.update_point(point2)
    print pl
    pl.update_point(point3)
    print pl

