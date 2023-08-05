# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: PointBase.py 93 2010-11-08 14:40:36Z kubin $


from gizela.util.Error     import Error
from gizela.text.TextTable import TextTable
from gizela.pyplot.PointStyle import PointStyle


class PointBaseError(Error): pass


class PointBase(object):
    '''base class for geodetic coordinates
    '''
    
    __slots__ = ["id", "textTable", "lindex"]
    
    def __init__(self, id, textTable=None):
        """id - point identification 
        textTable - describes format of output text table
        """
        self.id = id
        if textTable == None:
            self.textTable = TextTable([("id","%12s")])
        else:
            self.textTable = textTable
        self.lindex = None # index in PointList

    def with_text_table(self, textTable):
        """
        returns text table output with textTable without changing of
        self.textTable
        """
        tt = self.textTable
        self.textTable = textTable
        str = self.__str__()
        self.textTable = tt

        return str


    def set_row_data_function(self, rowDataFun): 
        """set list of functions for making row of data"""
        self.textTable.set_row_data_function(rowDataFun)

    def set_text_table_type(self, type):
        self.textTable.type = type

    def make_header(self): 
        """returns header of table"""
        return self.textTable.make_table_head()
    
    def make_table_row(self): 
        """returns row of table"""
        return self.textTable.make_table_row(self.id)
    
    def make_footer(self): 
        """returns footer of table"""
        return self.textTable.make_table_foot()

    def __str__(self): 
        return self.make_header() +\
               self.make_table_row()    +\
               self.make_footer()

    def __eq__(self,other):
        """operator equal =="""
        if isinstance(other, PointBase):
            return self.id == other.id
        else:
            return self.id == other

    def make_gama_xml(self):
        "returns xml tag for gama-local"
        return '<point id="%s"/>' % self.id

    def change_id(self, idDict):
        if self.id in idDict:
            self.id = idDict[self.id]


if __name__ == "__main__":

    p = PointBase("A")
    p2 = PointBase("B")
    print p
    p2.textTable.type = "plain"
    print p2

    print p == p
    print p == "A"
    print p == p2
    print p == "B"

    print p.make_gama_xml()
