# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

'''
class for list of point lists with dictionary for searching by point id

EpochPointList.list = [ PointList instance:
                                list = [<Point id="A", x, y, z>,
                                        <Point id="B", x, y, z>,<-o
                                        <Point id="C", x, y, z>,  |
                                        ...                       |
                                       ]                          |
                         PointList instance:                      |
                                list = [<Point id="B", x, y, z>,<-|--o
                                        <Point id="C", x, y, z>,  |  |
                                        ...                       |  |
                                       ]                          |  |
                             ...               o------------------o  |
                      ]                        |  o------------------o
                                               |  |
                                               v  v
EpochPointList.index = { "A": [0, None], "B": [1, 0], "C": [2, 1], ...}
'''


from gizela.util.Error     import Error
from gizela.data.PointList import PointList
#from gizela.data.point_text_table import coor_table
#from gizela.pyplot.PointProp import PointProp

class EpochPointListError(Error): pass


class EpochPointList(object):
    """
    List of PointList instances with 
    index - dictionary of ids for searching
    """

    def __init__(self, sortOutput=False):

        self.index = {}        # dictionary id: list index
        self.list  = []        # list of pointList instances

        self.sortOutput = sortOutput # sort points by id in text output?


    def add_epoch(self, epoch):
        '''adds PointList instance into list of epoch'''
        if not isinstance(epoch, PointList):
            raise PointListError("Requires PointList instance")
        
        # add pointList to list
        self.list.append(epoch)

        # add None to all point in index
        for id in self.index:
            self.index[id].append(None)

        # add indexes to points
        for id in epoch.index:
            if id in self.index:
                self.index[id][-1] = epoch.index[id]
            else:
                self.index[id] = [None for i in xrange(len(self.list))]
                self.index[id][-1] = epoch.index[id]

    
    def add_multiple_epoch(self, mepoch, reString, epochIndex, pointIndex):
        """
        add pointList (mepoch)  with more than one epoch and create index
        for all epoch inclusded by point id and regular expression

        use: for separating joined adjustment of multiple epochs

        mepoch: PointList object with multiple epochs
        reString: regular expression with two groups - point id, 
                                                     - epoch index from 0
        epochIndex: index of epoch number (0 or 1) in regular expression groups
        pointIndex: index of point id (0 or 1) in regular expression groups
        """
        import re

        try:
            patt = re.compile(reString)
        except:
            raise EpochPointListError, "Error compiling regular expression"

        for point in epoch.pointListFix:
            grp = patt.search(point.id)  
            if grp is not None:
                if len(grp) == 2:
                    id = grp[pointIndex]
                    ei = grp[epochIndex]


    def get_epoch(self, index):
        '''returns PointList instance'''
        try:
            return self.list[index]
        except IndexError:
            raise EpochPointListError("Unknown epoch %i" % index)


    def iter_point(self, id):
        "returns point instance generator through epochs"
        #from gizela.data.PointLocalGama import PointLocalGama
        if id in self.index:
            for i in xrange(len(self.list)):
                ind = self.index[id][i]
                if ind == None:
                    yield self.list[i].list[0].__class__(None)
                else:
                    yield self.list[i].list[ind]
                    #yield self.list[i].get_point(id)

        else:
            raise EpochPointListError, "Unknown point id=\"%s\"" % id

    
    def __len__(self):
        '''number of points'''
        return len(self.index)

    def get_num_epoch(self):
        "returns the number of epochs"
        return len(self.list)

    def __iter__(self):
        """
        iterator through points
        returns generator of generators of points in epoch
        """

        #return iter(self.index)
        for id in self.index:
            yield self.iter_point(id)

    def iter_id(self):
        """
        returns key-iterator of self.index: ids of points
        """
        
        return iter(self.index)

    def iter_epoch(self):
        "iterator for epoch - return PointList instances"
        for e in self.list:
            yield e


    #def iter_x(self, id):
    #    "generator for x coordinate of point id"
    #    if id in self.index:
    #        for point in self.iter_point(id):
    #            yield point.x
    #
    #def iter_y(self, id):
    #    "generator for y coordinate of point id"
    #    if id in self.index:
    #        for point in self.get_point(id):
    #            yield point.y
    #
    #def iter_z(self, id):
    #    "generator for z coordinate of point id"
    #    if id in self.index:
    #        for point in self.get_point(id):
    #            yield point.z
    
    def make_table(self):
        """makes text table of epochs"""
        
        if not self.list:
            return "Empty EpochPointList"

        #ids
        from gizela.text.TextTable import TextTable
        textTable = TextTable([("id","%12s")] + \
                              [("ep %i" % i, "%5s")\
                               for i in xrange(len(self.list))])
        
        ids = [id for id in self.index]
        if self.sortOutput:
            ids.sort()
        return  textTable.make_table_head() +\
                "".join([textTable.make_table_row(\
                            [id] + [i==None and " " or "*" \
                                       for i in self.index[id]])\
                         for id in ids]) +\
                textTable.make_table_foot()

    def __str__(self):
        return self.make_table()

    #def make_gama_xml(self):
    #    return "\n".join([point.make_gama_xml() for point in self.list])

    #def plot_point(self, figure, pointProp=PointProp):
    #    for point in self.list: point.plot_point(figure, pointProp)



if __name__ == "__main__":
    
    from gizela.data.PointCart import PointCart
    from gizela.data.PointList import PointList
    
    c1 = PointCart(id="C",x=1,y=2,z=3)
    c2 = PointCart(id="B",x=4,y=5,z=6)

    pl1=PointList() 
    pl2=PointList() 

    pl1.add_point(c1)
    pl1.add_point(c2)
    pl2.add_point(c2)
    
    print pl1
    print pl2

    el = EpochPointList()
    el.add_epoch(pl1)
    el.add_epoch(pl2)

    print el.index
    el.sortOutput = True
    print el

    for p in el.iter_point("C"):
        print p

    print "# iterator"
    for iter in el:
        for point in iter:
            print point
