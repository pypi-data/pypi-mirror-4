# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: NetworkAdjList.py 116 2010-12-17 16:04:37Z tomaskubin $


from gizela.util.Error import Error
from gizela.data.NetworkList import NetworkList

from gizela.data.EpochPointList import EpochPointList
from gizela.data.PointList import PointList
from gizela.data.PointListCovMat import PointListCovMat
from gizela.data.point_text_table import gama_coor_table
from gizela.text.TextTable import TextTable
from gizela.data.DUPLICATE_ID import DUPLICATE_ID
from gizela.stat.PointLocalGamaDisplTest import PointLocalGamaDisplTest
from gizela.util.CoordSystemLocal3D import CoordSystemLocal3D
from gizela.data.Network import Network
from gizela.data.StandardDeviation import StandardDeviation

import datetime, copy


class NetworkAdjListError(Error): pass


class NetworkAdjList(NetworkList):
    """
    list of Epoch instances
    like project
    """

    def __init__(self, 
                 coordSystemLocal,
                 stdevUseApriori=True,
                 confProb=0.95,
                 reliabProb=0.95,
                 testId=None,
                 duplicateIdFix=DUPLICATE_ID.compare,
                 duplicateIdAdj=DUPLICATE_ID.compare,
                 textTable=None):
        """
        stdevUseApriori: use apriori/aposteriori standard deviation
        confProb: confidence probability
        reliabProb: reliability probability
        testId: Ids of point for testing (currently only for output)
        duplicateFixId: what to do with duplicate fixed points in epoch
        textTable: text table instance for epochPointList
        """

        NetworkList.__init__(self, 
                             coordSystemLocal,
                             stdevUseApriori=stdevUseApriori,
                             confProb=confProb,
                             #reliabProb=reliabProb,
                             #duplicateIdFix=duplicateIdFix,
                             duplicateIdAdj=duplicateIdAdj)
        
        self.pointListAdj = PointList(textTable=gama_coor_table(), 
                                      duplicateId=duplicateIdFix)
            # list of fixed points for all epochs

        self.epochPointList = EpochPointList(idList=testId)
            # list of coordinates, displacements and test results
            # PointLocalGamaDisplTest instances

        self.stdevList = []
            # list of StandardDeviation instances
            # handles degrees of freedom from GamaLocalData instance

        ##self.testType = None

        if textTable is None:
            from gizela.stat.displ_test_text_table import displ_test_text_table
            self._textTable = displ_test_text_table()
        else:
            self._textTable = textTable

        self._reliabProb = reliabProb

    def _get_textTable(self):
        return self._textTable

    def _set_textTable(self, textTable):
        self._textTable = textTable
        for epoch in self.list:
            epoch.pointListAdjCovMat.textTable = textTable

    textTable = property(_get_textTable, _set_textTable)

    
    def append(self, net):
        """
        adds GamaLocalData instance to list of nets
        """

        if not isinstance(net, Network):
            raise NetworkAdjListError, "Network instance expected"

        NetworkList.append(self, net)

        # standard deviation
        net.stdev.set_use_apriori(self._stdevUseApriori)
        net.stdev.set_conf_prob(self._confProb)
        net.pointListAdjCovMat.covmat.useApriori = self._stdevUseApriori
        self.stdevList.append(net.stdev)

        # change textTable of pointList
        net.pointListAdjCovMat.textTable = self._textTable

        # compute displacements of net added
        #
        # compute differences from "zero" epoch
        for pp in net.pointListAdjCovMat:
            # change type of point
            p = PointLocalGamaDisplTest(pp)
            #p.epochIndex = len(self)# - 1
            p.epochIndex = len(self) - 1

            #import sys
            #from gizela.data.point_text_table import gama_coor_stdev_table
            #print >>sys.stderr, pp.with_text_table(gama_coor_stdev_table())
            #print >>sys.stderr, p.with_text_table(gama_coor_stdev_table())
            
            # find point in "zero" epoch
            
            p0 = None
            if p.id in self.epochPointList.iter_id():
                for pp in self.epochPointList.iter_point(p.id):
                    if p.is_set_xyz() and pp.is_set_xyz():
                        p0 = pp
                        break
                    elif p.is_set_xy() and pp.is_set_xy():
                        p0 = pp
                        break
                    elif p.is_set_z() and pp.is_set_z():
                        p0 = pp
                        break
                if p0 is not None:
                    #print "type p", type(p)
                    #print "minus", type((p - p0).covmat)
                    #from gizela.data.point_text_table import gama_coor_stdev_table
                    #print (p-p0).with_text_table(gama_coor_stdev_table())
                    p.set_displacement(p - p0)

            net.pointListAdjCovMat.replace_point(p)

        # compute differences - previous epoch
        #if self.numEpoch > 1:
        #    lastEpoch = self.epochPointList.get_epoch(-1)
        #    for p in pl:
        #        if p.id in lastEpoch:
        #            # compute displacement
        #            pd = p - lastEpoch.get_point(p.id)
        #            #print pd.id, pd.covmat.data
        #            # add displacement 
        #            p.set_displacement(pd)
        #from gizela.stat.displ_test_text_table import point_displ_text_table
        #pl.textTable = point_displ_text_table()
        #print pl


        # add adjusted points with displacements
        self.epochPointList.add_(net.pointListAdjCovMat)
        #for p in self.epochPointList.get_epoch(-1):
        #    print p.id,"covmat", p.covmat.make_gama_xml()
        #    print p.id,"var", p.var

        # add fixed points
        self.pointListAdj.extend(net.pointListAdj)


    def append_joined(self, data, reString, epochIndex, pointIndex):
        """
        separate data with joined epochs and add them

        data: Network instance with adjustment
        reString: regular expression with two groups - point id, 
                                                     - epoch index from 0
        epochIndex: index of epoch number (0 or 1) in regular expression groups
        pointIndex: index of point id (0 or 1) in regular expression groups
        """

        if not isinstance(data, Network):
            raise NetworkAdjList, "Network instance expected"

        # set text table
        data.pointListAdjCovMat.textTable = self._textTable

        # separate epochs
        self.epochPointList.add_joined(data.pointListAdjCovMat,
                                       reString, 
                                       epochIndex, pointIndex)

        # add epochs
        for i in xrange(self.epochPointList.get_num_epoch()):
            self.list.append(data)
        self.dateTimeList.extend(data.dateTimeList)

        # standard deviation
        data.stdev.set_use_apriori(self._stdevUseApriori)
        data.stdev.set_conf_prob(self._confProb)
        data.pointListAdjCovMat.covmat.useApriori = self._stdevUseApriori
        for i in xrange(self.epochPointList.get_num_epoch()):
            self.stdevList.append(data.stdev)
        
        # compute displacements
        #
        # change type of points
        for id, ind in self.epochPointList.index.items():
            #print id, ind
            for i, ii in enumerate(ind):
                if ii is not None:
                    pp = PointLocalGamaDisplTest(\
                                     self.epochPointList.list[i].list[ii])
                    pp.epochIndex = i
                    self.epochPointList.list[i].list[ii] = pp
                    #print self.epochPointList.list[i].list[ii]

        # add fixed points
        self.pointListAdj.extend(data.pointListAdj)

        # compute differences from "zero" epoch
        for id, ind in self.epochPointList.index.items():
            for i, ii in enumerate(ind):
                if ii is None:
                    continue
                p = self.epochPointList.list[i].list[ii]
                p0 = None
                for j, jj in enumerate(ind[:i]):
                    if jj is None:
                        continue
                    pp = self.epochPointList.list[j].list[jj]
                    if p.is_set_xyz() and pp.is_set_xyz():
                        p0 = pp
                        break
                    elif p.is_set_xy() and pp.is_set_xy():
                        p0 = pp
                        break
                    elif p.is_set_z() and pp.is_set_z():
                        p0 = pp
                        break
                if p0 is None:
                    # point in "zero" epoch not found
                    continue

                p.set_displacement(p - p0)
           

    def get_epoch_point_list(self, index):
        return self.epochPointList.get_epoch(index)


    def __str__(self):
        tt = TextTable([("epoch", "%5i"), ("date","%10s"), ("time","%8s")])
        str = [tt.make_table_head()]
        str.extend([tt.make_table_row(i, dt.date(), dt.time())\
                    for dt,i in zip(self.dateTimeList,
                                    xrange(len(self.dateTimeList)))])
        str.append(tt.make_table_foot())
        str.append("\n")
        str.append(self.epochPointList.__str__())

        return "".join(str)


    def get_epoch_table(self, index=None):
        """
        returns text table of displacements

        index: integer: index of epoch, None = all epoch
        """
        str = []
        if index is None:
            for i, e in enumerate(self.epochPointList.iter_epoch()):
                str.append("Epoch %i:" % i)
                str.append(e.__str__())
        else:
                str.append("Epoch %i:" % index)
                str.append(self.epochPointList.get_epoch(index).__str__())

        return "\n".join(str)

    def set_stdev_use(self, use):
        """
        set which standart deviation to use
        """

        if use is "apriori":
            self._stdevUseApriori = True
            for pl in self.epochPointList.iter_epoch():
                pl.covmat.useApriori = True
            for s in self.stdevList:
                s.set_stdev_use_apriori()
        elif use is "aposteriori":
            self._stdevUseApriori = False
            for pl in self.epochPointList.iter_epoch():
                pl.covmat.useApriori = False
            for s in self.stdevList:
                s.set_stdev_use_aposteriori()
        else:
            raise EpochListError, "Unknown value of parameter use: %s" % use

    def set_stdev_use_apriori(self):
        self.set_stdev_use("apriori")
    
    def set_stdev_use_aposteriori(self):
        self.set_stdev_use("aposteriori")

    def get_stdev_use(self): 
        return self._stdevUseApriori and "apriori" or "aposteriori"

    
    def plot_xy(self, figure, idAdj=None, idFix=None, plotTest=False):
        """
        plots figure with points and error ellipses and displacements

        figure: FigureLayoutBase instance or descendant
        idAdj: list of ids of adjusted points to be drawn
               for no adjusted points set idAdj = []
        idFix: plot fixed points
               for no fixed points set idFix = []
        """

        # id of points
        if idAdj is None:
            idAdj = [id for id in self.epochPointList.iter_id()]
        
        if idFix is None:
            idFix = [id for id in self.pointListAdj.iter_id()]

        # plot adjusted
        if len(idAdj) > 0:
           self.plot_adj(figure, idAdj, plotErrorZ=False, plotTest=plotTest)
        
        # plot fixed
        if len(idFix) > 0:
            self.plot_fix(figure, idFix)

    def plot_xyz(self, figure, idAdj=None, plotTest=False):
        """
        plots figure with points, error ellipses, displacements
        and confidence interval of z along y axis

        figure: FigureLayoutBase instance or descendant
        idAdj: list of ids of adjusted points to be drawn
               for no adjusted points set idAdj = []
        #idFix: plot fixed points
        #       for no fixed points set idFix = []

        """

        # id of points
        if idAdj is None:
            idAdj = [id for id in self.epochPointList.iter_id()]
        
        #if idFix is None:
        #    idFix = [id for id in self.pointListFix.iter_id()]

        # plot adjusted
        if len(idAdj) > 0:
           self.plot_adj(figure, idAdj, plotErrorZ=True, plotTest=plotTest)
        
        # plot fixed
        #if len(idFix) > 0:
        #    self.plot_fix(figure, idFix)

    
    def plot_z(self, figure, id, plotTest=False):
        """plot x coordinates of point id for all epochs with stdev

        self: EpochList isntance
        id: id or ids of point
        """

        if type(id) is not tuple and type(id) is not list:
            id = (id,)

        # set figure
        figure.set_color_style(self)
        figure.gca().xaxis_date()


        # plot points
        for idi in id:
            self._plot_epoch_list_displacement_z(figure, idi, plotTest)
            figure.reset_epoch_counter()
        
        # set free space around draw
        figure.set_free_space()

        #update
        figure.update_(self)
        

    def _plot_epoch_list_displacement_z(self, figure, id, plotTest): 
        """
        plot 2D graph of point z coordinates,
        confidence intervals of z coordinates and displacements for all epochs

        id: point id
        plotTest: plot results of test?
        """

        # point iterator
        pointIter = self.epochPointList.iter_point(id)
        # plot points and stdev
        z = [] # z coordinates of points
        for point, date in zip(pointIter, self.dateTimeList):
            point.plot_z(figure, date)
            if plotTest:
                if point.testPassed is not None: # point is tested
                    point.plot_z_stdev(figure, date)
            else:
                point.plot_z_stdev(figure, date)
                
            figure.next_point_dot_style()
            z.append(point.z)

        point0 = None
        for i, p in enumerate(self.epochPointList.iter_point(id)): 
            if p.is_set_z():
                point0 = p
                i_epoch = i
                break

        # label point0
        if point0 is not None:
            point0.x = self.dateTimeList[i_epoch]
            point0.y = point.z
            point0.plot_label(figure)

        # plot vector
        figure.plot_vector_z(self.dateTimeList, z)

        # plot zero line
        if point0 is not None:
            z0 = [point0.z for t in self.dateTimeList]
            figure.plot_vector_z0(self.dateTimeList, z0)

    
    def plot_fix(self, figure, id):
        """
        plots 2D graph of fixed points
        """

        figure.set_aspect_equal()
        figure.update_(self) 

        for idi in id:
            self.pointListAdj.plot_(figure)

        # set free space around draw
        figure.set_free_space()
        

    def plot_adj(self, figure, id, plotErrorZ, plotTest):
        """
        plots 2D graph of adjusted points, displacements and error ellipses

        figure: FigureLayoutBase instance
        id: id or ids of point
        plotErrorZ: plot confidence interval of z coordinate?
        plotTest: plot results of test?
        """

        if type(id) is not tuple and type(id) is not list:
            id = [id]

        # update figure 
        figure.set_aspect_equal()
        figure.update_(self)

        # plot points
        for idi in id:
            self._plot_epoch_list_displacement_xy(figure, idi, plotErrorZ,
                                                plotTest)
            figure.reset_epoch_counter()
        
        # set free space around draw
        figure.set_free_space()

    def _plot_epoch_list_displacement_xy(self, figure, id, 
                                          plotErrorZ, plotTest): 
        """
        plot 2D graph of point ,
        error ellipses and displacements for all epochs
        and optionally confidence interval of z coordinate along y axis

        id: point id
        plotErrorZ: plot confidence interval of z coordinate?
        plotTest: plot results of test?
        """
        
        # find zero epoch for point
        # the first point with x!=None and y!=None
        point0 = None
        for p in self.epochPointList.iter_point(id, withNone=False):
            if p.x != None and p.y != None:
                point0 = p
                #x0, y0 = point0.x, point0.y
                break
        if point0 == None:
            return # no xy point available

        # save coordinates of vector with scale
        pointScaled = [] # point list as normal list
        for p in self.epochPointList.iter_point(id, withNone=True):
            if plotTest and isinstance(p, PointLocalGamaDisplTest): 
                    covmat = p.displ.get_point_cov_mat()
            else:
                covmat = p.get_point_cov_mat()
            ps = (p - point0)*figure.errScale + point0
            ps.covmat = covmat
            #import sys
            #print >>sys.stderr, "Point: %s" % ps.id
            #print >>sys.stderr, "epl: %s" % type(ps)
            pointScaled.append(ps)

        # plot points and error ellipses
        for p in pointScaled:
            p.plot_(figure, plotLabel=False)
            figure.set_stdev(self) # sets StandardDeviation instance for epoch
            if plotTest and isinstance(p, PointLocalGamaDisplTest): 
                if p.testPassed is not None: # point is tested
                    p.plot_error_ellipse(figure)
            else:
                p.plot_error_ellipse(figure)
                
            figure.next_point_dot_style()

        # label point0
        point0_label = copy.deepcopy(point0)
        point0_label.id = id
        point0_label.plot_label(figure)
        
        # plot vector
        figure.plot_vector_xy(pointScaled)


    def compute_displacement_test(self, pointId=None, testType=None):
        """
        computes test statistic for displacements of points
        pointId: ids of point to be tested
        testType: type of test see DisplacementTestType class
                  or None for testing according to point dimension
        """

        #self.testType = testType
        from gizela.stat.DisplacementTest import DisplacementTest
        dtest = DisplacementTest(apriori=self._stdevUseApriori,
                                 confProb=self._confProb,
                                 reliabProb=self._reliabProb)
        dtest.compute_test(self.epochPointList, pointId, testType)

    def get_conf_prob(self):
        return self._confProb

    def set_conf_prob(sefl, confProb):
        self._confProb = confProb
        for s in self.stdevList:
            s.set_conf_prob(confProb)

    def _num_epoch(self): return len(self)

    numEpoch = property(_num_epoch)


