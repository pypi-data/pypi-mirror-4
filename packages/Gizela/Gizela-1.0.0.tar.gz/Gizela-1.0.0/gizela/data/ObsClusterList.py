# gizela 
# 
# Copyright (C) 2010 Michal Seidl, Tomas Kubin 
# Author: Tomas Kubin <tomas.kubin@fsv.cvut.cz> 
# URL: <http://slon.fsv.cvut.cz/gizela> 
# 
# $Id: ObsClusterList.py 114 2010-12-14 02:30:56Z tomaskubin $

from gizela.util.Error import Error
from gizela.data.ObsClusterBase import ObsClusterBase
from gizela.util.Unit import Unit
from gizela.data.ObsDirection import ObsDirection

import sys, math


class ObsClusterListError(Error): pass


class ObsClusterList(object):
    """iterable class for list of clusters
    """

    __slots__ = ["clusterList"]

    def __init__(self):
        self.clusterList = []

    def append_cluster(self, cluster):
        if isinstance(cluster, ObsClusterBase):
            self.clusterList.append(cluster)
        else:
            raise ObsClusterListError, "ObsClusterBase instance expected"

    def make_gama_xml(self, corrected=False):
        return "\n".join([cluster.make_gama_xml(corrected) for cluster in self.clusterList])
    
    def get_last_cluster(self): return self.clusterList[-1]

    def compute_corr(self, corr):
        """
        Evokes computation of correction on all clusters 
        @param corr: Instance of ObsCorrSphere correction
        @type corr: object ObsCorrSphere
        """
        for cluster in self.clusterList: cluster.compute_corr(corr)

    def compute_obs(self, corr):
        """
        Evokes computation of observation on all clusters 
        @param corr: Instance of ObsCorrSphere correction
        @type corr: object ObsCorrSphere
        """
        for cluster in self.clusterList: cluster.compute_obs(corr)

    def __iter__(self):
        return iter(self.clusterList)

    def __str__(self):
        return "\n".join([cluster.__str__() for cluster in self.clusterList])

    def __len__(self):
        return len(self.clusterList)


    def extend(self, other):
        """
        extends with other cluster list
        """
        if not isinstance(other, ObsClusterList):
            raise ObsClusterListError, "ObsClusterList instance expected"

        self.clusterList.extend(other.clusterList)


    def iter_cluster(self, clusterClass):
        """
        returns generator with clusters of clusterClass
        """

        for cluster in self.clusterList:
            if isinstance(cluster, clusterClass):
                yield cluster


    def iter_obs_from_to(self, obsClass, fromid, toid, fromdh=None, todh=None):
        """
        returns generator of obsClass instances with fromid and toid
        """

        for cluster in self.clusterList:
            for obs in cluster.iter_obs_from_to(obsClass=obsClass,
                                                fromid=fromid,
                                                toid=toid,
                                                fromdh=fromdh,
                                                todh=todh):
                yield obs


    def scale_vec_cov_mat(self, scale):

        from gizela.data.ObsClusterVector import ObsClusterVector

        for cl in self.iter_cluster(ObsClusterVector):
            cl.scale_cov_mat(scale)

    def tran_vec_2d(self, coordSystem, pointList):

        from gizela.data.ObsClusterVector import ObsClusterVector
        
        for cl in self.iter_cluster(ObsClusterVector):
            cl.tran_2d(coordSystem, pointList)


    def tran_vec_3d(self, coordSystem):

        from gizela.data.ObsClusterVector import ObsClusterVector
        
        for cl in self.iter_cluster(ObsClusterVector):
            cl.tran_3d(coordSystem)

    def sdist_to_dist(self):

        from gizela.data.ObsCluster import ObsCluster
        
        for cl in self.iter_cluster(ObsCluster):
            cl.sdist_to_dist()

    def dist_scale(self, coordSystem):

        from gizela.data.ObsCluster import ObsCluster
        
        for cl in self.iter_cluster(ObsCluster):
            cl.dist_scale(coordSystem)

    #def change_id(self, idDict):
    #    for cl in self.clusterList:
    #        cl.change_id(idDict)

    def delete_observation_class(self, obsClass):
        """
        deletes observations with specified class obsClass
        """

        from gizela.data.ObsCluster import ObsCluster

        for cluster in self.iter_cluster(ObsCluster):
            cluster.delete_observation_class(obsClass)



    def delete_observation(self, obs):
        """
        deletes observation obs
        """
        obs.cluster.delete_observation_index(index=obs.index)


    def _average_obs(self, obsClass, counter, inCluster):
        """
        compute average of observations
        obsClass: the class of observation
        counter: average counter observations?
        inCluster: make average only in one cluster?
        """

        # collect observations
        obsList = []
        for cl in self:
            for obs in cl.iter_obs(obsClass):
                obsList.append(obs)
            if inCluster:
                self._compute_average(obsList, counter)
                obsList = []

        if not inCluster:
            self._compute_average(obsList, counter)


    def _compute_average(self, obsList, counter):
        "helper function"
        for i, obs0 in enumerate(obsList):
            if obs0 is None:
                continue
            obsVal = [obs0.val]
            obsList[i] = None
            for ii, obs1 in enumerate(obsList):
                if obs1 is None:
                    continue
                if obs1.fromid == obs0.fromid and \
                   obs1.toid == obs0.toid:
                    #print >>sys.stderr, "val", obs1.val, "ii", ii
                    obsVal.append(obs1.val)
                    self.delete_observation(obs1)
                    obsList[ii] = None
                    continue
                if counter:
                    if obs1.fromid == obs0.toid and \
                       obs1.toid == obs0.fromid:
                        #print >>sys.stderr, "val", obs1.val, "ii", ii, "counter"
                        obsVal.append(obs1.val)
                        self.delete_observation(obs1)
                        obsList[ii] = None
            if len(obsVal) > 1:
                # computation of average
                if isinstance(obs0, ObsDirection):
                    obs0.val, stdev = self._average_direction_list(obsVal)
                else:
                    obs0.val = sum(obsVal) / len(obsVal)
                    sumSq = sum([(obs0.val - val)**2 for val in obsVal])
                    stdev = math.sqrt(sumSq/(len(obsVal) - 1))
                if isinstance(obs0, ObsDirection):
                    stdev = stdev * Unit.angleVal
                print >>sys.stderr, obs0.tag, "average: from=%s" % \
                    obs0.fromid, "to=%s" % obs0.toid,\
                    "stdev=%.4f" % stdev, "#", len(obsVal)

    def _average_direction_list(self, valList):
        """
        computes average and standard deviation of directions in list

        average around zero is computed - in the first and third quadrant
        average([pi/2 3*pi/2]) = 0
        average([pi/4 7*pi/4]) = 0
        """
        
        # inretval (pi, 2*pi) transform to (-pi, 0)
        vall = []
        for val in valList:
            if val > math.pi:
                vall.append(val - 2*math.pi)
            else:
                vall.append(val)

        average = sum(vall) / len(vall)
        sumsq = sum([(val - average)**2 for val in vall])
        stdev = math.sqrt(sumsq/(len(vall) - 1))

        return average, stdev


    def average_distance(self, counter=False):
        """
        compute average of repeated distances
        counter=True: average counter distances too
        """

        from gizela.data.ObsDistance import ObsDistance

        self._average_obs(obsClass=ObsDistance,
                          counter=counter,
                          inCluster=False)


    def average_direction(self):
        """
        computes averages for repeated direction
        in one cluster
        """

        from gizela.data.ObsDirection import ObsDirection

        self._average_obs(obsClass=ObsDirection,
                          counter=False, 
                          inCluster=True)

    #def delete_empty_cluster(self):
    #    """
    #    deletes empty clusters
    #    """
    #    self.clusterList = [cl for cl in self.clusterList if len(cl) > 0]




