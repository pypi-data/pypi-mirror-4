# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: ObsHeightDiff.py 82 2010-10-30 22:15:55Z michal $


from gizela.data.ObsBase import ObsBase
from gizela.util.Error   import Error
from gizela.data.obs_table import obs_height_diff_table


class ObsHeightDiffError(Error): pass


class ObsHeightDiff(ObsBase):
    """
    class for levelled height diffrence
    """

    __slots__ = ["dist"]

    def __init__(self, fromid, toid, val, dist=None, stdev=None, textTable=None):
        """height difference:
            fromid    id of stand point
            toid    id of target
            val    measured value in meters
            stdev    standard deviation in milimeters
            dist    distance of leveling section in kilometers
        """
        if dist == None and stdev == None:
                raise ObsHeightDiffError, "no stdev and no dist set"
        if dist != None and stdev != None:
                raise ObsHeightDiffError, "both stdev and dist set"
        
        if textTable == None:
            textTable = obs_height_diff_table()

        super(ObsHeightDiff, self).__init__(tag="dh", fromid=fromid, toid=toid,
                                            val=val, stdev=stdev,
                                            textTable=textTable,
                                            stdevscale=1e3)
    
        self.dist = dist
        self._dim = 1

    def compute_corr(self, corr):
        """
        Computes height difference correction
        @param corr: Instance of ObsCorrSphere correction
        @type corr: object ObsCorrSphere
        """        
#        corr.correct_height_diff(self)
        self.corr = corr.correct_height_diff(self)
        
    def compute_obs(self, corr):
        """
        Computes height difference value
        @param corr: Instance of ObsCorrSphere correction
        @type corr: object ObsCorrSphere
        """
        self.val = corr.compute_height_diff(self)        

    def make_gama_xml(self, corrected=False):
        if corrected:
            val = self.val + self.corr
        else:
            val = self.val

        str = ['<dh from="%s" to="%s" val="%.5f"' % (self.fromid, self.toid, val)]
        
        if self.stdev != None:
            str.append('stdev="%.2f"' % (self.stdev * self._stdevScale))
        
        if self.dist != None:
            str.append('dist="%.3f"' % (self.dist / 1e3))

        str.append("/>")

        return " ".join(str)
    
    def make_table_row(self):
        return self.textTable.make_table_row(self._tag, 
                                             self.fromid, self.toid,
                                             self.val, self.dist,
                                             self.stdev)


if __name__ == "__main__":

    dh1 = ObsHeightDiff("A", "B", 100.01, 550)
    dh2 = ObsHeightDiff("A", "B", 100.01, stdev=0.011)
    
    try:
        dh3 = ObsHeightDiff("A", "B", 100.01)
    except Error, e:
        print "Error"
        print e

    try:
        dh4 = ObsHeightDiff("A", "B", 100.01, 5.5, 1.1)
    except Error, e:
        print "Error"
        print e

    print dh1
    print dh1.make_gama_xml()
    print dh2
    print dh2.make_gama_xml()
