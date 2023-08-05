# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id$


from gizela.util.Error import Error
from gizela.data.GamaLocalData import GamaLocalData


class EpochError(Error): pass


class Epoch(object):
    """
    epoch object
    contents GamaLocalData instance
    """

    def __init__(self, data, epochList=None):
        """
        data: GamaLocalData instance
        epochList: EpochList instance
        """


        if isinstance(data, GamaLocalData):
            self.pointListAdj = data.pointListAdjCovMat
            self.pointListFix = data.pointListFix
            self.date = data.date
            self.time = data.time
            self.stdev = data.stdev
            self.coordSystemLocal = data.coordSystemLocal 

        else:
            raise EpochError, "Data not supported"


