# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.util.CoordSystemLocal2D import CoordSystemLocal2D
from gizela.util.CoordSystemLocal3D import CoordSystemLocal3D
from gizela.data.point_text_table import gama_coor_stdev_table
from gizela.data.GamaLocalData import GamaLocalData
from gizela.data.GamaLocalDataObs import GamaLocalDataObs
from gizela.data.StandardDeviation import StandardDeviation
from gizela.data.PointList         import PointList
from gizela.data.PointListCovMat import PointListCovMat
from gizela.data.ObsClusterList    import ObsClusterList
from gizela.data.point_text_table import gama_coor_table
from gizela.util.Error import Error
from gizela.data.DUPLICATE_ID import DUPLICATE_ID
from gizela.data.CovMatApri import CovMatApri
from gizela.util.AxesOrientation import AxesOrientation
from gizela.data.GamaCoordStatus import GamaCoordStatus
from gizela.util.Unit import Unit

import ConfigParser


class NetworkError(Error): pass


class Network(object):
    """
    base class for local geodetic network
    """

    def __init__(self, coordSystemLocal, data, useApriori=True):
        """
        coordSystemLocal: coordinate system instance
              CoordSystemLocal2D
              CoordSystemLocal3D
        data: instance with network observations
              GamaLocalDataObs
        useApriori: use apriori standard deviation?
        """

        # coordinate system
        if isinstance(coordSystemLocal, CoordSystemLocal2D) or \
           isinstance(coordSystemLocal, CoordSystemLocal3D):

            if not coordSystemLocal.is_consistent():
                raise NetworkError, "Coordinate system is not consistent"

            self.coordSystemLocal = coordSystemLocal

        else:
            raise NetworkError, "CoordSystemLocal* instance expected"

        self.dateTimeList = []
            # list of date and time of observations
            # joined epoch has more than one value

        self.configParser = ConfigParser.SafeConfigParser()
        self.configParser.optionxform = str 
            # to make options case sensitive

        self._useApriori = useApriori

        self.stdev = StandardDeviation(apriori=1.0, useApriori=self._useApriori)
            # standard deviation

        self.obsStdev = {"direction": None,
                         "distance": None,
                         "zenith-angle": None}

        # point list of FIXED POINTS
        #self.pointListFix = PointList(textTable=gama_coor_table())

        # list of point TO BE ADJUSTED and FIXED
        # point list of adjusted/constrained points without covariance matrix
        # use for points to be adjusted in input XML document
        self.pointListAdj = PointList(textTable=gama_coor_table())

        # list of ADJUSTED POINTS
        # point list of adjusted/constrained points with covariance matrix
        # use for adjusted points in output XML document
        self.pointListAdjCovMat =\
                PointListCovMat(covmat=CovMatApri(useApriori=self._useApriori),
                                textTable=gama_coor_stdev_table())

        # list of OBSERVATIONS
        self.obsClusterList = ObsClusterList()

        if isinstance(data, GamaLocalData):
            #self.pointListFix = data.pointListFix
            self.pointListAdj = data.pointListAdj + data.pointListFix
            self.pointListAdjCovMat = data.pointListAdjCovMat
            self.obsClusterList = data.obsClusterList

            # try to parse description string
            import StringIO
            try:
                # handle character % in description
                data.description = data.description.replace("%","%%")
                #import sys
                #print >>sys.stderr, "Description:", data.description
                self.configParser.readfp(StringIO.StringIO(data.description))
            except Exception, e:
                import sys
                print >>sys.stderr, "Warning: Description not parsed"
                print >>sys.stderr, "Description: %s" % data.description
                print >>sys.stderr, "Error: %s" % e

                # create section epoch
                self.configParser.add_section("epoch")
                # set option description
                self.configParser.set("epoch", "description", data.description)

            else:
                self.set_date_time_list()
                    # sets date and time according to configParser

            # set stdev
            self.stdev.apriori = data.stdev["apriori"]
            self.stdev.aposteriori = data.stdev["aposteriori"],
            self.stdev.set_use(data.stdev["used"])
            self.stdev.set_conf_prob(data.stdev["probability"])
            self.stdev.df = data.stdev["df"]

            # set observation stdev
            self.obsStdev["direction"] = data.param["direction-stdev"]
            self.obsStdev["distance"] = data.param["distance-stdev"]
            self.obsStdev["zenith-angle"] = data.param["zenith-angle-stdev"]

            # check axes and bearing orientation
            if self.coordSystemLocal.axesOri != data.param["axes-xy"]:
                import sys
                print >>sys.stderr, "Axes orientation is different (%s, %s)"\
                    % (self.coordSystemLocal.axesOri, data.param["axes-xy"])

            if self.coordSystemLocal.bearingOri != data.param["angles"]:
                import sys
                print >>sys.stderr, "Bearing orientation is different (%s, %s)"\
                    % (self.coordSystemLocal.bearingOri, data.param["angles"])

            ax = AxesOrientation(axesOri=data.param["axes-xy"],
                                 bearingOri=data.param["angles"])
            if not ax.is_consistent():
                raise NetworkError, \
                        "Coordinate system of data is not consistent"



    def set_date_time_list(self):
        """
        sets date and time dateTimeList according to configParser
        """

        if self.configParser.has_option("epoch", "date"):
            dates = self.configParser.get("epoch", "date")

            #import sys
            #print >>sys.stderr, dates

            self.set_date_time_string(dates)

        else:
            import sys
            print >>sys.stderr, "Network: No option 'date' in section 'epoch'"


    def set_date_time_string(self, dateTimeStr):
        """
        sets dateTimeList according to dateTimeStr

        dateTimeStr: string: string with date and time in format
                             yyyy.mm.dd.hh.mm.ss.microseconds
        """

        import datetime

        for date in dateTimeStr.split(" "):
            date = date.split(".")
            try:
                # one date in the form yyyy.mm.dd.hh.mm.ss.microseconds
                date = [int(i) for i in date]
            except: 
                raise NetworkError, "Wrong date: %s" % date

            if len(date) == 1:
                self.dateTimeList.append(datetime.datetime(year=date[0]))
            elif len(date) == 2:
                self.dateTimeList.append(datetime.datetime(year=date[0],
                                                   month=date[1]))
            elif len(date) == 3:
                self.dateTimeList.append(datetime.datetime(year=date[0],
                                                   month=date[1],
                                                   day=date[2]))
            elif len(date) == 4:
                self.dateTimeList.append(datetime.datetime(year=date[0],
                                                   month=date[1],
                                                   day=date[2],
                                                   hour=date[3]))
            elif len(date) == 5:
                self.dateTimeList.append(datetime.datetime(year=date[0],
                                                   month=date[1],
                                                   day=date[2],
                                                   hour=date[3],
                                                   minute=date[4]))
            elif len(date) == 6:
                self.dateTimeList.append(datetime.datetime(year=date[0],
                                                   month=date[1],
                                                   day=date[2],
                                                   hour=date[3],
                                                   minute=date[4],
                                                   second=date[5]))
            elif len(date) == 7:
                self.dateTimeList.append(datetime.datetime(year=date[0],
                                                   month=date[1],
                                                   day=date[2],
                                                   hour=date[3],
                                                   minute=date[4],
                                                   second=date[5],
                                                   microsecond=date[6]))
            else:
                raise NetworkError, "Wrong date: %s" % date


    def set_description_date_time(self):
        """
        sets description option date in section epoch
        according to dateTimeList
        """
        if not self.configParser.has_section("epoch"):
            self.configParser.add_section("epoch")

        self.configParser.set("epoch", "date",
                              " ".join(["%i.%i.%i.%i.%i.%i.%i" % \
                                        (d.year,
                                         d.month,
                                         d.day,
                                         d.hour,
                                         d.minute,
                                         d.second,
                                 d.microsecond) for d in self.dateTimeList]))

    #def set_date_time_string(self, dateTimeStr):

    #    dates = dateTimeStr.split(",")
    #    if len(dates) != len(self.dateTimeList):
    #        raise NetworkError, "Wrong number of epochs id dateTimeString"
    #    dateList=[]
    #    for date in dates:
    #        fields = date.split(".")
    #        try:
    #            num = [float(f) for f in fields]
    #        except:
    #            raise NetworkError, "Wrong field in dateTime string"
    #        while len(num) < 7:
    #            num.append(0.0)
    #        dateList.append(".".join(["%i" % n for n in num]))

    #    #import sys
    #    #print >>sys.stderr, "dateList", dateList

    #    if not self.configParser.has_section("epoch"):
    #        self.configParser.add_section("epoch")

    #    self.configParser.set("epoch", "date", " ".join(dateList))


    def set_stdev_use(self, use):
        """
        sets which standard deviation to use in adjustment
        apriori/aposteriori
        """

        if use == "apriori":
            apriori = True
        elif use == "aposteriori":
            apriori = False
        else:
            raise NetworkError, "Unknown stdev use: %s" % use

        self.set_use_apriori(apriori)


    def set_use_apriori(self, use):
        self._useApriori = use
        self.stdev.set_use_apriori(use)
        self.pointListAdjCovMat.set_use_apriori(use)


    def set_conf_prob(self, confidence):
        self.stdev.set_conf_prob(confidence)

                
    def extend(self, other, 
               #duplicateIdFix=DUPLICATE_ID.compare,
               duplicateIdAdj=DUPLICATE_ID.overwrite,
               duplicateIdAdjCovMat=DUPLICATE_ID.hold):
        """
        adds clusters with observations and points from other to self
        """

        if not isinstance(other, Network):
            raise NetworkError, "Network instance expected"

        # extend points
        #self.pointListFix.duplicateId  = duplicateIdFix
        self.pointListAdj.duplicateId  = duplicateIdAdj
        self.pointListAdjCovMat.duplicateId  = duplicateIdAdjCovMat

        #self.pointListFix.extend(other.pointListFix)
        self.pointListAdj.extend(other.pointListAdj)
        self.pointListAdjCovMat.extend(other.pointListAdjCovMat)
        # warning do not extend with covariance matrix

        # extend observations
        self.obsClusterList.extend(other.obsClusterList)

        # extend dateTimeList
        self.dateTimeList.extend(other.dateTimeList)

        # extend description ConfigParser
        for section in other.configParser.sections():
            if not self.configParser.has_section(section):
                self.configParser.add_section(section)
            #for option, value in other.configParser.items(section):
            for option in other.configParser.options(section):
                value = other.configParser.get(section, option)
                if self.configParser.has_option(section, option):
                    self.configParser.set(section, option, 
                                     self.configParser.get(section, option)\
                                     + " " + value)
                else:
                    self.configParser.set(section, option, value)


    def replace_point_with_adjusted(self, adj):
        """
        replaces points with adjusted one

        pointListFix -> pointListFix
        pointListAdjCovMat -> pointListAdj
        """

        if not isinstance(adj, Network):
            raise NetworkError, "Network instance expected"

        # replace fixed points
        #self.pointListFix = adj.pointListFix

        # create new poinListAdj and add adjusted points
        self.pointListAdj = PointList(textTable=self.pointListAdj.textTable,
                                      duplicateId=self.pointListAdj.duplicateId,
                                      sort=self.pointListAdj.sortOutput)
        for point in adj.pointListAdjCovMat:
            self.pointListAdj.add_point(point)
       

    def set_axes_ori(self, axesXY):
        "sets axes orientation"
        self.coordSystemLocal.axesOri = axesXY

    
    def get_axes_ori(self):
        return self.coordSystemLocal.axesOri
    

    def plot_point_fix(self, figure):
        #self.pointListFix.plot_(figure)
        pass

   
    def plot_point_adj(self, figure):
        self.pointListAdj.plot_(figure)
    
    
    def plot_point_adj_cov_mat(self, figure):
        
        self.pointListAdjCovMat.plot_(figure)
        self.pointListAdjCovMat.plot_error_ellipse(figure)

    
    def plot_point(self, figure):
        "plot all points"
        figure.update_(self) # sets figure stdev and axesOri
        figure.set_aspect_equal()
        #self.plot_point_fix(figure)
        self.plot_point_adj(figure)
        self.plot_point_adj_cov_mat(figure)
        #figure.update(self)


    def proj_point_xy(self):
        self.pointListAdj.proj_xy(self.coordSystemLocal)
        #self.pointListFix.proj_xy(self.coordSystemLocal)



    def make_gama_xml(self, corrected=False):
        """
        Writes Gama-local XML file with observation
        @param corrected: return corrected measurements or not
        @type corrected: bool
        """
        
        # header
        str = ['<?xml version="1.0" ?>',
               '<!DOCTYPE gama-xml',
               'SYSTEM "http://www.gnu.org/software/gama/gama-local.dtd">']
        str.append("<gama-local>")
        str.append('<network axes-xy="%s"' % self.coordSystemLocal.axesOri +\
                   ' angles="%s">' % self.coordSystemLocal.bearingOri)
                   #' epoch="%(epoch).4f">' % self.param)

        # description
        #
        # set description epoch date according to dateTimeList
        self.set_description_date_time()
        
        # write ConfigParser instance
        import StringIO
        f = StringIO.StringIO()
        self.configParser.write(f)
        description = "".join(f.buflist)
        str.append("<description>\n%s</description>" %  description)

        # parameters
        str.append('<parameters sigma-apr = "%.3f"' % self.stdev.apriori)
        str.append('            conf-pr   = "%.3f"' % self.stdev.confProb)
        #str.append('            tol-abs   = "%.1f"' % (self.param["tol-abs"] * Unit.tolabs))
        str.append('            sigma-act = "%s"/>' % self.stdev.get_use())
        #str.append('            update-constrained-coordinates = "%(update-constrained-coordinates)s" />' % self.param)

        # points-observations
        pobs = "<points-observations"
        if self.obsStdev["direction"] is not None:
            pobs += ' direction-stdev="%.1f"' %\
                    (self.obsStdev["direction"] * Unit.angleStdev)
        if self.obsStdev["distance"] is not None:
            pobs += ' distance-stdev="%s"' %\
                    " ".join(["%.1f" % (i * Unit.distStdev) \
                              for i in self.obsStdev["distance"]])
        if self.obsStdev["zenith-angle"] is not None:
            pobs += ' zenith-angle-stdev="%.1f"' %\
                    (self.obsStdev["zenith-angle"] * Unit.angleStdev)
        pobs += ">"
        str.append(pobs)
            
        # points
        #str.append(self.pointListFix.make_gama_xml())
        str.append(self.pointListAdj.make_gama_xml())

        # clusters of observations
        str.append(self.obsClusterList.make_gama_xml(corrected))

        # end tags
        str.append("</points-observations>")
        str.append("</network>")
        str.append("</gama-local>")

        return "\n".join(str)
    
    
    def set_file_name(self, fname):
        """
        sets the file name of data
        """
        if not self.configParser.has_section("epoch"):
            self.configParser.add_section("epoch")

        self.configParser.set("epoch", "obsFileName", fname)

    
    def compute_corr(self):
        """
        Computes corrections for all observation
        """
        from gizela.corr.ObsCorrSphere import ObsCorrSphere

        corr = ObsCorrSphere(self.coordSystemLocal.ellipsoid,
                             self.coordSystemLocal.centralPointGeo,
                             self.coordSystemLocal.centralPointLoc,
                             self.coordSystemLocal.axesOri,
                             self.coordSystemLocal.bearingOri,
                             #self.pointListFix + self.pointListAdj,
                             self.pointListAdj,
                             self.obsClusterList)

        self.obsClusterList.compute_corr(corr)
        
    def compute_obs(self):
        """
        Computes observation values for all observations
        """
        corr = ObsCorrSphere(self.ellipsoid,
                             self.centralPointGeo,
                             self.centralPointLoc,
                             #self.pointListFix + self.pointListAdj
                             self.pointListAdj)
        self.obsClusterList.compute_obs(corr)        


    #def add_adj(self, other):
    #    """
    #    adds GamaLocalDataAdj instance to self
    #    attribute pointListAdjCovMat moves to pointListAdj
    #    """

    #    super(GamaLocalDataObs, self).add_(other)

    #    from gizela.data.DUPLICATE_ID import DUPLICATE_ID

    #    self.pointListAdj.duplicateId  = DUPLICATE_ID.overwrite
    #    self.pointListAdj.extend(self.pointListAdjCovMat)

    #    from gizela.data.PointListCovMat import PointListCovMat
    #    from gizela.data.CovMatApri import CovMatApri
    #    from gizela.data.point_text_table import gama_coor_stdev_table

    #    self.pointListAdjCovMat = PointListCovMat(covmat=CovMatApri(),
    #                                        textTable=gama_coor_stdev_table())


    def tran_vec_3d(self):
        """
        Transforms vectors from geocentric system
        to local system sets by centralPointGeo.
        Local geodetic system has north-east orientation.
        """

        #lat, lon = self.centralPointGeo.get_latlon()
        #tr.rotation_xyz(0, lat - pi/2, lon - pi)
        #tr.trmat[:,1] *= -1.0 # changing y-axis orientation
        
        self.obsClusterList.tran_vec_3d(self.coordSystemLocal)


    def tran_vec_2d(self):
        """
        transforms vectors from geocentric system
        to local system xy sets by proj4String in self.coordSystemLocal
        Covariance matrix transforms to neu directions
        """

        self.obsClusterList.tran_vec_2d(self.coordSystemLocal, 
                                        self.pointListAdj) #+ self.pointListFix)

    def scale_vec_cov_mat(self, factor):
        """
        scale covatiance matrix of vectors with factor**2
        """

        self.obsClusterList.scale_vec_cov_mat(factor)


    def sdist_to_dist(self):
        self.obsClusterList.sdist_to_dist()

    def dist_scale(self):
        self.obsClusterList.dist_scale(self.coordSystemLocal)

    def delete_all_points(self):
        """ delete all points"""

        #self.pointListFix.__init__(textTable=gama_coor_table())
        self.pointListAdj.__init__(textTable=gama_coor_table())
        self.pointListAdjCovMat.__init__(covmat=CovMatApri(),
                                         textTable=gama_coor_stdev_table())

    def add_point(self, point):
        """
        adds point to pointListAdj
        """
        self.pointListAdj.add_point(point)


    def iter_point_id(self):
        """
        generator of point ids
        """

        #for id in self.pointListFix.iter_id():
        #    yield id
        for id in self.pointListAdj.iter_id():
            yield id


    def delete_observation_class(self, obsClass):
        """
        deletes all observations of class obsClass from obsClusterList
        """
        self.obsClusterList.delete_observation_class(obsClass)


    def average_direction(self):
        """
        computer an average of repeated direction
        """
        self.obsClusterList.average_direction()


    def average_distance(self, counter=False):
        """
        computer an average of repeated distance
        counter: make average from counter distances?
        """
        self.obsClusterList.average_distance(counter=counter)

    def tran_point(self, tran):
        """
        transforms point with given 2d transformation
        tran: instance Tran2D or Tran3D
        """

        self.pointListAdj.tran_point(tran)
        self.pointListAdjCovMat.tran_point(tran)


if __name__ == "__main__":
    pass

