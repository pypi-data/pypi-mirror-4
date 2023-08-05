# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$


from gizela.util.Error import Error
from gizela.stat.Epoch import Epoch
from gizela.stat.EpochPointList import EpochPointList
from gizela.data.PointList import PointList
from gizela.data.PointListCovMat import PointListCovMat
from gizela.data.point_text_table import gama_coor_table
from gizela.text.TextTable import TextTable
from gizela.data.DUPLICATE_ID import DUPLICATE_ID
from gizela.stat.PointLocalGamaDisplTest import PointLocalGamaDisplTest
from gizela.util.CoordSystemLocal2D import CoordSystemLocal2D
#from gizela.data.StandardDeviation import StandardDeviation

# plot styles
#from gizela.pyplot.PointStyle import PointStyle
#from gizela.pyplot.LabelStyle import LabelStyle
#from gizela.pyplot.ErrEllStyle import ErrEllStyle
#from gizela.pyplot.VecStyle import VecStyle
#from gizela.pyplot.DateStyle import DateStyle
#from gizela.pyplot.StdevStyle import StdevStyle

import datetime


class EpochListError(Error): pass


class EpochList(object):
    """
    list of Epoch instances
    like project
    """

    def __init__(self, 
                 stdevUseApriori=True,
                 confProb=0.95,
                 reliabProb=0.95,
                 #config=None,
                 duplicateFixId=DUPLICATE_ID.compare,
                 textTable=None):
        """
        stdevUseApriori: use apriori/aposteriori standard deviation
        confProb: confidence probability
        reliabProb: reliability probability
        config: project configuration file
        duplicateFixId: what to do with duplicate fixed points in epoch
        textTable: text table instance for epochPointList
        """

        self.numEpoch = 0 # the number of epoch added
        #self.epochList = []

        self.dateTimeList = [] # list of dates of epochs, datetime instances
        self.epochPointList = EpochPointList()
            # list of coordinates, displacements and test results
            # PointLocalGamaDisplTest instances
        
        self.pointListFix = PointList(textTable=gama_coor_table(), 
                                      duplicateId=duplicateFixId)
            # list of fixed points for all epochs

        self.coordSystemLocal = CoordSystemLocal2D()
            # definition of local geodetic system
        
        self.stdevList = []
            # list of StandardDeviation instances
            # handles degrees of freedom from GamaLocalData instance

        self._stdevUseApriori = stdevUseApriori

        self._confProb = confProb

        self.reliabProb = reliabProb

        self.testType = None

        if textTable is None:
            from gizela.stat.displ_test_text_table import displ_test_text_table
            self.textTable = displ_test_text_table()
        else:
            self.textTable = textTable

        #print self.textTable

        #self.id = self.epochPointList.index # just shorter name
        #self.axesOri = None # orientation of axes
        #self.coordSystem = None # system of coordinates
        #self.ellipsoid = None # ellipsoid instance

        #self.numPoint = 0 # the number of points in x, y and z lists
        #self.id = {} # dictionary of point ids and indexes in x, y, z lists
        #self.x = [] # list of lists of x coordinates
        #self.y = [] # list of lists of y coordinates
        #self.z = [] # list of lists of z coordinates
        #self.covmat = [] # list of covariance matrices of points

        # plots
        #self.displacementScale = 10.0 # scale factor for displacements
        #self.confScale1d = 1.0 # scale factor for confidence interval 
        #self.confScale2d = 1.0 # scale factor for confidence ellipse 
        #self.cmap = 'hsv'
        #self.pointStyleList = [] # properties for points in each epoch
                                 # PointStyleGama instances
        #self.errEllStyle = ErrEllStyle # properties for error ellipses
        #self.vecStyle = VecStyle # properties for vectors of displacements
        #self.dateStyle = DateStyle # properties for date plots
        #self.stdevStyle = StdevStyle # properties for standard deviation interval
        #if config is not None:
            # parsing configuration file
            #self.parse_config_file(config)

    
    def add_epoch(self, epoch, addCoordSystem=True):
        """adds GamaLocalData instance to list of epochs"""

        if not isinstance(epoch, Epoch):
            raise EpochListError, "Epoch instance expected"
        
        # add epoch
        self.numEpoch += 1
        #self.epochList.append(epoch)

        # stdev
        epoch.pointListAdj.covmat.useApriori = self._stdevUseApriori
        epoch.stdev.set_conf_prob(self._confProb)
        epoch.stdev.set_use(self._stdevUseApriori and "apriori" or
                                  "aposteriori")
        self.stdevList.append(epoch.stdev)


        # add epoch time and date
        self.dateTimeList.append(datetime.datetime(epoch.date.year,
                                                   epoch.date.month,
                                                   epoch.date.day,
                                                   epoch.time.hour,
                                                   epoch.time.minute,
                                                   epoch.time.second,
                                                   epoch.time.microsecond,
                                                   epoch.time.tzinfo))

        # change type of point
        pl = PointListCovMat(covmat=epoch.pointListAdj.covmat,
                             textTable=self.textTable)
        for p in epoch.pointListAdj:
            pp = PointLocalGamaDisplTest(p)
            pp.epochIndex = self.numEpoch - 1
            pl.add_point(pp)

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

        for p in pl:
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
                if p0 is None:
                    # no point found
                    continue

                #print "type p", type(p)
                #print "minus", type((p - p0).covmat)
                #from gizela.data.point_text_table import gama_coor_var_table
                #print (p-p0).with_text_table(gama_coor_var_table())
                p.set_displacement(p - p0)

        # add adjusted points
        self.epochPointList.add_epoch(pl)
        #for p in self.epochPointList.get_epoch(-1):
        #    print p.id,"covmat", p.covmat.make_gama_xml()
        #    print p.id,"var", p.var

        # add fixed points
        self.pointListFix.extend(epoch.pointListFix)
        

    def get_epoch_point_list(self, index):
        return self.epochPointList.get_epoch(index)

    
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
            idFix = [id for id in self.pointListFix.iter_id()]

        # plot adjusted
        if len(idAdj) > 0:
           self.plot_adj(figure, idAdj, plotErrorZ=False, plotTest=plotTest)
        
        # plot fixed
        if len(idFix) > 0:
            self.plot_fix(figure, idFix)

    def plot_xyz(self, figure, idAdj=None, idFix=None, plotTest=False):
        """
        plots figure with points, error ellipses, displacements
        and confidence interval of z along y axis

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
            idFix = [id for id in self.pointListFix.iter_id()]

        # plot adjusted
        if len(idAdj) > 0:
           self.plot_adj(figure, idAdj, plotErrorZ=True, plotTest=plotTest)
        
        # plot fixed
        if len(idFix) > 0:
            self.plot_fix(figure, idFix)

    
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
        for p, i in zip(self.epochPointList.iter_point(id), 
                        xrange(self.numEpoch)):
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
            self.pointListFix.plot_(figure)

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
        
        # point iterator
        pointIter = self.epochPointList.iter_point(id)
        
        # find zero epoch for point
        # the first point with x!=None and y!=None
        point0 = None
        for p in pointIter:
            if p.x != None and p.y != None:
                point0 = p
                #x0, y0 = point0.x, point0.y
                break
        if point0 == None:
            return # no xy point available

        # point iterator
        pointIter = self.epochPointList.iter_point(id)
        
        # save coordinates of vector with scale
        pointScaled = [] # point list as normal list
        for p in pointIter:
            if plotTest:
                covmat = p.displ.get_point_cov_mat()
            else:
                covmat = p.get_point_cov_mat()
            ps = (p - point0)*figure.errScale + point0
            ps.covmat = covmat
            #print "epl:", type(ps)
            pointScaled.append(ps)

        # plot points and error ellipses
        for p in pointScaled:
            p.plot_(figure, plotLabel=False)
            figure.set_stdev(self) # sets StandardDeviation instance for epoch
            if plotTest:
                if p.testPassed is not None: # point is tested
                    p.plot_error_ellipse(figure)
            else:
                p.plot_error_ellipse(figure)
                
            figure.next_point_dot_style()

        # label point0
        point0.plot_label(figure)
        
        # plot vector
        figure.plot_vector_xy(pointScaled)

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
        "returns text table of displacements"
        str = []
        if index is None:
            for i, e in zip(xrange(self.epochPointList.get_num_epoch()),
                            self.epochPointList.iter_epoch()):
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
            for pl in self.pointListAdj.iter_epoch():
                pl.covmat.useApriori = True
            for s in self.stdevList:
                s.set_stdev_use_apriori()
        elif use is "aposteriori":
            self._stdevUseApriori = False
            for pl in self.pointListAdj.iter_epoch():
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


    #def parse_config_file(self, fileName):

    #    import ConfigParser
    #    configParser = ConfigParser.SafeConfigParser()
    #    configParser.optionxform = str # to make options case sensitive
 
    #    readed = configParser.read(fileName)
    #    
    #    print "Fonfiguration file(s) readed: %s" % ", ".join(readed)
    #    
    #    self.config = {}

    #    for sec in configParser.sections():
    #        self.config[sec] = {}
    #        for p,v in configParser.items(sec):
    #            print p, v
    #            try:
    #                v=float(v)
    #            except:
    #                pass
    #            self.config[sec][p]=v

    #    #print self.config
    #    
    #    from gizela.util.Converter import Converter as con

    #    # local system
    #    try:
    #        self.coordSystemLocal = CoordSystemLocal(\
    #           ellipsoidCode = self.config["localSystem"]["ellipsoid"],
    #           lat = con.deg2rad_(self.config["localSystem"]["latitude"]),
    #           lon = con.deg2rad_(self.config["localSystem"]["longitude"]),
    #                  height = self.config["localSystem"]["height"],
    #                       x = self.config["localSystem"]["x"],
    #                       y = self.config["localSystem"]["y"],
    #                       z = self.config["localSystem"]["z"],
    #                 axesOri = self.config["localSystem"]["axesOri"],
    #              bearingOri = self.config["localSystem"]["bearingOri"],
    #                    name = self.config["localSystem"]["name"],
    #             description = self.config["localSystem"]["description"]
    #        )
    #    except:
    #        import sys
    #        print >>sys.stderr, "Warning: Local system not set."

    #    # standard deviation
    #    try:
    #        if self.config["stdev"]["use"] is "apriori":
    #            self.set_stdev_use("apriori")
    #        elif self.config["stdev"]["use"] is "aposteriori":
    #            self.set_stdev_use("aposteriori")
    #    except:
    #        import sys
    #        print >>sys.stderr, "Warning: Use of standard deviation not set"


    def compute_displacement_test(self, pointId=None, testType=None):
        """
        computes test statistic for displacements of points
        pointId: ids of point to be tested
        testType: type of test see DisplacementTestType class
                  or None for testing according to point dimension
        """

        self.testType = testType
        from gizela.stat.DisplacementTest import DisplacementTest
        dtest = DisplacementTest(apriori=self._stdevUseApriori,
                                 confProb=self._confProb,
                                 reliabProb=self.reliabProb)
        dtest.compute_test(self.epochPointList, pointId, testType)

    def get_conf_prob(self):
        return self._confProb

    def set_conf_prob(sefl, confProb):
        self._confProb = confProb
        for s in self.stdevList:
            s.set_conf_prob(confProb)


if __name__ == "__main__":

    from gizela.data.GamaLocalDataAdj import GamaLocalDataAdj
    from gizela.stat.Epoch import Epoch
   
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
        print "Run make in directory gizela/trunk/example/xml-epoch or run in stat directory"
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
    
    epl = EpochList(stdevUseApriori=True)
    #epl = EpochList(stdevUseApriori=False)
    
    for f in file:
        adj = GamaLocalDataAdj()
        adj.parse_file(f)
        ep = Epoch(adj)
        epl.add_epoch(ep)
    
    print ep.pointListAdj
    #print ep.pointListFix

    from gizela.stat.DisplacementTestType import DisplacementTestType
    #epl.compute_displacement_test()
    epl.compute_displacement_test(testType=DisplacementTestType.xy)

    print epl
    print epl.get_epoch_table()
    print epl.pointListFix

    for pl in epl.epochPointList.iter_epoch():
        print pl.covmat.apriori
        print pl.covmat.aposteriori
        print pl.covmat.useApriori

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
    fig1.set_axes_ori("en")
    #fig1.save_as()

    # plot z coordinate
    from gizela.pyplot.FigureLayoutEpochList1DTest import FigureLayoutEpochList1DTest
    id = "C2"
    print "Figure 1D Test of point %s" % id
    fig2 = FigureLayoutEpochList1DTest(displScale=1.0,
                                   title="Example",
                                   subtitle="z displacements - point %s" % id)
    
    epl.compute_displacement_test(testType=DisplacementTestType.z)
    print epl.get_epoch_table()
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
    
    fig1.show_(True)

