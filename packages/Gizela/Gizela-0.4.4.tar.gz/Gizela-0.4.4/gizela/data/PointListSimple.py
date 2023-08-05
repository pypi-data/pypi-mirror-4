# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: PointListSimple.py 68 2010-08-19 09:42:00Z tomaskubin $

'''
class for list of points without finding by id and without duplicity handling
'''


from gizela.util.Error     import Error
from gizela.text.TextTable import TextTable
from gizela.data.PointBase import PointBase

class PointListSimpleError(Error): pass

class PointListSimple(object):
    """List of geodetic points CoordBase without searching by id"""

    __slots__ = ["_list", "_textTable"]
    
    def _get_textTable(self): return self._textTable
    def _set_textTable(self,textTable):
        if isinstance(textTable, TextTable):
            self._textTable = textTable
            for point in self._list: point.textTable = textTable
        else:
            raise PointListSimpleError, "TextTable instance expected"

    textTable = property(_get_textTable, _set_textTable)

    def __init__(self, textTable):
        '''duplicity ... what to do with duplicit point
        textTable ... format of table for text output
        '''

        self._list      = []         # list of points
        self.textTable  = textTable    # TextTable instance

    def add_point(self, point):
        '''adds CoordBase instance into list'''
        if isinstance(point,PointBase):
            self._list.append(point)
        else:
            raise PointListSimpleError("Requires PointBase or its inheritance")
        
        # set text table
        point.textTable = self._textTable
    
    def __len__(self):
        '''number of points in dictionary'''
        return len(self._list)

    def __iter__(self):
        """iterator"""
        #return iter(self.pointDict)
        #self.idi=0 # iterator reset
        #return self
        return iter(self._list)
        #return iter(self._index)
    
    def make_table(self):
        """makes text table of points in dictionary"""
        
        if not self._list:
            return "Empty pointList"

        return  self._list[0].make_header() +\
                "".join([point.make_table_row() for point in self._list]) +\
                self._list[0].make_footer()

    
    def __str__(self):
        return self.make_table()



if __name__ == "__main__":
    
    from gizela.data.PointCart import PointCart
    
    c1 = PointCart(id="C",x=1,y=2,z=3)
    c2 = PointCart(id="B",x=4,y=5,z=6)

    #pd=PointList(textTable=c1.get_text_table()) 
        # setting text table accoridng to PointCart instance
    pd=PointListSimple(textTable=TextTable([("ID","%2s"),("XX","%2i"),("YY","%2i"),("ZZ","%2i")])) 

    print pd

    pd.add_point(c1)
    pd.add_point(c2)
    pd.add_point(PointCart(id="A",x=7,y=8,z=9))
    
    print pd
    print "C" in pd
    print "c" in pd
    for point in pd: print point

