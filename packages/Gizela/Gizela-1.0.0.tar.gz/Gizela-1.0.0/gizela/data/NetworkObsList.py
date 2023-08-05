# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: NetworkObsList.py 109 2010-12-08 15:38:53Z kubin $

from gizela.util.Error import Error
from gizela.data.NetworkList import NetworkList
from gizela.data.DUPLICATE_ID import DUPLICATE_ID


class NetworkObsListError(Error): pass


class NetworkObsList(NetworkList):
    """
    class for list of NetworkObs instances
    """

    def __init__(self, 
                 coordSystemLocal,
                 prefix=None,
                 suffix=None,
                 #duplicateIdFix=DUPLICATE_ID.compare,
                 duplicateIdAdj=DUPLICATE_ID.overwrite):
        """
        prefix: format string for one number (epoch index) usefull for joined
                adjustment of multiple epoch. As prefix of point id.
        suffix: almost the same as prefix
        duplicateIdFix, duplicateIdAdj: handling of duplicit point
        """

        NetworkList.__init__(self, 
                             coordSystemLocal,
                             #duplicateIdFix=duplicateIdFix,
                             duplicateIdAdj=duplicateIdAdj)
        self.set_prefix(prefix)
        self.set_suffix(suffix)

    def set_prefix(self, prefix):
        if prefix is not None:
            try:
                prefix % 0.0
            except TypeError, e:
                raise NetworkObsListError, \
                        "Prefix '%s' format error: %s" % (prefix, e)
        self.prefix = prefix


    def set_suffix(self, suffix):
        if suffix is not None:
            try:
                suffix % 0.0
            except TypeError, e:
                raise NetworkObsListError, "Suffix format error: %s" % e

        self.suffix = suffix


    def make_new_id(self, epochIndex, oldId):
        """
        returns new id with prefix and/or suffix
        """

        newId = ""
        if self.prefix is not None:
            newId += self.prefix % epochIndex
        newId += oldId
        if self.suffix is not None:
            newId += self.suffix % epochIndex

        return newId


    def change_id(self, holdId=[]):
        """
        changes ids of point with prefix and or suffix

        holdId: ids of point with same id in all epochs
        """

        # change ids with prefix/suffix
        for i in xrange(len(self)):

            for pointList in  (self[i].pointListAdj,\
                               self[i].pointListAdjCovMat):
                for point in pointList:
                    if point.id is not None:
                        if point.id not in holdId:
                            point.id = self.make_new_id(i, point.id)

            for cl in self[i].obsClusterList:
                if cl.fromid is not None:
                    if cl.fromid not in holdId:
                        cl.fromid = self.make_new_id(i, cl.fromid)
                for obs in cl:
                    if not obs.is_from_id_none():
                        if obs.fromid not in holdId:
                            obs.fromid = self.make_new_id(i, obs.fromid)
                    if obs.toid is not None:
                        if obs.toid not in holdId:
                            obs.toid = self.make_new_id(i, obs.toid)



