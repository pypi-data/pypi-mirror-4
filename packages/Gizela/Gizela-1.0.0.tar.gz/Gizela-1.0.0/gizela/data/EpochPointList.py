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

    def __init__(self, idList=None, sortOutput=False):
        """
        idList: list of ids to add in
        """

        self.index = {}        # dictionary id: list index
        self.list  = []        # list of pointList instances

        self.idList = idList

        self.sortOutput = sortOutput # sort points by id in text output?


    def add_(self, pList):
        '''adds PointList instance into list'''
        if not isinstance(pList, PointList):
            raise PointListError("Requires PointList instance")
        
        # add pointList to list
        self.list.append(pList)

        # add None to all point in index
        for id in self.index:
            self.index[id].append(None)

        # add indexes to points
        for id in pList.index:
            if id in self.index:
                self.index[id][-1] = pList.index[id]
            else:
                if self.idList is not None:
                    if id not in self.idList:
                        continue
                self.index[id] = [None for i in xrange(len(self.list))]
                self.index[id][-1] = pList.index[id]


    
    def add_joined(self, pList, reString, epochIndex, pointIndex):
        """
        add pointList (pList)  with more than one epoch and create index
        for all epoch included by point id and regular expression

        use: for separating joined adjustment of multiple epochs

        mepoch: PointList object with multiple epochs
        reString: regular expression with two groups - point id, 
                                                     - epoch index from 0
        epochIndex: index of epoch number (0 or 1) in regular expression groups
        pointIndex: index of point id (0 or 1) in regular expression groups
        """

        if self.get_num_epoch() > 0:
            raise EpochPointListError, "Method add_joined requres empty list"

        import re

        try:
            patt = re.compile(reString)
        except:
            raise EpochPointListError, "Error compiling regular expression"

        max_ei = 0 # maximal index of epoch
        #import sys
        for ide in pList.index:
            result = patt.search(ide)  
            len_grp = 0
            if result is not None:
                len_grp = len(result.groups())

            if len_grp == 2:
                # epoch detected
                #print >>sys.stderr, "Epoch detected: %s" % ide
                grp = result.groups()
                id = grp[pointIndex]
                if self.idList is not None:
                    if id not in self.idList:
                        #print >>sys.stderr, "continue id='%s'" % id
                        continue
                try:
                    ei = int(grp[epochIndex])
                except ValueError:
                    raise EpochPointListError, \
                        "Cannot determine epoch index"

                if ei > max_ei:
                    max_ei = ei

                if id not in self.index:
                    self.index[id] = []

                if len(self.index[id]) > ei:
                    if self.index[id][ei] is None:
                        self.index[id][ei] = pList.index[ide]
                        #print >>sys.stderr, "Epoch %i: %s" % (ei, ide)
                    else:
                        raise EpochPointListError, \
                            "Point '%s' allready exists" % id
                else:
                    for i in xrange(ei - len(self.index[id]) + 1):
                        self.index[id].append(None)
                    self.index[id][ei] = pList.index[ide]
                    #print self.index[id]
                    #print >>sys.stderr, "Epoch %i: %s" % (ei, ide)

            else: # result is None
                # epoch not detected
                # insert point to the zero epoch
                #print >>sys.stderr, "Epoch not detected: %s" % ide
                if ide in self.index:
                    raise EpochPointListError, "Point '%s' allready exists" % ide
                if self.idList is not None:
                    if ide not in self.idList:
                        #print >>sys.stderr, "continue id='%s'" % ide
                        continue
                self.index[ide] = [pList.index[ide]]
                #print >>sys.stderr, "Epoch zero: %s" % ide

        # all lists in self.index must have the same length
        for id in self.index:
            for i in xrange(max_ei - len(self.index[id]) + 1):
                self.index[id].append(None)

        # create list of epoch
        for i in xrange(max_ei + 1):
            self.list.append(pList)


    def get_epoch(self, index):
        '''returns PointList instance'''
        try:
            return self.list[index]
        except IndexError:
            raise EpochPointListError("Unknown epoch %i" % index)


    def iter_point(self, id, withNone=True):
        """returns point instance generator through epochs"""
        #from gizela.data.PointLocalGama import PointLocalGama
        if id in self.index:
            for i in xrange(len(self.list)):
                ind = self.index[id][i]
                if ind == None:
                    if withNone:
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

        #for e in self.list:
        #    yield e

        for i in xrange(self.get_num_epoch()):
            pl = self.list[0].__class__(textTable=self.list[0].textTable)
            #import sys
            #print >>sys.stderr, self.list[0].textTable
            for id, ind in self.index.items():
                if ind[i] is not None:
                    #import sys
                    #print >>sys.stderr, i, ind[i]
                    pl.add_point(self.list[i].list[ind[i]], withCovMat=True)
            yield pl


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
    el.add_(pl1)
    el.add_(pl2)

    print el.index
    el.sortOutput = True
    print el

    for p in el.iter_point("C"):
        print p

    print "\n# iterator"
    for iter in el:
        for point in iter:
            print point


    print "\n# joined epochs"
    plj = PointList()
    plj.add_point(PointCart(id="epoch_0_A", x=1, y=2, z=3))
    plj.add_point(PointCart(id="epoch_1_A", x=1, y=2, z=3))
    plj.add_point(PointCart(id="epoch_2_A", x=1, y=2, z=3))
    plj.add_point(PointCart(id="epoch_0_B", x=1, y=2, z=3))
    plj.add_point(PointCart(id="epoch_2_B", x=1, y=2, z=3))
    plj.add_point(PointCart(id="epoch_1_C", x=1, y=2, z=3))
    plj.add_point(PointCart(id="D", x=1, y=2, z=3))

    print plj
    print plj.index

    el = EpochPointList()
    el.add_joined(plj, reString="^epoch_(\d+)_(.+)$", epochIndex=0, pointIndex=1)

    print el.index

    print el