if __name__ == "__main__":

    from gizela.data.GamaLocalDataAdj import GamaLocalDataAdj
   
    try:
        file = [
                open("../../example/xml-epoch/epoch0.adj.xml"),
                open("../../example/xml-epoch/epoch1.adj.xml"),
                open("../../example/xml-epoch/epoch2.adj.xml"),
                open("../../example/xml-epoch/epoch3.adj.xml"),
                open("../../example/xml-epoch/epoch4.adj.xml"),
                open("../../example/xml-epoch/epoch5.adj.xml")
               ]
    except IOError, e:
        print e
        print "Try to run make in directory gizela/trunk/example/xml-epoch"
        import sys
        sys.exit(1)

    #date = [
    #        datetime.date(2000,1,1),
    #        datetime.date(2001,1,1),
    #        datetime.date(2002,1,1),
    #    datetime.date(2003,1,1),
    #        datetime.date(2004,1,1),
    #        datetime.date(2005,1,1)
    #       ]
    
    from gizela.util.CoordSystemLocal3D import CoordSystemLocal3D
    c3d = CoordSystemLocal3D()
    c3d.axesOri = "ne"

    epl = NetworkAdjList(coordSystemLocal=c3d, stdevUseApriori=True)
    #epl = NetworkAdjList(stdevUseApriori=False)
    
    from gizela.data.Network import Network
    for f in file:
        adj = GamaLocalDataAdj()
        adj.parse_file(f)
        #import sys
        #print >>sys.stderr, adj.pointListAdjCovMat
        net = Network(c3d, adj)
        epl.append(net)
    

    from gizela.stat.DisplacementTestType import DisplacementTestType
    #epl.compute_displacement_test()
    epl.compute_displacement_test(testType=DisplacementTestType.xy)

    print epl
    print epl.get_epoch_table()
    from gizela.data.point_text_table import gama_coor_stdev_table
    epl.textTable = gama_coor_stdev_table()
    print epl.get_epoch_table()
    print epl.pointListFix


    #for pl in epl.epochPointList.iter_epoch():
    #    print pl.covmat.apriori
    #    print pl.covmat.aposteriori
    #    print pl.covmat.useApriori

    # graph
    
    
    #fig3 = FigureLayoutEpochList(figScale=figScale,
    #                             title="Example",
    #                             subtitle="y displacements")
    
    
    # plot 2d
    from gizela.pyplot.FigureLayoutEpochList2DTest import FigureLayoutEpochList2DTest
    figScale = 1.0/1e4

    print "Figure 2D Test"
    fig1 = FigureLayoutEpochList2DTest(figScale=figScale,
                                   displScale=1.0/figScale/5, 
                                   title="Example",
                                   subtitle="displacements")
    
    epl.plot_xy(fig1, plotTest=True)
    #fig1.save_as()

    # plot z coordinate
    from gizela.pyplot.FigureLayoutEpochList1DTest import FigureLayoutEpochList1DTest
    id = "C2"
    print "Figure 1D Test of point %s" % id
    fig2 = FigureLayoutEpochList1DTest(displScale=1.0,
                                   title="Example",
                                   subtitle="z displacements - point %s" % id)
    
    epl.compute_displacement_test(testType=DisplacementTestType.z)
    #print epl.get_epoch_table()
    epl.plot_z(fig2, id, plotTest=True)
    #fig2.save_as()
    
    # plot y coordinates
    #fig = Figure()
    #epl.plot_point_y(fig, "ABC3", figScale=2)
    #fig.show_(False)

    # plot z coordinates
    #fig = Figure()
    #epl.plot_point_z(fig, "C3", figScale=2)

    # print abom
    from math import pi
    ep0 = epl.epochPointList.get_epoch(1)
    for p in ep0:
        if p.displ.is_set_xy():
            ell = p.displ.errEll
            print p.id, ell[-1]*200/pi
    
    #fig1.show_(True)

    import sys
    #sys.exit(1)

    print "\n # joined adjustment"

    try:
        file = open("../../example/xml-epoch/joined.adj.xml")
    except IOError, e:
        print e
        print "Try to run make in directory gizela/trunk/example/xml-epoch"
        import sys
        sys.exit(1)

    epl = NetworkAdjList(coordSystemLocal=c3d, stdevUseApriori=True)
    #epl = EpochList(stdevUseApriori=False)
    
    adj = GamaLocalDataAdj()
    adj.parse_file(file)
    net = Network(c3d, adj)
    epl.append_joined(net, reString="^e_(\d+)_(.+)$", epochIndex=0, pointIndex=1, )
    
    #print epl.dateTimeList

    from gizela.stat.DisplacementTestType import DisplacementTestType
    #epl.compute_displacement_test()
    epl.compute_displacement_test(testType=DisplacementTestType.xy)

    print epl
    print epl.get_epoch_table()
    print epl.pointListFix
