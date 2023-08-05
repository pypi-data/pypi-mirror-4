# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: ObsClusterBase.py 114 2010-12-14 02:30:56Z tomaskubin $


from gizela.util.Error import Error
from gizela.data.ObsBase import ObsBase
from gizela.data.CovMat import CovMat
from gizela.text.TextTable import TextTable
from gizela.data.obs_table import obs_none_table


class ObsClusterBaseError(Error): pass


class ObsClusterBase(object):
    """
    Abstract base class for clusters of observations
    abstract methods:
        make_gama_xml
        make_table_row
    """

    def __init__(self, fromid=None, fromdh=None, covmat=None, textTable=None):
        """
        fromid ... identifier of point 'from'
        fromdh ... instrument height
        covmat ... covariance matrix
        textTable ... TextTable instance
        """
        self.fromid = fromid
        self.fromdh = fromdh
        self._obsList    = [] # list of observations
        self._lastIndex = 0 # index of last observation appended
        self._covmat = covmat
        self._len = 0 # the number of observations
        
        if textTable == None:
            textTable = obs_none_table()
        self._textTable = textTable


    def _get_textTable(self): return self._textTable
    def _set_textTable(self,textTable):
        if isinstance(textTable, TextTable):
            self._textTable = textTable
            for obs in self: obs.textTable = textTable
        else:
            raise ObsClusterBaseError, "TextTable instance expected"

    textTable = property(_get_textTable, _set_textTable)
    

    def _get_cov_mat(self): return self._covmat
    def _set_cov_mat(self, covmat): self._covmat = covmat

    covmat = property(_get_cov_mat, _set_cov_mat)


    def append_obs(self, obs):
        if isinstance(obs, ObsBase):
            obs.cluster = self
            obs.index = self._lastIndex
            self._lastIndex += obs._dim
            obs.textTable = self.textTable
            self._obsList.append(obs)
            self._len += 1
        else:
            raise ObsClusterBaseError, "ObsBase instance expected"

    def __len__(self): return self._len
    
    def __iter__(self): 
        for obs in self._obsList:
            if obs is not None:
                yield obs
    
    def is_cov_mat(self): return self.covmat != None

    def is_cov_mat_dim(self):
        "is covariance matrix with proper dimension present?"
        if self.covmat == None: return False
        return self._lastIndex == self.covmat.dim
    #    dims = [obs.dim for obs in self._obsList]
    #    return sum(dims) == self.covmat.dim

    def make_gama_xml(self, corrected=False): 
        raise NotImplementedError( "Method not implemented." )
        
    def make_gama_xml_covmat(self):
        if self.is_cov_mat():
            if self.is_cov_mat_dim():
                return self.covmat.make_gama_xml()
            else:
                raise ObsClusterBaseError, "Wrong dimension of covariance matrix (measurements %i, dim %i)" % (self._lastIndex, self.covmat.dim)
        else: 
            raise ObsClusterBaseError, "No covariance matrix"

    def compute_corr(self, corr):
        """
        Evokes computation of correction on all observation 
        @param corr: Instance of ObsCorrSphere correction
        @type corr: object ObsCorrSphere
        """
        for obs in self: obs.compute_corr(corr)

    def compute_obs(self, corr):
        """
        Evokes computation of observation value on all observation objects 
        @param corr: Instance of ObsCorrSphere correction
        @type corr: object ObsCorrSphere
        """
        for obs in self: obs.compute_obs(corr)

    # text table
    def set_row_data_function(self, rowDataFun): 
        """set list of functions for making row of data"""
        self.textTable.set_row_data_function(rowDataFun)

    def make_header(self): 
        """returns header of table"""
        return self.textTable.make_table_head()
    
    def make_table_row(self):
        """
        returns row of table
        """
        str = [self.textTable.make_table_row("cluster", self.fromid, None, 
                                       self.fromdh)]
        str.extend([obs.make_table_row() for obs in self])
        return "".join(str)

    def make_footer(self): 
        """returns footer of table"""
        return self.textTable.make_table_foot()

    def __str__(self): 
        return self.make_header() +\
               self.make_table_row()    +\
               self.make_footer()

    #def tran_3d(self, *args, **kwargs): pass

    #def tran_2d(self, *args, **kwargs): pass

    #def call(self, cls, fun, *args, **kwargs):
    #    """
    #    call function fun with specified classes cls
    #    """
    #    for obs in self._obsList:
    #        if isinstance(obs, cls):
    #            obs.fun(*args, **kwargs)

    def iter_obs(self, obsClass):
        """
        returns generator of instances obsClass in cluster
        """

        for obs in self:
            if isinstance(obs, obsClass):
                yield obs


    def iter_obs_from_to(self, obsClass, fromid, toid, fromdh, todh):
        """
        returns generator of obsClass instances with fromid and toid
        """

        for obs in self:
            if isinstance(obs, obsClass):
                if fromdh is None and todh is None:
                    if obs.fromid == fromid and obs.toid == toid:
                        yield obs
                else:
                    if obs.fromid == fromid and obs.toid == toid \
                       and obs.fromdh == fromdh and obs.todh == todh:
                        yield obs


    #def change_id(self, idDict):
    #    """
    #    changes identifier of fromid and/or toid 
    #    """

    #    if self.fromid in idDict:
    #        self.fromid = idDict[self.fromid]

    #    for obs in self._obsList:
    #        obs.change_id(idDict)


    def delete_observation_index(self, index):
        """
        deletes observation with index
        """

        if index > len(self._obsList):
            raise ObsClusterBaseError, "Index out of range"

        self._obsList[index] = None
        self._len -= 1
        #import sys
        #print >>sys.stderr, "cluster length:", self._len

    def delete_observation_class(self, obsClass):
        """
        deletes all observations with class obsClass

        warning: covariance matrix not handed
        """

        for i, obs in enumerate(self._obsList):
            if isinstance(obs, obsClass):
                self.delete_observation_index(i)
                #self._obsList[i]=None