if __name__ == "__main__":

    from gizela.data.ObsDistance  import ObsDistance
    from gizela.data.ObsDirection import ObsDirection
    from gizela.data.ObsZAngle    import ObsZAngle
    from gizela.data.ObsSDistance import ObsSDistance
    from gizela.data.ObsCluster   import ObsCluster 

    from math import pi
    dist  = ObsDistance("AB", 100.01)
    dist2 = ObsDistance("AB", 100.03)
    dist3 = ObsDistance(fromid="AB", toid="CD", val=100.05)
    dir   = ObsDirection("AB", 90.01/200*pi)
    dir2  = ObsDirection("AB", 90.03/200*pi)
    zen   = ObsZAngle("AB", 90.01/200*pi)
    sdist = ObsSDistance("AB", 100.01)

    cl = ObsCluster("CD")
    cl.append_obs(dist)
    #cl.append_obs(dist2)
    #cl.append_obs(dist3)
    cl.append_obs(dir)
    cl.append_obs(dir2)
    cl.append_obs(zen)
    cl.append_obs(sdist)

    cl3 = ObsCluster("AB")
    cl3.append_obs(dist3)

    lst = ObsClusterList()
    lst.append_cluster(cl)
    #import copy
    #cl2 = copy.deepcopy(cl)
    lst.append_cluster(cl3)
    print lst

    # iterator
    print "\n".join(["from=%s" % cl.fromid for cl in lst])

    # average
    print "Average of distance"
    lst.average_distance(counter=True)
    print lst

    print "Average of direction"
    lst.average_direction()
    print lst
    
    #print "Making correction"
    #from gizela.corr.ObsCorrSphere import ObsCorrSphere
    #from gizela.util.Ellipsoid     import Ellipsoid
    #from gizela.data.PointGeodetic import PointGeodetic
    #from gizela.data.PointCart     import PointCart
    #from gizela.data.PointList     import PointList

    #pA = PointCart("AB", x=0, y=0, z=0)
    #pl = PointList(textTable=pA.textTable)
    #pl.add_point(pA)
    #pl.add_point(PointCart("CD", x=1, y=1, z=1))
    #print pl

    #corr = ObsCorrSphere(ellipsoid=Ellipsoid(), 
    #        centralPointGeo=PointGeodetic(id="c", lat=0, lon=0, height=0),\
    #        centralPointLoc=PointCart(id="c", x=0, y=0, z=0), \
    #        pointList=pl)
    #lst.compute_corr(corr)
    #print lst
    #print lst.make_gama_xml(corrected=True)

