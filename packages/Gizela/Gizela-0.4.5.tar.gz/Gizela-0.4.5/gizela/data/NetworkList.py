# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$

from gizela.data.Network import Network
from gizela.util.Error import Error
from gizela.util.CoordSystemLocal3D import CoordSystemLocal3D
from gizela.data.GamaLocalData import GamaLocalData
from gizela.data.DUPLICATE_ID import DUPLICATE_ID
from gizela.data.EpochPointList import EpochPointList
from gizela.util.CoordSystemLocal2D import CoordSystemLocal2D
from gizela.util.CoordSystemLocal3D import CoordSystemLocal3D

import datetime


class NetworkListError(Error): pass


class NetworkList(object):
    """
    class for list of GamaLocalData instances
    """

    def __init__(self,
                 coordSystemLocal,
                 stdevUseApriori=True,
                 confProb=0.95,
                 #reliabProb=0.95,
                 #duplicateIdFix=DUPLICATE_ID.compare,
                 duplicateIdAdj=DUPLICATE_ID.overwrite):
        """
        coordSystemLocal: local coordinate system
        stdevUseApriori: use apriori/aposteriori standard deviation
        confProb: confidence probability
        reliabProb: reliability probability
        duplicateFixId: what to do with duplicate fixed points - join
        """
        self.list = []
        if isinstance(coordSystemLocal, CoordSystemLocal2D) or \
           isinstance(coordSystemLocal, CoordSystemLocal3D):
            self.coordSystemLocal = coordSystemLocal
        else:
            raise NetworkListError, "CoordSystemLocal* instance expected"

        self.dateTimeList = [] 
            # list of dates of epochs, datetime instances

        #self.duplicateIdFix = duplicateIdFix
        self.duplicateIdAdj = duplicateIdAdj

        self._confProb = confProb
        #self._reliabProb = reliabProb
        self._stdevUseApriori = stdevUseApriori


    def append(self, data):
        """adds Network instance to list"""

        if not isinstance(data, Network):
            raise NetworkListError, "Network instance expected"
        
        # check local coordinate system
        if self.coordSystemLocal != data.coordSystemLocal:
            import sys
            print >>sys.stderr, self.coordSystemLocal
            print >>sys.stderr, data.coordSystemLocal
            raise NetworkListError,\
                    "Local coordinate systems with different settings"
                
        # add epoch
        self.list.append(data)
        #self.fileNameList.append(data.fileName)

        # add epoch time and date
        self.dateTimeList.extend(data.dateTimeList)

        # set confidence and stdevUse
        data.set_conf_prob(self._confProb)
        data.set_use_apriori(self._stdevUseApriori)

    def __len__(self):
        return len(self.list)

    def __getitem__(self, key):
        return self.list[key]

    def __iter__(self):
        return iter(self.list)

    def join(self):
        """
        joins all observations and points to the
        first object GamaLocalDataObs in self.list
        """

        # join 
        for data in self.list[1:]:
            self[0].extend(data, 
                           #duplicateIdFix=self.duplicateIdFix, 
                           duplicateIdAdj=self.duplicateIdAdj,
                           duplicateIdAdjCovMat=DUPLICATE_ID.hold)

        # set date and time
        #self[0].dateTimeList = self.dateTimeList



