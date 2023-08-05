# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: ObsBase.py 114 2010-12-14 02:30:56Z tomaskubin $


from gizela.text.TextTable import TextTable
from gizela.util.Error import Error


class ObsBaseError(Error): pass


class ObsBase(object):
    """
    Abstract class for geodetic observations
    abstract methods:
        make_gama_xml
        make_table_row
    """
    __slots__ = ["_tag",
                 "cluster", 
                 "_fromid", "_fromdh", 
                 "toid", "todh",
                 "val", "stdev", 
                 "corr",
                 "index", 
                 "_dim",
                 "textTable",
                 "_stdevScale",
                 "_valScale"]

    def __init__(self, tag, toid, val=None, fromid=None, fromdh=None, todh=None,
            stdev=None, index=None, textTable=None, valscale=1.0, stdevscale=1.0):
        """
        tag    ... the name of xml tag
        fromid ... identifier of point "from"
        fromdh ... instrument height
        toid   ... identifier of target point "to"
        todh   ... target height
        val    ... measured value
        stdev  ... standard deviation of measurement
        index  ... covariance matrix row index 
        textTable ... text table instance
        valscale  ... scale factor for val in gama xml
        stdevscale ... scale factor for stdev in gama xml
        """

        self._tag = tag
        self.cluster = None # reference to ObsClusterBase instance
        self.fromid, self.fromdh  = fromid, fromdh 
        self.toid, self.todh = toid, todh 
        self.val, self.stdev = val, stdev
        self.corr    = 0.0 # correction of observation
        self.index = index # index of starting row in covariance matrix
        self._dim = 0 # dimension of measurement
        self.textTable = textTable
        self._valScale = valscale
        self._stdevScale = stdevscale

    def _get_var(self): 
        "returns variance(s) of observation(s)"
        
        if self.stdev != None:
            return self.stdev * self.stdev
        if self.cluster == None or self.index == None or \
           self.cluster.covmat == None:
            return None
        else:
            return self.cluster.covmat.get_var(self.index)

    def _set_var(self, var):
        "sets variance(s) of observation(s)"
        if self.cluster == None or self.cluster.covmat == None or\
           self.index == None:
            from math import sqrt
            self.stdev = sqrt(var)
        else:
            self.stdev = None
            self.cluster.covmat.set_var(self.index, var)

    var = property(_get_var, _set_var)
    
    def _get_dim(self): return self._dim
    
    dim = property(_get_dim) # read only attribute

    def _get_from_id(self):
        if self._fromid != None: return self._fromid
        if self.cluster:
            return self.cluster.fromid
        else:
            return None

    def _set_from_id(self, fromid): self._fromid=fromid
    
    fromid = property(_get_from_id, _set_from_id)

    def is_from_id_none(self):
        return self._fromid is None

    def _get_from_dh(self):
        if self._fromdh != None: return self._fromdh
        if self.cluster:
            return self.cluster.fromdh
        else:
            return None

    def _set_from_dh(self, fromdh): self._fromdh=fromdh

    fromdh = property(_get_from_dh, _set_from_dh)

    def _get_tag(self): return self._tag

    tag = property(_get_tag)
    
    def compute_corr(self, corr): 
        """
        Abstract method overwriten by observation object
        @param corr:
        @type corr:
        """
        raise NotImplementedError("Method not implemented.")
    
    def compute_obs(self, corr):
        """
        Abstract method overwriten by observation object
        @param corr:
        @type corr:
        """
        raise NotImplementedError("Method not implemented.")
        
    def make_gama_xml(self, corrected=False):
        if corrected:
            val = self.val + self.corr
        else:
            val = self.val

        str = ["<%s" % self._tag ]
        
        if self._fromid != None:
            str.append('from="%s"' % self._fromid)
        
        str.append('to="%s"' % self.toid)

        if self.fromdh != None:
            str.append('from_dh="%.4f"' % self.fromdh)
        
        if self.todh != None:
            str.append('to_dh="%.4f"' % self.todh)
        
        str.append('val="%.5f"' % (val * self._valScale))
        
        if self.stdev != None:
            str.append('stdev="%.2f"' % (self.stdev * self._stdevScale))
        

        str.append("/>")

        return " ".join(str)
    
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
        if self.val == None:
            val = None
        else:
            val = self.val * self._valScale
        return self.textTable.make_table_row(self._tag, 
                                             self.fromid, self.toid,
                                             self.fromdh, self.todh,
                                             val, self.stdev)
    
    def make_footer(self): 
        """returns footer of table"""
        return self.textTable.make_table_foot()

    def __str__(self): 
        return self.make_header() +\
               self.make_table_row()    +\
               self.make_footer()

    #def tran_3d(self, *args, **kwargs): pass
    #def tran_2d(self, *args, **kwargs): pass

    def change_id(self, idDict):
        """
        change ids fromid and toid according to dictionary idDict
        """
        if self.fromid in idDict:
            self.fromid = idDict[self.fromid]
        if self.toid in idDict:
            self.toid = idDict[self.toid]

