# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: GamaLocalData.py 103 2010-11-29 00:06:19Z tomaskubin $


from gizela.data.PointList         import PointList
from gizela.data.PointListCovMat   import PointListCovMat
from gizela.data.ObsClusterList    import ObsClusterList
from gizela.data.PointGeodetic   import PointGeodetic
from gizela.data.PointCart       import PointCart
from gizela.util.Ellipsoid       import Ellipsoid
from gizela.data.point_text_table import gama_coor_table
from gizela.data.point_text_table import gama_coor_stdev_table
from gizela.util.CoordSystemLocal3D import CoordSystemLocal3D
from gizela.data.StandardDeviation import StandardDeviation
from gizela.data.CovMatApri import CovMatApri
from gizela.util.Error import Error
from gizela.data.DUPLICATE_ID import DUPLICATE_ID

import ConfigParser
import datetime


class GamaLocalDataError(Error):pass


class GamaLocalData(object):
    """
    local geodetic network data suitable for gama-local
    base class
    """
    
    slots = ["description",
             #"dateTimeList",
             #"coordSystemLocal",
             "stdev",
             "param",
             "gamaLocal",
             "coordinatesSummary",
             "obsSummary",
             "projEqn",
             "stdev",
             "pointListFix",
             "pointListAdj",
             "pointListAdjCovMat",
             "obsClusterList",
            ]

    def __init__(self):
        
        self.dateTimeList = []
            # list of date and time of observations
            # joined epoch has more than one value

        self.description = ""
        #self.description = ConfigParser.SafeConfigParser()
            # description as config parser
        #self.description.optionxform = str 
            # to make options case sensitive

        #self.fileName = "" # name of file with data
        #self.coordSystemLocal = CoordSystemLocal3D() 
            # implicit 3D local geodetic coordinates system

        #self.stdev = StandardDeviation(apriori=1.0, useApriori=True)
            # standard deviation

        self.stdev = {"apriori": 1.0,
                      "probability": 0.95,
                      "used": "apriori",
                      "aposteriori": None,
                      "df": None}

        self.param = {"axes-xy": "ne",
                      "angles" : "right-handed",
                      "epoch"  : 0.0,
                      "update-constrained-coordinates" : "no",
                      "tol-abs": 1.0,
                      "direction-stdev": None,
                      "distance-stdev": None,
                      "zenith-angle-stdev": None
                     }

        self.gamaLocal = {}
        self.coordinatesSummary = {}
        self.obsSummary = {}
        self.projEqn = {}

        # point list of FIXED POINTS
        self.pointListFix = PointList(textTable=gama_coor_table())

        # list of point TO BE ADJUSTED
        # point list of adjusted/constrained points without covariance matrix
        # use for points to be adjusted in input XML document
        self.pointListAdj = PointList(textTable=gama_coor_table())

        # list of ADJUSTED POINTS
        # point list of adjusted/constrained points with covariance matrix
        # use for adjusted points in output XML document
        self.pointListAdjCovMat = PointListCovMat(covmat=CovMatApri(),
                                              textTable=gama_coor_stdev_table())
        # list of OBSERVATIONS
        self.obsClusterList = ObsClusterList()
        

    def parse_file(self, file):
        "parse XML file"
        
        raise NotImplementedError, "method parse_file not implemented"
        
    
    def __str__(self): 
        return "\n".join(["%s: %s" % 
                    (self.slots[i], self.__getattribute__(self.slots[i]))
                    for i in xrange(len(self.slots))])

        

if __name__ == "__main__":

        print "see GamaLocalDataObs.py or GamaLocalDataAdj.py"
